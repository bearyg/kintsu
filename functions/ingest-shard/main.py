import functions_framework
from google.cloud import storage, firestore
from google import genai
import os
import json
import zipfile
import io
import tempfile
import time

# Import BYOS modules
try:
    from storage_adapter import DriveStorageAdapter
    from aggregator import InventoryAggregator
except ImportError as e:
    print(f"BYOS Import Error: {e}")
    # Fallback or allow failure if modules missing in some envs
    pass

# Initialize clients
storage_client = storage.Client()
db = firestore.Client()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Failed to initialize Gemini Client: {e}")

def handle_zip_archive(bucket, blob):
    """
    Downloads, unzips, and re-uploads files to GCS under Hopper/Extracted/
    """
    zip_name = os.path.basename(blob.name).replace('.zip', '')
    
    # Extract Context (User/Job) from path if available
    # Path: uploads/{userId}/{jobId}/{filename}
    parts = blob.name.split('/')
    base_path = f"Hopper/Extracted/{zip_name}"
    
    if len(parts) >= 4 and parts[0] == 'uploads':
        user_id = parts[1]
        job_id = parts[2]
        base_path = f"Hopper/Extracted/{user_id}/{job_id}"
        print(f"Detected Context - User: {user_id}, Job: {job_id}")

    print(f"Unzipping {blob.name} to {base_path}/...")

    try:
        zip_bytes = blob.download_as_bytes()
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            for filename in z.namelist():
                if filename.endswith('/'): continue # Skip directories
                
                # Check for hidden files (__MACOSX, .ds_store)
                if '__MACOSX' in filename or filename.startswith('.'):
                    continue

                file_data = z.read(filename)
                
                # Construct new path: {base_path}/{filename}
                new_blob_name = f"{base_path}/{filename}"
                
                new_blob = bucket.blob(new_blob_name)
                new_blob.upload_from_string(file_data)
                print(f"-> Extracted: {new_blob_name}")
                
    except Exception as e:
        print(f"Error processing zip {blob.name}: {e}")
    else:
        # Only delete if no exception occurred
        print(f"Extraction complete. Deleting source zip: {blob.name}")
        try:
            blob.delete()
        except Exception as e:
            print(f"Failed to delete source zip {blob.name}: {e}")

