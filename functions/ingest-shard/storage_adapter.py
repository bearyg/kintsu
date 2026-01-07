from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import io
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

class StorageAdapter(ABC):
    @abstractmethod
    def list_files(self, path: str) -> List[Dict]:
        """List files in a directory"""
        pass

    @abstractmethod
    def get_file_metadata(self, path: str) -> Dict:
        """Get size and metadata"""
        pass

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

    def create_file(self, name: str, parent_id: str, content: any, mime_type: str = 'application/json') -> Dict:
        """
        Create a file or folder in a specific folder. Content can be str or bytes.
        If mime_type is 'application/vnd.google-apps.folder', content is ignored.
        """
        file_metadata = {
            'name': name,
            'parents': [parent_id],
            'mimeType': mime_type
        }
        
        if mime_type == 'application/vnd.google-apps.folder':
            file = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
        else:
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            else:
                content_bytes = content

            media = MediaIoBaseUpload(
                io.BytesIO(content_bytes),
                mimetype=mime_type,
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
        
        return file

    def update_file(self, file_id: str, content: any, mime_type: str = 'application/json') -> Dict:
        """
        Update an existing file's content. Content can be str or bytes.
        """
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content

        media = MediaIoBaseUpload(
            io.BytesIO(content_bytes),
            mimetype=mime_type,
            resumable=True
        )

        file = self.service.files().update(
            fileId=file_id,
            media_body=media,
            fields='id'
        ).execute()
        
        return file

    def download_file(self, file_id: str) -> bytes:
        """
        Download a file's content as bytes.
        """
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        return fh.getvalue()
    
    def find_file_by_name(self, name: str, parent_id: str) -> Optional[Dict]:
        """
        Finds a file by name in a specific parent folder.
        """
        query = f"name = '{name}' and '{parent_id}' in parents and trashed = false"
        results = self.service.files().list(q=query, fields='files(id, name)').execute()
        files = results.get('files', [])
        if files:
            return files[0]
        return None
