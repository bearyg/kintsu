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
    """HTTP Cloud Function to scan and ingest Gmail data (DEPRECATED)."""
    logger.warning("Call to DEPRECATED ingest_gmail function. Direct Gmail access is no longer supported.")
    return {"error": "Direct Gmail access is deprecated. Please use the Google Takeout ingestion flow instead."}, 410
