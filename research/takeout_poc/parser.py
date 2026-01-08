import mailbox
import email
from email.policy import default
import sys
import os

def extract_body(message):
    """
    Extracts the HTML body (or plain text if no HTML) from an email message.
    """
    body = ""
    if message.is_multipart():
        for part in message.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            # skip any text/plain (txt) attachments
            if ctype == 'text/html' and 'attachment' not in cdispo:
                try:
                    body = part.get_payload(decode=True).decode('utf-8')
                    return body  # Return immediately if HTML found
                except:
                    pass
    else:
        # Not multipart - just get payload
        try:
             body = message.get_payload(decode=True).decode('utf-8')
        except:
            pass
    return body

def parse_mbox(mbox_path):
    """
    Parses an Mbox file and prints a summary of the first 5 emails.
    """
    if not os.path.exists(mbox_path):
        print(f"Error: File not found: {mbox_path}")
        return

    print(f"Scanning {mbox_path}...")
    
    mbox = mailbox.mbox(mbox_path, factory=None)
    
    count = 0
    for message in mbox:
        count += 1
        subject = message.get('subject', 'No Subject')
        sender = message.get('from', 'Unknown Sender')
        date = message.get('date', 'Unknown Date')
        
        # Parse body
        body = extract_body(message)
        body_snippet = body[:100].replace('\n', ' ') if body else "No Body Content"

        print(f"[{count}] Subject: {subject}")
        print(f"    From: {sender}")
        print(f"    Date: {date}")
        print(f"    Body Snippet: {body_snippet}...")
        print("-" * 40)

        if count >= 5:
            break
            
    print(f"Finished scanning. Total messages processed: {count}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parser.py <path_to_mbox_file>")
    else:
        parse_mbox(sys.argv[1])
