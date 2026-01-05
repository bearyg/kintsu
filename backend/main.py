import os
import requests
import json
import tempfile
import zipfile
import shutil
import re
import pandas as pd
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from storage import LocalStorageAdapter, GCSAdapter 
import google.generativeai as genai
from google.cloud import firestore
from processors.amazon import AmazonProcessor

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
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "kintsu-hopper-kintsu-gcp")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

db = firestore.Client()

class RefineRequest(BaseModel):
    file_id: str
    fileName: str
    access_token: str
    source_type: str
    debug_mode: bool = False

def log(message: str, debug: bool = False, is_error: bool = False):
    if is_error:
        print(f"[ERROR] {message}")
    elif debug:
        print(f"[DEBUG] {message}")
    else:
        print(f"[INFO] {message}")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "gemini_ready": bool(GEMINI_API_KEY)}

async def save_shard(shard_data: dict, shard_id: str):
    db.collection("shards").document(shard_id).set(shard_data)
    log(f"Saved shard: {shard_id}")

async def process_single_file(file_path: str, mime_type: str, original_filename: str, source_type: str, debug_mode: bool, parent_zip: str = None):
    """
    Fallback: Uploads a single file to Gemini and saves the shard.
    """
    try:
        log(f"Processing single file (Generic): {original_filename} ({mime_type})", debug=debug_mode)
        
        # Upload to Gemini
        gemini_file = genai.upload_file(path=file_path, mime_type=mime_type)
        model = genai.GenerativeModel('gemini-2.5-pro')
        
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
        
        gen_resp = model.generate_content([prompt, gemini_file])
        text = gen_resp.text
        
        extracted_data = {}
        try:
            clean_text = text.replace('```json', '').replace('```', '').strip()
            match = re.search(r'\{.*\}', clean_text, re.DOTALL)
            if match: clean_text = match.group(0)
            extracted_data = json.loads(clean_text)
        except json.JSONDecodeError:
            log(f"JSON Parse Error for {original_filename}.", is_error=True)
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
        log(f"Error processing {original_filename}: {e}", is_error=True)

async def process_drive_file_background(req: RefineRequest):
    log(f"Starting background process for: {req.fileName}", debug=req.debug_mode)
    work_dir = tempfile.mkdtemp()
    
    try:
        # Download
        headers = {"Authorization": f"Bearer {req.access_token}"}
        drive_url = f"https://www.googleapis.com/drive/v3/files/{req.file_id}?alt=media"
        response = requests.get(drive_url, headers=headers, stream=True)
        if response.status_code != 200:
            log(f"Download failed: {response.text}", is_error=True)
            return

        local_filename = os.path.join(work_dir, req.fileName)
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # File List to Process
        files_to_process = [] # Tuples: (path, filename)

        if req.fileName.lower().endswith('.zip'):
            log("Unzipping archive...", debug=req.debug_mode)
            extract_dir = os.path.join(work_dir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)
            with zipfile.ZipFile(local_filename, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file.startswith('.') or '__MACOSX' in root: continue
                    files_to_process.append((os.path.join(root, file), file))
        else:
            files_to_process.append((local_filename, req.fileName))

        # Processing Loop
        amazon_processor = AmazonProcessor()
        sibling_files = [f[0] for f in files_to_process]

        for file_path, file_name in files_to_process:
            # 1. Try Specialized Processors
            if amazon_processor.can_process(file_path, req.source_type):
                log(f"Routing {file_name} to AmazonProcessor", debug=req.debug_mode)
                shards = amazon_processor.process(file_path, file_name, sibling_files=sibling_files)
                for i, shard_data in enumerate(shards):
                    shard_id = f"amazon_{req.file_id}_{i}"
                    final_shard = {
                        "id": shard_id,
                        "fileName": f"{file_name} (Item {i+1})",
                        "sourceType": "Amazon",
                        "parentZip": req.fileName,
                        "status": "refined",
                        "extractedData": shard_data,
                        "createdAt": firestore.SERVER_TIMESTAMP
                    }
                    await save_shard(final_shard, shard_id)
                continue

            # 2. Fallback to Generic Gemini
            ext = file_name.split('.')[-1].lower()
            mime_type = 'application/octet-stream'
            if ext in ['csv', 'txt']: mime_type = 'text/csv'
            elif ext == 'pdf': mime_type = 'application/pdf'
            elif ext in ['jpg', 'jpeg', 'png']: mime_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"
            
            # Skip unsupported in generic
            if mime_type == 'application/octet-stream': continue

            await process_single_file(file_path, mime_type, file_name, req.source_type, req.debug_mode, parent_zip=req.fileName)

    except Exception as e:
        log(f"Background Job Error: {e}", is_error=True)
    finally:
        shutil.rmtree(work_dir)
        log("Cleanup complete.", debug=req.debug_mode)

@app.post("/api/refine-drive-file")
async def refine_drive_file(req: RefineRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_drive_file_background, req)
    return {"status": "queued", "message": f"Processing {req.fileName} in background"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))