import requests
import logging
import os
import json

logger = logging.getLogger(__name__)

class DriveUploader:
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.base_url = "https://www.googleapis.com/drive/v3/files"
        self.headers = {
            "Authorization": f"Bearer {auth_token}"
        }

    def find_folder(self, name, parent_id='root'):
        try:
            query = f"name='{name}' and '{parent_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'"
            params = {'q': query, 'fields': 'files(id, name)'}
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            files = response.json().get('files', [])
            return files[0]['id'] if files else None
        except Exception as e:
            logger.error(f"Error finding folder {name}: {e}")
            return None

    def create_subfolder(self, name, parent_id):
        try:
            metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            response = requests.post(self.base_url, headers=self.headers, json=metadata)
            response.raise_for_status()
            return response.json().get('id')
        except Exception as e:
            logger.error(f"Error creating folder {name}: {e}")
            return None

    def upload_file(self, filename, content, mime_type, parent_id):
        try:
            # Simple upload for small files (JSON/HTML)
            metadata = {
                'name': filename,
                'parents': [parent_id]
            }
            
            files = {
                'data': ('metadata', json.dumps(metadata), 'application/json'),
                'file': (filename, content, mime_type)
            }
            
            upload_url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
            response = requests.post(upload_url, headers=self.headers, files=files)
            
            if response.status_code == 200:
                return response.json().get('id')
            else:
                logger.error(f"Upload failed: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error uploading {filename}: {e}")
            return None

    def ensure_path(self, path_segments, root_id='root'):
        """
        Ensures a folder path exists (e.g. ['Kintsu', 'Hopper', 'Gmail']).
        Returns the ID of the final folder.
        """
        current_id = root_id
        for segment in path_segments:
            found_id = self.find_folder(segment, current_id)
            if not found_id:
                found_id = self.create_subfolder(segment, current_id)
            
            if not found_id:
                raise Exception(f"Failed to navigate/create folder: {segment}")
            current_id = found_id
        return current_id
