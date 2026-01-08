import functions_framework
import os
import tempfile
import zipfile
import shutil
import requests
import json
import logging
import io
from google.cloud import firestore
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from processor import AmazonProcessor

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = firestore.Client()

def get_drive_service(access_token):
    creds = Credentials(access_token)
    return build('drive', 'v3', credentials=creds)

def find_or_create_folder(service, name, parent_id='root'):
    query = f"name = '{name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields='files(id, name)').execute()
    files = results.get('files', [])
    if files:
        return files[0]['id']
    
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    file = service.files().create(body=file_metadata, fields='id').execute()
    return file.get('id')

def write_sidecar(service, parent_id, name, content):
    file_metadata = {
        'name': name,
        'parents': [parent_id],
        'mimeType': 'application/json'
    }
    media = MediaIoBaseUpload(io.BytesIO(json.dumps(content, indent=2).encode('utf-8')), mimetype='application/json')
    
    # Check if exists
    query = f"name = '{name}' and '{parent_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields='files(id, name)').execute()
    files = results.get('files', [])
    
    if files:
        file = service.files().update(fileId=files[0]['id'], media_body=media, fields='id').execute()
    else:
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

def save_shard(shard_data: dict, shard_id: str):
    db.collection("shards").document(shard_id).set(shard_data)
    logger.info(f"Saved shard: {shard_id}")

@functions_framework.http
def process_amazon(request):
    """HTTP Cloud Function to process Amazon data files (BYOS Mode)."""
    try:
        req_json = request.get_json(silent=True)
        if not req_json:
            return {"error": "Invalid JSON"}, 400

        file_id = req_json.get('file_id')
        file_name = req_json.get('fileName')
        access_token = req_json.get('access_token')
        source_type = req_json.get('source_type', 'Amazon')
        debug_mode = req_json.get('debug_mode', False)

        if not all([file_id, file_name, access_token]):
             return {"error": "Missing required fields"}, 400

        logger.info(f"Starting Amazon processing for: {file_name} (Debug: {debug_mode})")
        drive_service = get_drive_service(access_token)
        
        # Ensure Kintsu folder exists
        kintsu_id = find_or_create_folder(drive_service, "Kintsu")

        work_dir = tempfile.mkdtemp()
        try:
            # Download
            headers = {"Authorization": f"Bearer {access_token}"}
            drive_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
            response = requests.get(drive_url, headers=headers, stream=True)
            if response.status_code != 200:
                logger.error(f"Download failed: {response.text}")
                return {"error": "Download failed"}, 500

            local_filename = os.path.join(work_dir, file_name)
            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Unzip / List Files
            files_to_process = [] 
            if file_name.lower().endswith('.zip'):
                logger.info("Unzipping archive...")
                extract_dir = os.path.join(work_dir, "extracted")
                os.makedirs(extract_dir, exist_ok=True)
                with zipfile.ZipFile(local_filename, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        if file.startswith('.') or '__MACOSX' in root: continue
                        files_to_process.append((os.path.join(root, file), file))
            else:
                files_to_process.append((local_filename, file_name))

            # Process
            processor = AmazonProcessor()
            sibling_files = [f[0] for f in files_to_process]
            
            processed_count = 0

            for file_path, current_file_name in files_to_process:
                if processor.can_process(file_path, source_type):
                    shards, excluded = processor.process(
                        file_path, 
                        current_file_name, 
                        sibling_files=sibling_files, 
                        debug=debug_mode
                    )
                    
                    for i, shard_data in enumerate(shards):
                        shard_id = f"amazon_{file_id}_{i}"
                        
                        # BYOS: Write sidecar to Drive
                        sidecar_name = f"{current_file_name}_item_{i+1}.kintsu.json"
                        drive_sidecar_id = write_sidecar(drive_service, kintsu_id, sidecar_name, shard_data)

                        final_shard = {
                            "id": shard_id,
                            "fileName": f"{current_file_name} (Item {i+1})",
                            "sourceType": "Amazon",
                            "parentZip": file_name,
                            "status": "refined",
                            "driveFileId": drive_sidecar_id,
                            "createdAt": firestore.SERVER_TIMESTAMP
                        }
                        save_shard(final_shard, shard_id)
                    
                    processed_count += len(shards)

                    if debug_mode and excluded:
                        batch = db.batch()
                        for i, item in enumerate(excluded):
                            debug_id = f"debug_excl_{file_id}_{i}"
                            doc_ref = db.collection("debug_excluded_items").document(debug_id)
                            batch.set(doc_ref, {
                                "fileName": current_file_name,
                                "parentZip": file_name,
                                "reason": item.get('reason'),
                                "item": item,
                                "createdAt": firestore.SERVER_TIMESTAMP
                            })
                        batch.commit()

            return {"status": "success", "processed_items": processed_count}

        finally:
            shutil.rmtree(work_dir)
            
    except Exception as e:
        logger.error(f"Function Error: {e}", exc_info=True)
        return {"error": str(e)}, 500

