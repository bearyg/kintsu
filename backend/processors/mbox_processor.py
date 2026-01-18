from typing import List, Optional
import mailbox
import os
import json
import logging
import io
import time
import base64
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class MboxProcessor:
    def __init__(self, drive_service_wrapper):
        self.drive = drive_service_wrapper
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    async def process_file(self, file_path: str, folder_id: str):
        """Processes a file (MBOX or ZIP containing MBOX) and uploads results to Drive."""
        if file_path.endswith('.zip'):
             import zipfile
             with zipfile.ZipFile(file_path, 'r') as zip_ref:
                extract_path = file_path + "_extracted"
                zip_ref.extractall(extract_path)
                for root, dirs, files in os.walk(extract_path):
                    for file in files:
                        if file.endswith('.mbox') or file.lower() == "all mail including spam and trash.mbox":
                            await self.process_mbox(os.path.join(root, file), folder_id)
        elif file_path.endswith('.mbox'):
            await self.process_mbox(file_path, folder_id)

    async def process_mbox(self, mbox_path: str, folder_id: str):
        mbox = mailbox.mbox(mbox_path)
        logger.info(f"Processing MBOX: {mbox_path} with {len(mbox)} messages")
        
        # Create output folder for this batch
        batch_folder_name = f"Processed_{os.path.basename(mbox_path)}_{int(time.time())}"
        batch_folder_id = self.drive.ensure_folder(batch_folder_name, folder_id)

        count = 0
        for message in mbox:
            count += 1
            if count > 50: break # Limit for testing/demo? Or process all? User said "Process zip", so maybe all. But careful with timeouts.
            # Maybe restrict to 50 for now or use background task.
            
            try:
                await self.process_email(message, batch_folder_id)
            except Exception as e:
                logger.error(f"Error processing email {count}: {e}")

    async def process_email(self, message, folder_id):
        # Extract HTML/Body
        body = self._get_html_body(message)
        if not body: return

        # Gemini Analysis
        inventory = self.extract_inventory(body)
        if inventory:
             # Save JSON to Drive
             msg_id = message.get('Message-ID', '').strip() or f"no_id_{int(time.time()*100000)}"
             safe_name = "".join([c for c in msg_id if c.isalnum() or c in ('-','_')])
             
             # Upload EML
             try:
                # message.as_bytes() might fail if not bytes, try as_string if needed or encode
                eml_content = message.as_string()
                self.drive.upload_file_content(f"{safe_name}.eml", eml_content, "message/rfc822", folder_id)
             except Exception as e:
                logger.error(f"Failed to save EML for {safe_name}: {e}")

             # Upload HTML
             self.drive.upload_file_content(f"{safe_name}.html", body, "text/html", folder_id)

             # Upload JSON
             self.drive.upload_file_content(f"{safe_name}.json", json.dumps(inventory, indent=2), "application/json", folder_id)

    def _get_html_body(self, message):
        # ... reuse logic ...
        body = ""
        if message.is_multipart():
            for part in message.walk():
                ctype = part.get_content_type()
                if ctype == 'text/html':
                    try: return part.get_payload(decode=True).decode('utf-8', errors='replace')
                    except: pass
        else:
            try: return message.get_payload(decode=True).decode('utf-8', errors='replace')
            except: pass
        return body

    def extract_inventory(self, email_body):
        if not self.client: return None
        try:
             prompt = "Analyze this email and extract unique inventory items..." # reuse prompt
             response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=[prompt, email_body],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
             return json.loads(response.text)
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return None
