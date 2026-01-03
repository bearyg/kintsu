import functions_framework
from google.cloud import storage, firestore
import google.generativeai as genai
import os
import json
import zipfile
import io
import tempfile
import time

# Initialize clients
storage_client = storage.Client()
db = firestore.Client()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def handle_zip_archive(bucket, blob):
    """
    Downloads, unzips, and re-uploads files to GCS under Hopper/Extracted/
    """
    zip_name = os.path.basename(blob.name).replace('.zip', '')
    print(f"Unzipping {blob.name} to Hopper/Extracted/{zip_name}/...")

    try:
        zip_bytes = blob.download_as_bytes()
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            for filename in z.namelist():
                if filename.endswith('/'): continue # Skip directories
                
                # Check for hidden files (__MACOSX, .ds_store)
                if '__MACOSX' in filename or filename.startswith('.'):
                    continue

                file_data = z.read(filename)
                
                # Construct new path: Hopper/Extracted/{ZipName}/{OriginalStructure}
                new_blob_name = f"Hopper/Extracted/{zip_name}/{filename}"
                
                new_blob = bucket.blob(new_blob_name)
                new_blob.upload_from_string(file_data)
                print(f"-> Extracted: {new_blob_name}")
                
    except Exception as e:
        print(f"Error processing zip {blob.name}: {e}")

def extract_data_with_gemini(blob, mime_type):
    """
    Uses Gemini 2.5 Pro to extract structured data from the file.
    """
    print(f"Starting Gemini 2.5 Pro extraction for {blob.name} ({mime_type})")
    
    # 1. Download to temp file
    _, temp_local_filename = tempfile.mkstemp()
    blob.download_to_filename(temp_local_filename)

    try:
        # 2. Upload to Gemini
        gemini_file = genai.upload_file(path=temp_local_filename, mime_type=mime_type)
        
        # Wait for processing if necessary (mostly for video, but good practice)
        while gemini_file.state.name == "PROCESSING":
            time.sleep(2)
            gemini_file = genai.get_file(gemini_file.name)

        # 3. Generate Content
        model = genai.GenerativeModel('gemini-2.5-pro')
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
        
        response = model.generate_content([prompt, gemini_file])
        
        # Cleanup Gemini file
        genai.delete_file(gemini_file.name)
        
        # Parse JSON response
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text)

    except Exception as e:
        print(f"Gemini Extraction Error: {e}")
        return None
    finally:
        if os.path.exists(temp_local_filename):
            os.remove(temp_local_filename)

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

    # 3. Create Initial Shard Record
    shard_id = f"{source_type}_{blob.generation}"
    
    shard_data = {
        "id": shard_id,
        "sourceType": source_type,
        "filePath": file_name,
        "fileName": os.path.basename(file_name),
        "status": "unprocessed",
        "size": blob.size,
        "contentType": blob.content_type,
        "createdAt": firestore.SERVER_TIMESTAMP
    }

    db.collection("shards").document(shard_id).set(shard_data)
    print(f"Shard {shard_id} indexed. Source: {source_type}")

    # 4. AI Extraction (The Refinery)
    supported_types = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf']
    
    if blob.content_type in supported_types and GEMINI_API_KEY:
        print(f"Refining shard {shard_id}...")
        extracted_data = extract_data_with_gemini(blob, blob.content_type)
        
        if extracted_data:
            db.collection("shards").document(shard_id).update({
                "status": "refined",
                "extractedData": extracted_data,
                "refinedAt": firestore.SERVER_TIMESTAMP
            })
            print(f"Shard {shard_id} successfully refined.")
        else:
             db.collection("shards").document(shard_id).update({
                "status": "error",
                "errorMsg": "Gemini extraction failed"
            })
    else:
        print(f"Skipping refinement for {blob.content_type}")


