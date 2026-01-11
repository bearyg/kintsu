import os
import json
import logging
import mailbox
import tempfile
import io
import time
from fastapi import FastAPI, Request
from google.cloud import storage, firestore
from job_service import JobService  # Shared logic
from utils import sanitize_filename
from logger import DriveLogger
from google import genai
from google.genai import types

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
        """
        Extracts content from a message and saves EML/HTML files.
        Returns: base_name (str) if processed, None if skipped/error.
        """
        msg_id = message.get('Message-ID', '').strip()
        if not msg_id:
            # Fallback for missing ID
            msg_id = f"no_id_{int(time.time()*1000)}"
            
        safe_name = sanitize_filename(msg_id)
        
        # Paths
        eml_path_rel = f"{self.base_path}/{safe_name}.eml"
        html_path_rel = f"{self.base_path}/{safe_name}.html"
        
        # Idempotency Check (Check if EML exists)
        blob = self.bucket.blob(eml_path_rel)
        if blob.exists():
            self.logger.log_event("skipped", msg_id, "Duplicate file exists")
            return None

        try:
            # 1. Save EML (Binary)
            blob.upload_from_file(io.BytesIO(message.as_bytes()), content_type='message/rfc822')
            
            # 2. Extract & Save HTML
            html_body = self._get_html_body(message)
            if html_body:
                html_blob = self.bucket.blob(html_path_rel)
                html_blob.upload_from_string(html_body, content_type='text/html')
                
                # 3. Gemini Extraction (Async-ish)
                self.extract_inventory(html_body, safe_name)
            
            self.logger.log_event("processed", msg_id, f"Saved to {safe_name}")
            return safe_name
            
        except Exception as e:
            self.logger.log_event("error", msg_id, str(e))
            return None

    def extract_inventory(self, email_body, base_name):
        """
        Uses Gemini to extract inventory data from the email body.
        Saves result to <base_name>.json.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.logger.log_event("warning", base_name, "GEMINI_API_KEY not set")
            return

        try:
            client = genai.Client(api_key=api_key)
            
            prompt = """
            Analyze this email and extract inventory items purchased or described.
            Return ONLY a JSON object with this schema:
            {
                "items": [
                    {
                        "name": "Item Name",
                        "description": "Brief description",
                        "price": 0.00,
                        "currency": "USD",
                        "category": "Electronics/Clothing/etc",
                        "quantity": 1
                    }
                ],
                "transaction": {
                    "merchant": "Merchant Name",
                    "date": "YYYY-MM-DD",
                    "order_number": "Order #",
                    "total_amount": 0.00,
                    "currency": "USD"
                }
            }
            If no inventory items are found, return items array as empty.
            """
            
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[prompt, email_body],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            if response.text:
                json_content = response.text
                
                # Save JSON
                json_path_rel = f"{self.base_path}/{base_name}.json"
                blob = self.bucket.blob(json_path_rel)
                blob.upload_from_string(json_content, content_type='application/json')
                
                self.logger.log_event("extracted", base_name, "Inventory JSON saved")

        except Exception as e:
            self.logger.log_event("error", base_name, f"Gemini Extraction Failed: {e}")

    def _get_html_body(self, message):
        body = ""
        if message.is_multipart():
            for part in message.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))
                if ctype == 'text/html' and 'attachment' not in cdispo:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                        return body
                    except:
                        pass
        else:
            # Fallback to plain text if that's all there is, or try to get payload
             try:
                 body = message.get_payload(decode=True).decode('utf-8', errors='replace')
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

    # Verify it's a job upload OR an extracted mbox
    if name.startswith("uploads/"):
        # Path: uploads/{userId}/{jobId}/{filename}
        parts = name.split('/')
        if len(parts) < 4:
            logger.error(f"Invalid upload path: {name}")
            return {"status": "error"}
        job_id = parts[2]
        user_id = parts[1]
        
    elif name.startswith("Hopper/Extracted/"):
        # Path: Hopper/Extracted/{userId}/{jobId}/{filename}
        parts = name.split('/')
        if len(parts) < 5:
             logger.error(f"Invalid extraction path: {name}")
             return {"status": "ignored"}
        
        # Verify it is an mbox file
        if not name.endswith(".mbox"):
             return {"status": "ignored"}

        user_id = parts[2]
        job_id = parts[3]
    else:
        logger.info(f"Ignoring non-upload file: {name}")
        return {"status": "ignored"}
    
    logger.info(f"Processing Job {job_id} for User {user_id}")
    job_service.update_progress(job_id, 10, "processing", "Worker started. Downloading file...")

    # Fetch Job Details (to get Auth Token)
    job_doc = db.collection("jobs").document(job_id).get()
    auth_token = None
    if job_doc.exists:
        auth_token = job_doc.to_dict().get('authToken')
    
    drive_uploader = None
    target_folder_id = None
    
    if auth_token:
        try:
            from drive_uploader import DriveUploader
            drive_uploader = DriveUploader(auth_token)
            # Ensure Path: Kintsu -> Hopper -> Gmail
            target_folder_id = drive_uploader.ensure_path(['Kintsu', 'Hopper', 'Gmail'])
            logger.info(f"Drive Upload configured. Target Folder: {target_folder_id}")
        except Exception as e:
            logger.error(f"Failed to configure Drive Uploader: {e}")
    else:
        logger.warning("No Auth Token found in job. Results will NOT be uploaded to Drive.")

    temp_file = None
    try:
        # Download file
        blob = storage_client.bucket(bucket).blob(name)
        _, temp_file = tempfile.mkstemp()
        blob.download_to_filename(temp_file)
        
        job_service.update_progress(job_id, 20, "processing", "File downloaded. Parsing Mbox...")
        
        # Define Extraction Path
        # Format: Hopper/gmail/extract_<zip_name>
        mbox_name = os.path.basename(name).replace('.mbox', '')
        extract_path = f"Hopper/gmail/extract_{mbox_name}"
        
        # Initialize Logger
        bucket_obj = storage_client.bucket(bucket)
        log_path = f"{extract_path}/processing_log.json"
        
        proc_logger = DriveLogger(bucket_obj, log_path)
        
        # Initialize Processor
        processor = EmailProcessor(bucket_obj, extract_path, proc_logger)
        
        # Parse Mbox
        mbox = mailbox.mbox(temp_file)
        total_messages = len(mbox)
        logger.info(f"Mbox contains {total_messages} messages")
        
        processed_count = 0
        
        for message in mbox:
            processed_count += 1
            if processed_count % 100 == 0:
                progress = 20 + int((processed_count / total_messages) * 70) 
                job_service.update_progress(job_id, progress, "processing", f"Processed {processed_count}/{total_messages} emails...")
                proc_logger.save()

            # Process Message
            result_name = processor.process_message(message)
            
            # Post-Process: Upload to Drive if configured
            if result_name and drive_uploader and target_folder_id:
                try:
                    # Upload HTML
                    html_blob = bucket_obj.blob(f"{extract_path}/{result_name}.html")
                    if html_blob.exists():
                        html_content = html_blob.download_as_text()
                        drive_uploader.upload_file(f"{result_name}.html", html_content, "text/html", target_folder_id)
                    
                    # Upload JSON (Inventory)
                    json_blob = bucket_obj.blob(f"{extract_path}/{result_name}.json")
                    if json_blob.exists():
                        json_content = json_blob.download_as_text()
                        drive_uploader.upload_file(f"{result_name}.json", json_content, "application/json", target_folder_id)
                        
                except Exception as up_err:
                    logger.error(f"Failed to upload result {result_name} to Drive: {up_err}")

        
        # Final Log Save
        proc_logger.save()
        
        job_service.update_progress(job_id, 90, "processing", f"Extraction complete. Processed {processed_count} emails.")
        
        # Cleanup GCS File (Zero Retention)
        blob.delete()
        job_service.update_progress(job_id, 100, "completed", "Job complete. Mbox processed and uploaded to Drive.")

    except Exception as e:
        logger.error(f"Job failed: {e}", exc_info=True)
        job_service.update_progress(job_id, 0, "failed", f"Error: {str(e)}")
        
    finally:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)

    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
