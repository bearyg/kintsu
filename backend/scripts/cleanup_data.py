
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

def clean_all_shards():
    """
    Deletes ALL documents in the 'shards' collection.
    Use with caution.
    """
    logger.warning("CLEANING ALL SHARDS")
    docs = db.collection("shards").stream()
    count = 0
    for doc in docs:
        doc.reference.delete()
        count += 1
    logger.info(f"Deleted {count} shards.")

def clean_all_jobs():
    """
    Deletes ALL documents in the 'jobs' collection AND their GCS data.
    """
    logger.warning("CLEANING ALL JOBS")
    docs = db.collection("jobs").stream()
    count = 0
    for doc in docs:
        job = doc.to_dict()
        jid = doc.id
        uid = job.get('userId')
        if uid:
             # Clean Job specific GCS
             delete_gcs_folder(f"uploads/{uid}/{jid}/")
             delete_gcs_folder(f"Hopper/Extracted/{uid}/{jid}/")
        
        doc.reference.delete()
        count += 1
    logger.info(f"Deleted {count} jobs.")

def nuke_gcs_orphans():
    """
    Force deletes known top-level directories in the bucket.
    """
    logger.warning("NUKING ALL GCS DATA (Orphans)")
    # Delete 'uploads/'
    delete_gcs_folder("uploads/")
    # Delete 'Hopper/'
    delete_gcs_folder("Hopper/")
    logger.info("GCS Nuke Complete.")


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
    shards = db.collection("shards").where("userId", "==", user_id).stream()
    shard_count = 0
    for shard in shards:
        shard.reference.delete()
        shard_count += 1
    logger.info(f"Deleted {shard_count} shards for user {user_id}")
    
    # 3. GCS Global User Folders
    delete_gcs_folder(f"uploads/{user_id}/")
    delete_gcs_folder(f"Hopper/Extracted/{user_id}/")
    
    logger.info("User Nuke Complete.")

def clean_build_artifacts():
    """
    Cleans up the Cloud Run source staging bucket.
    """
    build_bucket_name = "run-sources-kintsu-gcp-us-central1"
    try:
        build_bucket = storage_client.bucket(build_bucket_name)
        logger.warning(f"CLEANING BUILD ARTIFACTS in {build_bucket_name}")
        
        # List and delete all blobs in the bucket
        blobs = list(build_bucket.list_blobs())
        count = 0
        if not blobs:
            logger.info("No build artifacts found.")
            return

        # Batch delete might be better for many files, but simple loop is fine for script
        for blob in blobs:
            blob.delete()
            count += 1
            if count % 10 == 0:
                logger.info(f"Deleted {count} build artifacts...")
        
        logger.info(f"Build artifact cleanup complete. Deleted {count} files.")
    except Exception as e:
        logger.error(f"Failed to clean build artifacts: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "nuke":
             if len(sys.argv) < 3:
                 print("Usage: python cleanup_data.py nuke <userId>")
             else:
                 nuke_user_data(sys.argv[2])
        elif sys.argv[1] == "clean-all":
            clean_all_shards()
            clean_all_jobs()
            nuke_gcs_orphans() 
            clean_build_artifacts() # Add build cleanup
            cleanup_stale_jobs(hours=0)
        elif sys.argv[1] == "clean-builds":
            clean_build_artifacts()
    else:
        print("Running Stale Job Cleanup...")
        cleanup_stale_jobs(hours=0.01) 
