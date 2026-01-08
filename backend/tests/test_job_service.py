import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from job_service import JobService

@pytest.fixture
def mock_firestore():
    with patch('job_service.db') as mock_db:
        yield mock_db

@pytest.fixture
def mock_storage():
    with patch('job_service.storage_client') as mock_storage:
        yield mock_storage

def test_create_job(mock_firestore, mock_storage):
    service = JobService("test-bucket")
    
    # Mock Blob
    mock_blob = MagicMock()
    mock_blob.generate_signed_url.return_value = "https://signed.url"
    mock_storage.bucket.return_value.blob.return_value = mock_blob
    
    result = service.create_job("user123", "test.mbox")
    
    assert "jobId" in result
    assert result["uploadUrl"] == "https://signed.url"
    assert "gcsPath" in result
    
    # Verify Firestore write
    mock_firestore.collection.return_value.document.return_value.set.assert_called_once()

def test_update_progress(mock_firestore, mock_storage):
    service = JobService("test-bucket")
    
    service.update_progress("job1", 50, "processing", "Starting...")
    
    mock_firestore.collection.return_value.document.return_value.update.assert_called_once()
