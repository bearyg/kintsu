from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import os
import json
import io
from google.cloud import storage
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

class StorageAdapter(ABC):
    @abstractmethod
    def list_files(self, path: str) -> List[Dict]:
        """List files in a directory (recursively or flat)"""
        pass

    @abstractmethod
    def get_file_metadata(self, path: str) -> Dict:
        """Get size and metadata"""
        pass

class LocalStorageAdapter(StorageAdapter):
    def __init__(self, root_path: str):
        self.root = root_path

    def list_files(self, relative_path: str) -> List[Dict]:
        target_dir = os.path.join(self.root, relative_path)
        results = []
        
        if not os.path.exists(target_dir):
            return []

        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.startswith("."): continue
                
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.root)
                
                results.append({
                    "name": file,
                    "path": rel_path,
                    "size": os.path.getsize(full_path)
                })
        return results

    def get_file_metadata(self, path: str) -> Dict:
        return {}

class GCSAdapter(StorageAdapter):
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.client = storage.Client()

    def list_files(self, relative_path: str) -> List[Dict]:
        """
        Lists blobs in GCS bucket with the given prefix.
        """
        bucket = self.client.bucket(self.bucket_name)
        # Ensure prefix ends with a slash to simulate folder listing
        prefix = relative_path if relative_path.endswith('/') else relative_path + '/'
        blobs = bucket.list_blobs(prefix=prefix)
        
        results = []
        for blob in blobs:
            # Skip the folder itself if it's returned as a blob
            if blob.name == prefix:
                continue
                
            results.append({
                "name": os.path.basename(blob.name),
                "path": blob.name,
                "size": blob.size
            })
        return results

    def get_file_metadata(self, path: str) -> Dict:
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.get_blob(path)
        if blob:
            return {
                "name": os.path.basename(blob.name),
                "path": blob.name,
                "size": blob.size,
                "content_type": blob.content_type,
                "updated": blob.updated
            }
        return {}

class DriveStorageAdapter(StorageAdapter):
    def __init__(self, root_folder_id: Optional[str] = None):
        """
        Initialize Drive Service.
        root_folder_id: Optional ID to act as the 'root' for relative paths.
        """
        creds, _ = google.auth.default()
        self.service = build('drive', 'v3', credentials=creds)
        self.root_id = root_folder_id

    def list_files(self, folder_id: str) -> List[Dict]:
        """
        List files in a specific Drive folder.
        'folder_id' is the Drive ID of the folder.
        """
        results = []
        page_token = None
        
        query = f"'{folder_id}' in parents and trashed = false"

        while True:
            response = self.service.files().list(
                q=query,
                spaces='drive',
                fields='nextPageToken, files(id, name, mimeType, size)',
                pageToken=page_token
            ).execute()
            
            for file in response.get('files', []):
                results.append({
                    "name": file.get('name'),
                    "path": file.get('id'), # Using ID as path for Drive
                    "size": int(file.get('size', 0)),
                    "mimeType": file.get('mimeType')
                })
                
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
                
        return results

    def get_file_metadata(self, file_id: str) -> Dict:
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, size, modifiedTime, parents'
            ).execute()
            return file
        except Exception as e:
            print(f"Error getting metadata for {file_id}: {e}")
            return {}

    def create_file(self, name: str, parent_id: str, content: str, mime_type: str = 'application/json') -> Dict:
        """
        Create a file in a specific folder.
        """
        file_metadata = {
            'name': name,
            'parents': [parent_id]
        }
        
        media = MediaIoBaseUpload(
            io.BytesIO(content.encode('utf-8')),
            mimetype=mime_type,
            resumable=True
        )
        
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file

    def update_file(self, file_id: str, content: str, mime_type: str = 'application/json') -> Dict:
        """
        Update an existing file's content.
        """
        media = MediaIoBaseUpload(
            io.BytesIO(content.encode('utf-8')),
            mimetype=mime_type,
            resumable=True
        )

        file = self.service.files().update(
            fileId=file_id,
            media_body=media,
            fields='id'
        ).execute()
        
        return file

