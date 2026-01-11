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

    def create_job(self, user_id: str, file_name: str, auth_token: str = None, folder_id: str = None, debug_mode: bool = False) -> dict:
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
            "authToken": auth_token,  # Store for worker to use
            "folderId": folder_id,    # Target Drive Folder
            "progress": 0,
            "logs": [],
            "createdAt": firestore.SERVER_TIMESTAMP,
            "updatedAt": firestore.SERVER_TIMESTAMP
        }
        
        db.collection("jobs").document(job_id).set(job_data)
        
        # Generate Signed URL (valid for 15 minutes)
        # Use Impersonated Credentials to sign via IAM API (fixes "no private key" on Cloud Run)
        import google.auth
        from google.auth import impersonated_credentials
        from google.auth.transport.requests import Request

        source_credentials, project = google.auth.default()
        target_principal = "351476623210-compute@developer.gserviceaccount.com"
        
        # Create impersonated credentials (self-impersonation to get signing capability)
        creds = impersonated_credentials.Credentials(
            source_credentials=source_credentials,
            target_principal=target_principal,
            target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
            lifetime=3600
        )
        
        # Refresh to ensure token is valid
        creds.refresh(Request())

        blob = self.bucket.blob(blob_name)
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=15),
            method="PUT",
            content_type="application/octet-stream",
            credentials=creds
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
