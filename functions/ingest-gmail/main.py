import functions_framework
import os
import json
import re
import logging
from google.cloud import firestore
import google.generativeai as genai
from processor import GmailProcessor

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = firestore.Client()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not set. Body analysis will fail.")

def save_shard(shard_data: dict, shard_id: str):
    db.collection("shards").document(shard_id).set(shard_data)
    logger.info(f"Saved shard: {shard_id}")

@functions_framework.http
def ingest_gmail(request):
    """HTTP Cloud Function to scan and ingest Gmail data."""
    try:
        req_json = request.get_json(silent=True)
        if not req_json:
            return {"error": "Invalid JSON"}, 400

        access_token = req_json.get('access_token')
        query = req_json.get('query', 'subject:(order OR confirmation OR receipt OR invoice)')
        max_results = req_json.get('max_results', 10)
        debug_mode = req_json.get('debug_mode', False)
        trace_id = req_json.get('trace_id')

        if not access_token:
             return {"error": "Missing access_token"}, 400

        if debug_mode:
            logger.setLevel(logging.DEBUG)
            logger.info(f"DEBUG MODE ENABLED for Gmail Scan (Trace: {trace_id}). Query: {query}")
        else:
            logger.info(f"Starting Gmail scan (Trace: {trace_id}): {query}")

        try:
            logger.debug(f"Initializing GmailProcessor with token: {access_token[:10]}...")
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

        for msg_id in message_ids:
            try:
                logger.debug(f"Fetching details for message: {msg_id}")
                message = processor.get_email_details(msg_id)
                
                metadata = processor.extract_metadata(message)
                logger.info(f"Processing email: {metadata.get('subject', 'No Subject')} from {metadata.get('from', 'Unknown')}")
                
                body = processor.parse_body(message)
                
                if len(body) > 100:
                    shard_id = f"gmail_body_{msg_id}"
                    
                    doc = db.collection("shards").document(shard_id).get()
                    if not doc.exists:
                        if not GEMINI_API_KEY:
                            logger.error("Skipping body analysis due to missing API Key")
                            continue

                        logger.debug(f"Refining email body with Gemini for {shard_id}")
                        model = genai.GenerativeModel('gemini-2.5-pro')
                        prompt = f"""
                        Analyze this email content from {metadata['from']} about {metadata['subject']}.
                        Extract financial record details (order, receipt, etc).
                        
                        Return ONLY JSON:
                        {{
                            "item_name": "Product or Service name",
                            "merchant": "Store Name",
                            "date": "{metadata['date']}",
                            "total_amount": number,
                            "currency": "USD",
                            "category": "Type",
                            "confidence": "High/Med/Low"
                        }}
                        
                        Email Body:
                        {body[:4000]} 
                        """
                        
                        gen_resp = model.generate_content(prompt)
                        text = gen_resp.text
                        
                        extracted_data = {}
                        try:
                            clean_text = text.replace('```json', '').replace('```', '').strip()
                            match = re.search(r'\{.*\}', clean_text, re.DOTALL)
                            if match: clean_text = match.group(0)
                            extracted_data = json.loads(clean_text)
                        except json.JSONDecodeError:
                            logger.error(f"JSON Parse Error for email {msg_id}.")
                            extracted_data = {"item_name": metadata['subject'], "raw_analysis": text, "confidence": "Low"}
                        
                        shard_data = {
                            "id": shard_id,
                            "fileName": f"Email: {metadata['subject']}",
                            "sourceType": "Gmail",
                            "status": "refined",
                            "extractedData": extracted_data,
                            "createdAt": firestore.SERVER_TIMESTAMP
                        }
                        save_shard(shard_data, shard_id)
                        processed_count += 1
                    else:
                        logger.debug(f"Skipping existing shard: {shard_id}")
                
            except Exception as msg_err:
                logger.error(f"Error processing message {msg_id}: {msg_err}", exc_info=True)

        return {"status": "success", "processed_count": processed_count}

    except Exception as e:
        logger.critical(f"Critical Gmail Scan Error: {e}", exc_info=True)
        return {"error": str(e)}, 500
