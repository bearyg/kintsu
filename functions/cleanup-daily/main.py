import functions_framework
import os
import logging
from datetime import datetime, timedelta, timezone
from google.cloud import storage, firestore

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Clients
storage_client = storage.Client()
db = firestore.Client()
BUCKET_NAME = os.getenv("BUCKET_NAME", "kintsu-hopper-kintsu-gcp")

RETENTION_HOURS = 24

@functions_framework.http
def cleanup(request):
    """
    Daily cleanup of stale data (files and job records > 24h old).
    Triggered by Cloud Scheduler via HTTP (OIDC).
    """
    logger.info("Starting Daily Cleanup...")
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=RETENTION_HOURS)
    logger.info(f"Retention Policy: Delete items older than {cutoff_time.isoformat()}")

    stats = {
        "gcs_deleted": 0,
        "gcs_errors": 0,
        "firestore_deleted": 0,
        "firestore_errors": 0
    }

    # 1. Cleanup GCS
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blobs = bucket.list_blobs()
        
        for blob in blobs:
            # Check prefixes we manage
            if blob.name.startswith("uploads/") or blob.name.startswith("Hopper/"):
                
                # Check creation time
                if blob.time_created < cutoff_time:
                    try:
                        logger.info(f"Deleting stale file: {blob.name} (Created: {blob.time_created})")
                        blob.delete()
                        stats["gcs_deleted"] += 1
                    except Exception as e:
                        logger.error(f"Failed to delete {blob.name}: {e}")
                        stats["gcs_errors"] += 1
                        
    except Exception as e:
        logger.error(f"GCS Cleanup Failed: {e}")
        return {"status": "error", "message": f"GCS Error: {str(e)}"}, 500

    # 2. Cleanup Firestore (Jobs)
    try:
        jobs_ref = db.collection("jobs")
        # Query for jobs updated before cutoff
        # Note: Requires composite index if filtering by multiple fields, but basic inequality is fine here.
        query = jobs_ref.where(filter=firestore.FieldFilter("updatedAt", "<", cutoff_time))
        stale_jobs = query.stream()
        
        for job in stale_jobs:
            try:
                logger.info(f"Deleting stale job: {job.id}")
                job.reference.delete()
                stats["firestore_deleted"] += 1
            except Exception as e:
                logger.error(f"Failed to delete job {job.id}: {e}")
                stats["firestore_errors"] += 1

    except Exception as e:
         logger.error(f"Firestore Cleanup Failed: {e}")
         # We continue to return partial success if GCS worked

    logger.info(f"Cleanup Complete. Stats: {stats}")
    return {"status": "success", "stats": stats}
