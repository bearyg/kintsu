from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
from typing import List, Dict, Any

class GmailProcessor:
    def __init__(self, access_token: str):
        self.creds = Credentials(token=access_token)
        self.service = build('gmail', 'v1', credentials=self.creds)

    def search_emails(self, query: str = 'label:inbox', max_results: int = 10) -> List[str]:
        """
        Searches for emails matching the query and returns a list of message IDs.
        """
        try:
            results = self.service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
            messages = results.get('messages', [])
            return [m['id'] for m in messages]
        except Exception as e:
            print(f"[GmailProcessor] Search error: {e}")
            return []

    def get_email_details(self, message_id: str) -> Dict[str, Any]:
        """
        Fetches full email details including headers and body.
        """
        try:
            message = self.service.users().messages().get(userId='me', id=message_id).execute()
            return message
        except Exception as e:
            print(f"[GmailProcessor] Get details error: {e}")
            return {}

    def extract_metadata(self, message: Dict[str, Any]) -> Dict[str, str]:
        """
        Extracts sender, date, and subject from email headers.
        """
        headers = message.get('payload', {}).get('headers', [])
        metadata = {
            'from': '',
            'date': '',
            'subject': ''
        }
        for header in headers:
            name = header.get('name', '').lower()
            if name == 'from':
                metadata['from'] = header.get('value', '')
            elif name == 'date':
                metadata['date'] = header.get('value', '')
            elif name == 'subject':
                metadata['subject'] = header.get('value', '')
        return metadata

    def extract_attachments(self, message_id: str, part: Dict[str, Any]) -> bytes:
        """
        Extracts attachment data from a message part.
        """
        try:
            attachment_id = part['body'].get('attachmentId')
            if not attachment_id:
                return b''
            
            attachment = self.service.users().messages().attachments().get(
                userId='me', messageId=message_id, id=attachment_id
            ).execute()
            
            data = attachment.get('data')
            if data:
                return base64.urlsafe_b64decode(data)
            return b''
        except Exception as e:
            print(f"[GmailProcessor] Extract attachment error: {e}")
            return b''

    def parse_body(self, message: Dict[str, Any]) -> str:
        """
        Parses the email body (prefers plain text, falls back to HTML).
        """
        payload = message.get('payload', {})
        parts = payload.get('parts', [])
        
        body_text = ""
        
        def find_text_part(parts):
            nonlocal body_text
            for part in parts:
                mime_type = part.get('mimeType')
                if mime_type == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        body_text += base64.urlsafe_b64decode(data).decode('utf-8')
                elif mime_type == 'text/html' and not body_text:
                    # If we don't have plain text yet, consider HTML (maybe strip tags later)
                    data = part['body'].get('data')
                    if data:
                        body_text += base64.urlsafe_b64decode(data).decode('utf-8')
                elif 'parts' in part:
                    find_text_part(part['parts'])

        if 'parts' in payload:
            find_text_part(payload['parts'])
        else:
            # Simple payload
            data = payload.get('body', {}).get('data')
            if data:
                body_text = base64.urlsafe_b64decode(data).decode('utf-8')
                
        return body_text
