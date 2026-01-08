from google.cloud import firestore
import google.auth

def purge_extracted_data():
    """
    Retroactively removes 'extractedData' field from all documents in the 'shards' collection.
    """
    creds, project = google.auth.default()
    db = firestore.Client(project=project, credentials=creds)
    
    shards_ref = db.collection("shards")
    docs = shards_ref.stream()
    
    count = 0
    for doc in docs:
        data = doc.to_dict()
        if 'extractedData' in data:
            print(f"Purging data from shard {doc.id}...")
            shards_ref.document(doc.id).update({
                'extractedData': firestore.DELETE_FIELD
            })
            count += 1
            
    print(f"Finished. Purged {count} documents.")

if __name__ == "__main__":
    purge_extracted_data()
