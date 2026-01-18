import json
from datetime import datetime

class DriveLogger:
    def __init__(self, bucket, log_path):
        """
        Initializes the logger.
        :param bucket: GCS Bucket object
        :param log_path: Path to processing_log.json in GCS
        """
        self.bucket = bucket
        self.log_path = log_path
        self.log_data = {
            "start_time": datetime.utcnow().isoformat(),
            "summary": {
                "processed": 0, 
                "skipped_duplicate": 0, 
                "extracted_json": 0,
                "error": 0
            },
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
        if event_type == "processed":
            self.log_data["summary"]["processed"] += 1
        elif event_type == "skipped":
            self.log_data["summary"]["skipped_duplicate"] += 1
        elif event_type == "extracted":
            self.log_data["summary"]["extracted_json"] += 1
        elif event_type == "error":
            self.log_data["summary"]["error"] += 1
            
        # Log to stdout for Cloud Logging visibility
        print(json.dumps(entry))
            
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
