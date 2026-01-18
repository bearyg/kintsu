import functions_framework
from google.cloud import storage, pubsub_v1
import os
import json
import zipfile
import io
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
storage_client = storage.Client()
publisher = pubsub_v1.PublisherClient()

# Configuration
PROJECT_ID = os.getenv("GCP_PROJECT", "kintsu-gcp")
TOPIC_ID = "kintsu-processing-workload"
TOPIC_PATH = publisher.topic_path(PROJECT_ID, TOPIC_ID)

def publish_event(file_data, type_hint):
    """
    Publishes a notification to the processing workload topic.
    """
    try:
        # Construct the message payload
        # we pass the file details so the worker can download it
        message_json = json.dumps(file_data)
        message_bytes = message_json.encode("utf-8")
        
        # Publish with attributes for filtering
        future = publisher.publish(
            TOPIC_PATH, 
            message_bytes, 
            event_type=type_hint, # filtering attribute
            source_bucket=file_data.get('bucket'),
            file_name=file_data.get('name')
        )
        message_id = future.result()
        logger.info(f"Published message {message_id} to {TOPIC_PATH} (type={type_hint})")
    except Exception as e:
        logger.error(f"Failed to publish event: {e}")

def handle_zip_archive(bucket, blob):
    """
    Downloads, unzips, and re-uploads files to GCS.
    Does NOT publish events - relies on the new file creation to trigger this function again for the unzipped content.
    """
    zip_name = os.path.basename(blob.name).replace('.zip', '')
    
    # Extract Context (User/Job) from path if available
    # Path: uploads/{userId}/{jobId}/{filename}
    parts = blob.name.split('/')
    base_path = f"Hopper/Extracted/{zip_name}"
    
    if len(parts) >= 4 and parts[0] == 'uploads':
        user_id = parts[1]
        job_id = parts[2]
        base_path = f"Hopper/Extracted/{user_id}/{job_id}"
        logger.info(f"Detected Context - User: {user_id}, Job: {job_id}")

    logger.info(f"Unzipping {blob.name} to {base_path}/...")

    try:
        zip_bytes = blob.download_as_bytes()
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            for filename in z.namelist():
                if filename.endswith('/'): continue # Skip directories
                
                # Check for hidden files (__MACOSX, .ds_store)
                if '__MACOSX' in filename or filename.startswith('.'):
                    continue

                file_data = z.read(filename)
                
                # Construct new path: {base_path}/{filename}
                new_blob_name = f"{base_path}/{filename}"
                
                new_blob = bucket.blob(new_blob_name)
                # Check if file exists to avoid unnecessary writes? 
                # No, overwrite is safer for retries to ensure we trigger the event.
                new_blob.upload_from_string(file_data)
                logger.info(f"-> Extracted: {new_blob_name}")
                
    except Exception as e:
        logger.error(f"Error processing zip {blob.name}: {e}")
        return # Do not delete zip if failed
    
    # Only delete source zip if successful
    logger.info(f"Extraction complete. Deleting source zip: {blob.name}")
    try:
        blob.delete()
    except Exception as e:
        logger.warning(f"Failed to delete source zip {blob.name}: {e}")

@functions_framework.cloud_event
def process_new_shard(cloud_event):
    """
    Triggered by a change to a Cloud Storage bucket.
    Acts as a Dispatcher: Unzips archives OR Publishes events for processable files.
    """
    data = cloud_event.data
    bucket_name = data["bucket"]
    file_name = data["name"]
    
    # Ignore folder creation events
    if file_name.endswith('/'):
        return

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.get_blob(file_name)

    if not blob: 
        logger.warning(f"Blob {file_name} not found (deleted?).")
        return

    logger.info(f"Inspecting: {file_name} ({blob.content_type})")

    # 1. ZIP Handling (Unzip Strategy)
    if file_name.lower().endswith('.zip'):
        handle_zip_archive(bucket, blob)
        return

    # 2. Extract Context
    user_id = "unknown"
    job_id = "unknown"
    
    parts = file_name.split('/')
    # Attempt to parse context from standard paths
    # Hopper/Extracted/{userId}/{jobId}/...
    if len(parts) >= 4 and parts[0] == 'Hopper' and parts[1] == 'Extracted':
        user_id = parts[2]
        job_id = parts[3]
    # uploads/{userId}/{jobId}/... (Direct upload of mbox?)
    elif len(parts) >= 4 and parts[0] == 'uploads':
        user_id = parts[1]
        job_id = parts[2]

    file_payload = {
        "bucket": bucket_name,
        "name": file_name,
        "user_id": user_id,
        "job_id": job_id,
        "size": blob.size,
        "content_type": blob.content_type,
        "time_created": blob.time_created.isoformat() if blob.time_created else None
    }

    # 3. Dispatch Logic
    if file_name.lower().endswith('.mbox'):
        logger.info(f"Dispatching MBOX event for {file_name}")
        publish_event(file_payload, "mbox")
        
    elif "amazon" in file_name.lower() and file_name.lower().endswith('.csv'):
        logger.info(f"Dispatching Amazon event for {file_name}")
        publish_event(file_payload, "amazon_history")
        
    else:
        logger.info(f"Ignoring file {file_name} - no matching handler.")
