from abc import ABC, abstractmethod
from typing import List, Dict
import os
from google.cloud import storage

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

