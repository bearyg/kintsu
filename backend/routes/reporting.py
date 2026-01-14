from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from ..reporting.exporter import ReportExporter

router = APIRouter()
logger = logging.getLogger(__name__)

class ReportRequest(BaseModel):
    folderId: str
    reportName: str
    formats: List[str] = ['pdf', 'csv', 'zip']
    accessToken: str

class DriveServiceWrapper:
    def __init__(self, access_token):
        creds = Credentials(token=access_token)
        self.service = build('drive', 'v3', credentials=creds)

    async def ensure_folder(self, name: str, parent_id: str) -> str:
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

    async def upload_file(self, filepath: str, folder_id: str) -> str:
        from googleapiclient.http import MediaFileUpload
        import os
        
        filename = os.path.basename(filepath)
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        media = MediaFileUpload(filepath, resumable=True)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

@router.post("/api/reports/generate")
async def generate_report(req: ReportRequest, background_tasks: BackgroundTasks):
    """
    Initiates report generation.
    """
    try:
        drive_service = DriveServiceWrapper(req.accessToken)
        exporter = ReportExporter(drive_service)
        
        # Run synchronously for now to keep it simple, or move to background task if heavy
        # For a "real" implementation, this should be a background task that updates firestore status
        
        result = await exporter.generate_report(req.folderId, req.reportName, req.formats)
        return {"status": "success", "files": result}

    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
