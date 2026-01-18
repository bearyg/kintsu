from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import logging
from drive_client import DriveServiceWrapper
from reporting.exporter import ReportExporter

router = APIRouter()
logger = logging.getLogger(__name__)

class ReportRequest(BaseModel):
    folderId: str
    reportName: str
    formats: List[str] = ['pdf', 'csv', 'zip']
    accessToken: str

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
