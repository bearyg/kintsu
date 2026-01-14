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
from routes import reporting

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', force=True)
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(reporting.router)


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
    authToken: Optional[str] = None
    folderId: Optional[str] = None
    debugMode: bool = False

# ... (omitting health check and other unrelated code blocks for brevity if not changing)

@app.post("/api/jobs/create")
async def create_job(req: JobRequest):
    """
    Creates a new async job and returns a signed URL for uploading the file.
    """
    try:
        result = job_service.create_job(
            req.userId, 
            req.fileName, 
            req.authToken, 
            req.folderId, 
            req.debugMode
        )
        logger.info(f"Created Job {result['jobId']} for user {req.userId}")
        return result
    except Exception as e:
        logger.error(f"Failed to create job: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))