import os
import json
import logging
import mailbox
import tempfile
import io
import time
import base64
from fastapi import FastAPI, Request
from google.cloud import storage, firestore
from job_service import JobService
from utils import sanitize_filename
from logger import DriveLogger
from google import genai
from google.genai import types
from google.api_core.exceptions import NotFound

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
storage_client = storage.Client()
db = firestore.Client()

BUCKET_NAME = os.getenv("BUCKET_NAME", "kintsu-hopper-kintsu-gcp")
job_service = JobService(BUCKET_NAME)

class EmailProcessor:
    def __init__(self, bucket, base_path, logger):
        self.bucket = bucket
        self.base_path = base_path.rstrip('/')
        self.logger = logger
        
    def process_message(self, message):
        """Extracts content and saves EML/HTML."""
        msg_id = message.get('Message-ID', '').strip()
        if not msg_id:
            msg_id = f"no_id_{int(time.time()*1000)}"
            
        safe_name = sanitize_filename(msg_id)
        
        # Paths
        eml_path_rel = f"{self.base_path}/{safe_name}.eml"
        html_path_rel = f"{self.base_path}/{safe_name}.html"
        
        # Idempotency
        blob = self.bucket.blob(eml_path_rel)
        if blob.exists():
            self.logger.log_event("skipped", msg_id, "Duplicate file exists")
            return safe_name

        try:
            # 1. Save EML
            blob.upload_from_file(io.BytesIO(message.as_bytes()), content_type='message/rfc822')
            
            # 2. Extract & Save HTML
            html_body = self._get_html_body(message)
            if html_body:
                html_blob = self.bucket.blob(html_path_rel)
                html_blob.upload_from_string(html_body, content_type='text/html')
                
                # 3. Gemini Analysis
                self.extract_inventory(html_body, safe_name)
            
            self.logger.log_event("processed", msg_id, f"Saved to {safe_name}")
            return safe_name
            
        except Exception as e:
            self.logger.log_event("error", msg_id, str(e))
            return None

    def extract_inventory(self, email_body, base_name):
        """Uses Gemini 2.5-Flash to extract inventory data."""
        # Use Vertex AI (Service Account) as requested
        # This requires 'roles/aiplatform.user' on the Service Account (Granted in Step 355)
        try:
            client = genai.Client(vertexai=True, project="kintsu-gcp", location="us-central1")
            
            prompt = """
            Analyze this email and extract inventory items.
            Return ONLY a JSON object:
            {
                "items": [{"name": "", "price": 0, "currency": "USD", "category": ""}],
                "transaction": {"merchant": "", "date": "YYYY-MM-DD", "total": 0}
            }
            """
            
            # Note: gemini-2.5-flash might be 'gemini-1.5-flash' on Vertex. 
            # We attempt 2.5 as strictly requested.
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, email_body],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            if response.text:
                json_path_rel = f"{self.base_path}/{base_name}.json"
                blob = self.bucket.blob(json_path_rel)
                blob.upload_from_string(response.text, content_type='application/json')
                self.logger.log_event("extracted", base_name, "Inventory JSON saved")

        except Exception as e:
            self.logger.log_event("error", base_name, f"Gemini Extraction Failed: {e}")

    def _get_html_body(self, message):
        body = ""
        if message.is_multipart():
            for part in message.walk():
                ctype = part.get_content_type()
                if ctype == 'text/html' and 'attachment' not in str(part.get('Content-Disposition')):
                    try:
                        return part.get_payload(decode=True).decode('utf-8', errors='replace')
                    except: pass
        else:
             try:
                 return message.get_payload(decode=True).decode('utf-8', errors='replace')
             except: pass
        return body

def safe_update_progress(job_id, progress, status, message, stage=None):
    if not job_id or job_id == "unknown": return
    try:
        job_service.update_progress(job_id, progress, status, message, stage=stage)
    except NotFound:
        logger.warning(f"Job {job_id} not found. Ignoring.")
    except Exception as e:
        logger.error(f"Failed to update progress: {e}")

