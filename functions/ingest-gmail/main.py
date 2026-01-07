import functions_framework
import os
import json
import re
import logging
from google.cloud import firestore, storage
from processor import GmailProcessor

# Configure Logging
logger = logging.getLogger(__name__)

db = firestore.Client()
storage_client = storage.Client()
BUCKET_NAME = "kintsu-hopper-kintsu-gcp"

def save_shard(shard_data: dict, shard_id: str):
    db.collection("shards").document(shard_id).set(shard_data)
    logger.info(f"Saved shard: {shard_id}")

@functions_framework.http
def ingest_gmail(request):
    """HTTP Cloud Function to scan Gmail and upload HTML artifacts to GCS."""
    try:
        req_json = request.get_json(silent=True)
        if not req_json:
            return {"error": "Invalid JSON"}, 400

        access_token = req_json.get('access_token')
        query = req_json.get('query', 'subject:(order OR confirmation OR receipt OR invoice)')
        max_results = req_json.get('max_results', 10)
        debug_mode = req_json.get('debug_mode', False)
        trace_id = req_json.get('trace_id')

        # Adjust logging level
        if debug_mode:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.setLevel(logging.DEBUG)
            logger.info(f"DEBUG MODE ENABLED for Gmail Scan (Trace: {trace_id}). Query: {query}")
        else:
            logging.getLogger().setLevel(logging.INFO)
            logger.setLevel(logging.INFO)
            logger.info(f"Starting Gmail scan (Trace: {trace_id}): {query}")

        if not access_token:
             return {"error": "Missing access_token"}, 400

        try:
            logger.debug(f"Initializing GmailProcessor")
            processor = GmailProcessor(access_token)
        except Exception as init_err:
            logger.critical(f"Failed to initialize GmailProcessor: {init_err}", exc_info=True)
            return {"error": "Failed to initialize GmailProcessor"}, 500

        # Search
        try:
            logger.debug(f"Searching emails with query: {query}")
            message_ids = processor.search_emails(query=query, max_results=max_results)
            logger.info(f"Found {len(message_ids)} emails to process.")
        except Exception as search_err:
            logger.error(f"Gmail search failed: {search_err}", exc_info=True)
            return {"error": str(search_err)}, 500

        if not message_ids:
            return {"status": "success", "message": "No emails found matching criteria."}

        processed_count = 0
        bucket = storage_client.bucket(BUCKET_NAME)

        for msg_id in message_ids:
            try:
                logger.debug(f"Fetching details for message: {msg_id}")
                message = processor.get_email_details(msg_id)
                metadata = processor.extract_metadata(message)
                
                # Use HTML body if available, otherwise plain text
                html_body = processor.get_raw_html(message)
                if not html_body:
                    html_body = f"<html><body><pre>{processor.parse_body(message)}</pre></body></html>"
                
                # Sanitize filename
                safe_subject = re.sub(r'[^a-zA-Z0-9]', '_', metadata.get('subject', 'NoSubject'))[:50]
                gcs_filename = f"Hopper/Gmail/{msg_id}_{safe_subject}.html"
                
                # Upload to GCS
                blob = bucket.blob(gcs_filename)
                blob.upload_from_string(html_body, content_type='text/html')
                logger.info(f"Uploaded email artifact: {gcs_filename}")
                
                # Create Shard record (unprocessed)
                # The ingest-shard trigger will see this and perform Gemini extraction
                shard_id = f"Gmail_{msg_id}"
                shard_data = {
                    "id": shard_id,
                    "fileName": f"{msg_id}_{safe_subject}.html",
                    "filePath": gcs_filename,
                    "sourceType": "Gmail",
                    "status": "unprocessed",
                    "createdAt": firestore.SERVER_TIMESTAMP
                }
                save_shard(shard_data, shard_id)
                processed_count += 1
                
            except Exception as msg_err:
                logger.error(f"Error processing message {msg_id}: {msg_err}", exc_info=True)

        return {"status": "success", "processed_count": processed_count}

    except Exception as e:
        logger.critical(f"Critical Gmail Scan Error: {e}", exc_info=True)
        return {"error": str(e)}, 500
