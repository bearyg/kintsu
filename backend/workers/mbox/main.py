import os
import json
import logging
import mailbox
import tempfile
from fastapi import FastAPI, Request
from google.cloud import storage, firestore
from job_service import JobService  # Shared logic
# Import other shared modules if needed (e.g. storage adapter)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
storage_client = storage.Client()
db = firestore.Client()

BUCKET_NAME = os.getenv("BUCKET_NAME", "kintsu-hopper-kintsu-gcp")
job_service = JobService(BUCKET_NAME)

def extract_body(message):
    body = ""
    if message.is_multipart():
        for part in message.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))
            if ctype == 'text/html' and 'attachment' not in cdispo:
                try:
                    body = part.get_payload(decode=True).decode('utf-8')
                    return body
                except:
                    pass
    else:
        try:
             body = message.get_payload(decode=True).decode('utf-8')
        except:
            pass
    return body

@app.post("/")
async def handle_event(request: Request):
    """
    Handles Cloud Storage Object Finalized event via Eventarc.
    """
    event = await request.json()
    logger.info(f"Received event: {event}")

    # Eventarc envelope for GCS
    # Structure varies slightly by trigger type, assuming standard CloudEvent or AuditLog
    # For Audit Log: protoPayload.resourceName
    # For Direct notification: bucket, name
    
    # We'll assume direct notification or parsing common fields
    bucket = event.get('bucket')
    name = event.get('name')
    
    if not bucket or not name:
        # Check if it's a CloudEvent format
        if 'message' in event and 'data' in event['message']:
             # Pub/Sub format
             import base64
             data = json.loads(base64.b64decode(event['message']['data']).decode('utf-8'))
             bucket = data.get('bucket')
             name = data.get('name')

    if not bucket or not name:
        logger.error("Could not parse GCS event")
        return {"status": "ignored"}

    # Verify it's a job upload
    if not name.startswith("uploads/"):
        logger.info(f"Ignoring non-upload file: {name}")
        return {"status": "ignored"}

    # Extract Job ID from path: uploads/{userId}/{jobId}/{filename}
    parts = name.split('/')
    if len(parts) < 4:
        logger.error(f"Invalid upload path: {name}")
        return {"status": "error"}
    
    job_id = parts[2]
    user_id = parts[1]
    
    logger.info(f"Processing Job {job_id} for User {user_id}")
    job_service.update_progress(job_id, 10, "processing", "Worker started. Downloading file...")

    temp_file = None
    try:
        # Download file
        blob = storage_client.bucket(bucket).blob(name)
        _, temp_file = tempfile.mkstemp()
        blob.download_to_filename(temp_file)
        
        job_service.update_progress(job_id, 20, "processing", "File downloaded. Parsing Mbox...")
        
        # Parse Mbox
        mbox = mailbox.mbox(temp_file)
        total_messages = len(mbox) # This can be slow for huge files, maybe skip or estimate
        logger.info(f"Mbox contains {total_messages} messages")
        
        processed = 0
        extracted_count = 0
        
        for message in mbox:
            processed += 1
            if processed % 100 == 0:
                progress = 20 + int((processed / total_messages) * 60)
                job_service.update_progress(job_id, progress, "processing", f"Scanned {processed} emails...")

            subject = message.get('subject', '')
            
            # Simple Heuristic Filter
            if any(keyword in subject.lower() for keyword in ['receipt', 'order', 'invoice', 'confirmation']):
                body = extract_body(message)
                if body:
                    extracted_count += 1
                    
                    # Create Artifact
                    safe_subject = "".join(x for x in subject if x.isalnum() or x in "._- ")[:50]
                    artifact_name = f"Hopper/Gmail/{job_id}_{processed}_{safe_subject}.html"
                    
                    # Upload to GCS (Triggers ingest-shard)
                    artifact_blob = storage_client.bucket(bucket).blob(artifact_name)
                    artifact_blob.upload_from_string(body, content_type='text/html')
                    
                    logger.info(f"Uploaded artifact: {artifact_name}")
        
        job_service.update_progress(job_id, 90, "processing", f"Extraction complete. Found {extracted_count} candidates. Cleaning up...")
        
        # Cleanup GCS File (Zero Retention)
        blob.delete()
        job_service.update_progress(job_id, 100, "completed", "Job complete. Source file deleted.")

    except Exception as e:
        logger.error(f"Job failed: {e}", exc_info=True)
        job_service.update_progress(job_id, 0, "failed", f"Error: {str(e)}")
        
    finally:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)

    return {"status": "ok"}
