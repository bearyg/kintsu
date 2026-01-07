import pytest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage_adapter import DriveStorageAdapter

@pytest.fixture
def mock_drive_service():
    with patch('storage_adapter.build') as mock_build:
        with patch('storage_adapter.google.auth.default') as mock_auth:
            mock_auth.return_value = (MagicMock(), "project-id")
            service = MagicMock()
            mock_build.return_value = service
            yield service

def test_drive_adapter_init(mock_drive_service):
    adapter = DriveStorageAdapter()
    assert adapter.service == mock_drive_service

def test_create_file_folder(mock_drive_service):
    adapter = DriveStorageAdapter()
    
    mock_files = mock_drive_service.files.return_value
    mock_files.create.return_value.execute.return_value = {'id': 'folder_id'}
    
    # Test folder creation (mimeType logic)
    res = adapter.create_file("Folder", "root", "", "application/vnd.google-apps.folder")
    assert res['id'] == 'folder_id'
    
    # Verify NO media_body was passed
    call_kwargs = mock_files.create.call_args[1]
    assert 'media_body' not in call_kwargs
