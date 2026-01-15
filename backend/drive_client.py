from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import os

class DriveServiceWrapper:
    def __init__(self, access_token):
        creds = Credentials(token=access_token)
        self.service = build('drive', 'v3', credentials=creds)

    def ensure_folder(self, name: str, parent_id: str) -> str:
        # Check if folder exists
        query = f"mimeType='application/vnd.google-apps.folder' and name='{name}' and '{parent_id}' in parents and trashed=false"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        
        if files:
            return files[0]['id']
        
        # Create folder
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        file = self.service.files().create(body=file_metadata, fields='id').execute()
        return file.get('id')

    def upload_file(self, filepath: str, folder_id: str) -> str:
        from googleapiclient.http import MediaFileUpload
        
        filename = os.path.basename(filepath)
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        media = MediaFileUpload(filepath, resumable=True)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    
    def upload_file_content(self, filename: str, content: str, mimetype: str, folder_id: str) -> str:
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype=mimetype, resumable=True)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

    def get_file_content(self, file_id: str) -> bytes:
        return self.service.files().get_media(fileId=file_id).execute()