def extract_data_with_gemini(blob, mime_type):
    """
    Uses Gemini 2.5 Pro to extract structured data from the file.
    """
    if not client:
        print("Gemini Client not initialized.")
        return None

    print(f"Starting Gemini 2.5 Pro extraction for {blob.name} ({mime_type})")
    
    # 1. Download to temp file
    _, temp_local_filename = tempfile.mkstemp()
    blob.download_to_filename(temp_local_filename)

    try:
        # 2. Upload to Gemini
        # New API uses client.files.upload
        gemini_file = client.files.upload(file=temp_local_filename, config={'mime_type': mime_type})
        
        # Wait for processing if necessary
        while gemini_file.state.name == "PROCESSING":
            time.sleep(2)
            gemini_file = client.files.get(name=gemini_file.name)

        # 3. Generate Content
        prompt = """
        Analyze this document/image for a property insurance claim. 
        Extract the following fields and return ONLY a valid JSON object:
        {
            "item_name": "Name of the main item or service",
            "merchant": "Name of store or vendor",
            "date": "Date of purchase/transaction (YYYY-MM-DD)",
            "total_amount": "Total cost (number only, no currency symbol)",
            "currency": "Currency code (USD, etc)",
            "category": "Suggested category (Electronics, Furniture, Clothing, etc)",
            "confidence": "High/Medium/Low assessment of this extraction"
        }
        If a field is not found, use null.
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=[prompt, gemini_file]
        )
        
        # Parse JSON response
        text = response.text.replace('```json', '').replace('```', '').strip()
        match = None
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match: text = match.group(0)
            
        return json.loads(text)

    except Exception as e:
        print(f"Gemini Extraction Error: {e}")
        return None
    finally:
        if os.path.exists(temp_local_filename):
            os.remove(temp_local_filename)
        
        # 4. Cleanup Gemini File
        if 'gemini_file' in locals() and gemini_file:
            try:
                print(f"Deleting Gemini file: {gemini_file.name}")
                client.files.delete(name=gemini_file.name)
            except Exception as e:
                print(f"Failed to delete Gemini file: {e}")

@functions_framework.cloud_event
def process_new_shard(cloud_event):
    """
    Triggered by a change to a Cloud Storage bucket.
    """
    data = cloud_event.data
    bucket_name = data["bucket"]
    file_name = data["name"]
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.get_blob(file_name)

    if not blob: return

    print(f"Processing: {file_name}")

    # 1. ZIP Handling
    if file_name.lower().endswith('.zip'):
        handle_zip_archive(bucket, blob)
        return

    # 2. Identify Source Type
    parts = file_name.split('/')
    source_type = "Unknown"
    
    if len(parts) > 1 and parts[0] == 'Hopper':
        if parts[1] == 'Extracted' and len(parts) > 3:
            potential_source = parts[3]
            if potential_source in ['Amazon', 'Banking', 'Gmail', 'Photos']:
                source_type = potential_source
            else:
                source_type = "Extracted_Generic"
        elif len(parts) > 2:
            source_type = parts[1]

    # 3. Create Initial Shard Record (DEPRECATED: Shards are not used, we read from Drive directly)
    # shard_id = f"{source_type}_{blob.generation}"
    
    # shard_data = {
    #     "id": shard_id,
    #     "sourceType": source_type,
    #     "filePath": file_name,
    #     "fileName": os.path.basename(file_name),
    #     "status": "unprocessed",
    #     "size": blob.size,
    #     "contentType": blob.content_type,
    #     "createdAt": firestore.SERVER_TIMESTAMP
    # }

    # db.collection("shards").document(shard_id).set(shard_data)
    # print(f"Shard {shard_id} indexed. Source: {source_type}")

    # 4. AI Extraction (The Refinery)
    supported_types = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf']
    
    if blob.content_type in supported_types and GEMINI_API_KEY:
        # print(f"Refining shard {shard_id}...")
        extracted_data = extract_data_with_gemini(blob, blob.content_type)
        
        if extracted_data:
            # BYOS Implementation
            try:
                drive_adapter = DriveStorageAdapter()
                
                # Find or Create 'Kintsu' folder in Drive Root
                kintsu_folder = drive_adapter.find_file_by_name("Kintsu", "root")
                if not kintsu_folder:
                    print("Creating Kintsu folder in Drive...")
                    kintsu_folder = drive_adapter.create_file("Kintsu", "root", "", "application/vnd.google-apps.folder")
                
                kintsu_folder_id = kintsu_folder['id']

                # 1. Write Sidecar (.kintsu.json)
                sidecar_name = f"{os.path.basename(file_name)}.kintsu.json"
                sidecar_content = json.dumps(extracted_data, indent=2)
                
                # Check if exists to update or create? For now assume create (overwrite usually requires update in Drive)
                # Helper to check?
                existing_sidecar = drive_adapter.find_file_by_name(sidecar_name, kintsu_folder_id)
                if existing_sidecar:
                    new_file = drive_adapter.update_file(existing_sidecar['id'], sidecar_content)
                else:
                    new_file = drive_adapter.create_file(sidecar_name, kintsu_folder_id, sidecar_content)
                
                print(f"Sidecar created/updated: {new_file.get('id')}")

                # 2. Append to Master Inventory
                aggregator = InventoryAggregator(drive_adapter)
                aggregator.append_item(kintsu_folder_id, extracted_data, os.path.basename(file_name))

                # 3. Update Firestore (Status Only) - DEPRECATED
                # db.collection("shards").document(shard_id).update({
                #     "status": "refined",
                #     "driveFileId": new_file.get('id'),
                #     "refinedAt": firestore.SERVER_TIMESTAMP
                # })
                print(f"Shard refined (BYOS Mode).")

                # 4. Cleanup Source Blob
                try:
                    print(f"Cleanup: Deleting processed shard {file_name}")
                    blob.delete()
                except Exception as e:
                    print(f"Failed to delete processed shard {file_name}: {e}")

            except Exception as e:
                print(f"BYOS/Drive Error: {e}")
                # db.collection("shards").document(shard_id).update({
                #     "status": "error",
                #     "errorMsg": f"BYOS Error: {str(e)}"
                # })

        else:
             # db.collection("shards").document(shard_id).update({
             #    "status": "error",
             #    "errorMsg": "Gemini extraction failed"
             # })
            pass
    else:
        print(f"Skipping refinement for {blob.content_type}")