@app.post("/")
async def handle_pubsub_event(request: Request):
    """
    Handles Pub/Sub Push Notification.
    Format: {"message": {"data": "base64...", "attributes": {...}}, "subscription": "..."}
    """
    try:
        envelope = await request.json()
    except Exception:
        logger.error("Failed to parse JSON body")
        return {"status": "error", "reason": "invalid_json"}

    if not envelope.get("message"):
        logger.error("No message field in request")
        return {"status": "ignored"}

    pubsub_message = envelope["message"]
    
    # Check attributes for routing (optional extra safety)
    attributes = pubsub_message.get("attributes", {})
    event_type = attributes.get("event_type")
    
    if event_type and event_type != "mbox":
        logger.info(f"Ignoring event type: {event_type}")
        return {"status": "ignored"}

    # Decode Data
    try:
        data_str = base64.b64decode(pubsub_message["data"]).decode("utf-8")
        event_data = json.loads(data_str)
    except Exception as e:
        logger.error(f"Failed to decode message data: {e}")
        return {"status": "error"}

    bucket = event_data.get("bucket")
    name = event_data.get("name")
    job_id = event_data.get("job_id", "unknown")
    user_id = event_data.get("user_id", "unknown")

    if not bucket or not name:
        logger.error("Missing bucket/name in payload")
        return {"status": "error"}

    logger.info(f"Processing MBOX Job {job_id} for User {user_id} (File: {name})")

    # Fetch Job & Auth
    auth_token = None
    if job_id != "unknown":
        job_snap = db.collection("jobs").document(job_id).get()
        if job_snap.exists:
            auth_token = job_snap.get("authToken")
    
    safe_update_progress(job_id, 10, "processing", "Worker received job. Downloading...", stage="init")

    # Initialize Drive Uploader
    drive_uploader = None
    target_folder_id = None
    if auth_token:
        try:
            from drive_uploader import DriveUploader
            drive_uploader = DriveUploader(auth_token)
            target_folder_id = drive_uploader.ensure_path(['Kintsu', 'Hopper', 'Gmail'])
        except Exception as e:
            logger.error(f"Drive Init Failed: {e}")

    temp_file = None
    try:
        blob = storage_client.bucket(bucket).blob(name)
        _, temp_file = tempfile.mkstemp()
        blob.download_to_filename(temp_file)
        
        safe_update_progress(job_id, 20, "processing", "Parsing Mbox...", stage="extracting")
        
        # Setup paths
        mbox_name = os.path.basename(name).replace('.mbox', '')
        # Output to GCS first: Hopper/gmail/extract_{mbox_name}
        extract_path = f"Hopper/gmail/extract_{mbox_name}"
        bucket_obj = storage_client.bucket(bucket)
        
        proc_logger = DriveLogger(bucket_obj, f"{extract_path}/processing_log.json")
        processor = EmailProcessor(bucket_obj, extract_path, proc_logger)
        
        mbox = mailbox.mbox(temp_file)
        total = len(mbox)
        logger.info(f"Messages to process: {total}")
        
        count = 0
        for msg in mbox:
            count += 1
            if count % 50 == 0:
                safe_update_progress(job_id, 30, "processing", f"Analyzed {count}/{total}...", stage="analyzing")
                proc_logger.save() # periodic save

            res_name = processor.process_message(msg)
            
            # Upload to Drive
            if res_name and drive_uploader and target_folder_id:
                try:
                    for ext, mime in [('.eml', 'message/rfc822'), ('.html', 'text/html'), ('.json', 'application/json')]:
                        gcs_b = bucket_obj.blob(f"{extract_path}/{res_name}{ext}")
                        if gcs_b.exists():
                            content = gcs_b.download_as_text() if ext != '.eml' else gcs_b.download_as_string()
                            drive_uploader.upload_file(f"{res_name}{ext}", content, mime, target_folder_id)
                            gcs_b.delete() 
                except Exception as e:
                    logger.error(f"Drive upload failed for {res_name}: {e}")

        # Finalize
        proc_logger.save()
        if drive_uploader and target_folder_id:
            try:
                log_b = bucket_obj.blob(f"{extract_path}/processing_log.json")
                if log_b.exists():
                    drive_uploader.upload_file("processing_log.json", log_b.download_as_text(), "application/json", target_folder_id)
            except: pass

        safe_update_progress(job_id, 100, "completed", "Processing Complete", stage="done")
        
        # Cleanup Source Mbox
        try:
            blob.delete()
            logger.info(f"Deleted source mbox: {name}")
        except: pass
        
        # Cleanup Job
        if job_id != "unknown":
            try:
                db.collection("jobs").document(job_id).delete()
            except: pass

    except Exception as e:
        logger.error(f"Fatal Error: {e}", exc_info=True)
        safe_update_progress(job_id, 0, "failed", str(e))
    finally:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)

    return {"status": "ok"}
