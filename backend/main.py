import os
import requests
import json
import logging
import re
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from google import genai
from google.cloud import firestore
from job_service import JobService

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', force=True)
logger = logging.getLogger(__name__)

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AMAZON_PROCESSOR_URL = os.getenv("AMAZON_PROCESSOR_URL")
GMAIL_INGEST_URL = os.getenv("GMAIL_INGEST_URL")
BUCKET_NAME = os.getenv("BUCKET_NAME", "kintsu-hopper-kintsu-gcp") # Default bucket

client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Gemini Client: {e}")

db = firestore.Client()
job_service = JobService(BUCKET_NAME)

class RefineRequest(BaseModel):
    file_id: str
    fileName: str
    access_token: str
    source_type: str
    debug_mode: bool = False

class JobRequest(BaseModel):
    userId: str
    fileName: str
    debugMode: bool = False

@app.get("/api/health")
def health_check():
    return {
        "status": "ok", 
        "gemini_ready": bool(GEMINI_API_KEY),
        "amazon_processor_configured": bool(AMAZON_PROCESSOR_URL),
        "gmail_ingest_configured": bool(GMAIL_INGEST_URL)
    }

async def save_shard(shard_data: dict, shard_id: str):
    db.collection("shards").document(shard_id).set(shard_data)
    logger.info(f"Saved shard: {shard_id}")

async def process_single_file_generic(file_path: str, mime_type: str, original_filename: str, source_type: str, debug_mode: bool, parent_zip: str = None):
    """
    Fallback: Uploads a single file to Gemini and saves the shard.
    Kept in backend for now as a catch-all.
    """
    try:
        if debug_mode: logger.info(f"Processing single file (Generic): {original_filename} ({mime_type})")
        
        if not client:
             logger.error("Gemini Client not configured.")
             return

        # Upload to Gemini
        gemini_file = client.files.upload(file=file_path, config={'mime_type': mime_type})
        
        prompt = """
        Analyze this document for an insurance claim. 
        Extract ONLY JSON:
        {
            "item_name": "Name",
            "merchant": "Store",
            "date": "YYYY-MM-DD",
            "total_amount": number,
            "currency": "USD",
            "category": "Type",
            "confidence": "High/Med/Low"
        }
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=[prompt, gemini_file]
        )
        text = response.text
        
        extracted_data = {}
        try:
            clean_text = text.replace('```json', '').replace('```', '').strip()
            match = re.search(r'\{.*\}', clean_text, re.DOTALL)
            if match: clean_text = match.group(0)
            extracted_data = json.loads(clean_text)
        except json.JSONDecodeError:
            logger.error(f"JSON Parse Error for {original_filename}.")
            extracted_data = {"item_name": "Unstructured Extraction", "raw_analysis": text, "confidence": "Low"}
        
        shard_id = f"drive_{os.path.basename(file_path)}_{source_type}"
        shard_data = {
            "id": shard_id,
            "fileName": original_filename,
            "sourceType": source_type,
            "parentZip": parent_zip,
            "status": "refined",
            "extractedData": extracted_data,
            "createdAt": firestore.SERVER_TIMESTAMP
        }
        await save_shard(shard_data, shard_id)
        
    except Exception as e:
        logger.error(f"Error processing {original_filename}: {e}", exc_info=True)

async def dispatch_amazon_processing(req: RefineRequest):
    if not AMAZON_PROCESSOR_URL:
        logger.error("Amazon Processor URL not configured.")
        return

    try:
        logger.info(f"Dispatching to Amazon Processor: {req.fileName}")
        
        payload = {
            "file_id": req.file_id,
            "fileName": req.fileName,
            "access_token": req.access_token,
            "source_type": req.source_type,
            "debug_mode": req.debug_mode
        }
        
        resp = requests.post(AMAZON_PROCESSOR_URL, json=payload, timeout=300)
        if resp.status_code == 200:
            logger.info(f"Amazon Processor Success: {resp.json()}")
        else:
            logger.error(f"Amazon Processor Failed ({resp.status_code}): {resp.text}")

    except Exception as e:
        logger.error(f"Failed to dispatch Amazon job: {e}", exc_info=True)

@app.post("/api/refine-drive-file")
async def refine_drive_file(req: RefineRequest, background_tasks: BackgroundTasks, debug: Optional[str] = None):
    # Override debug_mode if query param is present
    if debug and debug.lower() in ['on', 'true', '1']:
        req.debug_mode = True
        
    # Routing Logic
    if req.source_type == 'Amazon' or 'Retail.OrderHistory' in req.fileName:
        background_tasks.add_task(dispatch_amazon_processing, req)
        return {"status": "queued", "message": f"Dispatched {req.fileName} to Amazon Processor"}
    
    return {"status": "skipped", "message": "Generic processing temporarily disabled during refactor."}

@app.post("/api/jobs/create")
async def create_job(req: JobRequest):
    """
    Creates a new async job and returns a signed URL for uploading the file.
    """
    try:
        result = job_service.create_job(req.userId, req.fileName, req.debugMode)
        logger.info(f"Created Job {result['jobId']} for user {req.userId}")
        return result
    except Exception as e:
        logger.error(f"Failed to create job: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))