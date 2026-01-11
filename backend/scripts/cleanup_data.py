
import firebase_admin
from firebase_admin import credentials, firestore, storage
from datetime import datetime, timedelta
import logging

# Initialize Firebase (assuming implicit credentials or existing env)
if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()
bucket_name = "kintsu-hopper-kintsu-gcp"
# bucket = storage.bucket(bucket_name) # Admin SDK storage is different, use google-cloud-storage directly for easier GCS ops if needed, but admin sdk also wraps it.
# Usually cleaner to use google-cloud-storage for explicit bucket ops
from google.cloud import storage as gcs
storage_client = gcs.Client()
bucket = storage_client.bucket(bucket_name)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cleanup")

def delete_gcs_folder(folder_path):
    """Recursively deletes a folder in GCS"""
    blobs = list(bucket.list_blobs(prefix=folder_path))
    if not blobs:
        return
    
    for blob in blobs:
        blob.delete()
    logger.info(f"Deleted GCS path: {folder_path} ({len(blobs)} files)")

def cleanup_stale_jobs(hours=1):
    """Cleans up jobs that have been stuck for > 1 hour"""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    # Query stuck jobs
    # Note: Complex queries might need index. Simple scan for now or composite index.
    # Jobs don't have 'status' indexed by default maybe?
    # Scanning all recent jobs is safer if volume is low.
    
    docs = db.collection("jobs").where("createdAt", "<", cutoff).stream()
    
    count = 0
    for doc in docs:
        data = doc.to_dict()
        status = data.get("status")
        
        # Define 'stuck' statuses
        if status in ["pending_upload", "processing", "error"]:
            job_id = doc.id
            user_id = data.get("userId")
            
            logger.info(f"Cleaning up stale job {job_id} ({status}) from user {user_id}")
            
            # 1. Delete GCS Uploads
            if user_id:
                delete_gcs_folder(f"uploads/{user_id}/{job_id}/")
                delete_gcs_folder(f"Hopper/Extracted/{user_id}/{job_id}/")
                delete_gcs_folder(f"Hopper/gmail/extract_{job_id}/") # Heuristic for mbox extracts if name matching
            
            # 2. Delete Firestore Job
            db.collection("jobs").document(job_id).delete()
            count += 1
            
    logger.info(f"Cleanup complete. Removed {count} stale jobs.")

def nuke_user_data(user_id):
    """
    Destructive: Removes ALL data for a user.
    """
    logger.warning(f"NUKING DATA FOR USER: {user_id}")
    
    # 1. Jobs
    jobs = db.collection("jobs").where("userId", "==", user_id).stream()
    for job in jobs:
        logger.info(f"Deleting job {job.id}")
        # Clean GCS for this job
        delete_gcs_folder(f"uploads/{user_id}/{job.id}/")
        job.reference.delete()
        
    # 2. Shards
    # Shards don't always have userId indexed or stored top-level? 
    # Checking Shard definition: id, fileName, sourceType, status... no userId?
    # Shards currently seem global/mixed. If userId is missing, we can't safely delete shards.
    # Checking App.tsx: shards are queries by collection(db, "shards").
    # If shards are shared, we can't nuke them by user. skipping.
    
    # 3. GCS Global User Folders
    delete_gcs_folder(f"uploads/{user_id}/")
    delete_gcs_folder(f"Hopper/Extracted/{user_id}/")
    
    logger.info("User Nuke Complete.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "nuke":
         if len(sys.argv) < 3:
             print("Usage: python cleanup_data.py nuke <userId>")
         else:
             nuke_user_data(sys.argv[2])
    else:
        print("Running Stale Job Cleanup...")
        cleanup_stale_jobs(hours=0.01) # Aggressive: 36 seconds old 
