from google.cloud import firestore, storage
from datetime import datetime, timedelta
import uuid
import logging

db = firestore.Client()
storage_client = storage.Client()

logger = logging.getLogger(__name__)

class JobService:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.bucket = storage_client.bucket(bucket_name)

    def create_job(self, user_id: str, file_name: str, debug_mode: bool = False) -> dict:
        """
        Creates a new job record and generates a signed URL for file upload.
        """
        job_id = str(uuid.uuid4())
        blob_name = f"uploads/{user_id}/{job_id}/{file_name}"
        
        # Create Job Record
        job_data = {
            "id": job_id,
            "userId": user_id,
            "status": "pending_upload",
            "fileName": file_name,
            "gcsPath": f"gs://{self.bucket_name}/{blob_name}",
            "debugMode": debug_mode,
            "progress": 0,
            "logs": [],
            "createdAt": firestore.SERVER_TIMESTAMP,
            "updatedAt": firestore.SERVER_TIMESTAMP
        }
        
        db.collection("jobs").document(job_id).set(job_data)
        
        # Generate Signed URL (valid for 15 minutes)
        blob = self.bucket.blob(blob_name)
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=15),
            method="PUT",
            content_type="application/octet-stream" 
        )
        
        return {
            "jobId": job_id,
            "uploadUrl": url,
            "gcsPath": job_data["gcsPath"]
        }

    def get_job(self, job_id: str) -> dict:
        doc = db.collection("jobs").document(job_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def update_progress(self, job_id: str, progress: int, status: str = None, log_message: str = None):
        """
        Updates the job progress and optionally status/logs.
        """
        update_data = {
            "progress": progress,
            "updatedAt": firestore.SERVER_TIMESTAMP
        }
        
        if status:
            update_data["status"] = status
            
        if log_message:
            # Atomic array union for logs
            update_data["logs"] = firestore.ArrayUnion([{
                "ts": datetime.utcnow().isoformat(),
                "msg": log_message
            }])
            
        db.collection("jobs").document(job_id).update(update_data)
