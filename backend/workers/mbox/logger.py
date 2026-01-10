import json
import time
from datetime import datetime

class DriveLogger:
    def __init__(self, bucket, log_path):
        """
        Initializes the logger.
        :param bucket: GCS Bucket object
        :param log_path: Path to processing_log.json in GCS (e.g., Hopper/gmail/extract_.../processing_log.json)
        """
        self.bucket = bucket
        self.log_path = log_path
        self.log_data = {
            "start_time": datetime.utcnow().isoformat(),
            "summary": {"processed": 0, "skipped": 0, "errors": 0},
            "events": []
        }
    
    def log_event(self, event_type, message_id, details=None):
        """
        Logs an event (processed, skipped, error).
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "message_id": message_id,
            "details": details or ""
        }
        self.log_data["events"].append(entry)
        
        # Update summary
        if event_type in self.log_data["summary"]:
            self.log_data["summary"][event_type] += 1
            
    def save(self):
        """
        Computes final stats and uploads log to GCS.
        """
        self.log_data["end_time"] = datetime.utcnow().isoformat()
        
        # Convert to JSON string
        json_content = json.dumps(self.log_data, indent=2)
        
        # Upload
        blob = self.bucket.blob(self.log_path)
        blob.upload_from_string(json_content, content_type="application/json")
        print(f"Log saved to {self.log_path}")
