import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage import DriveStorageAdapter

@pytest.fixture
def mock_drive_service():
    with patch('storage.build') as mock_build:
        with patch('storage.google.auth.default') as mock_auth:
            mock_auth.return_value = (MagicMock(), "project-id")
            service = MagicMock()
            mock_build.return_value = service
            yield service

def test_drive_adapter_init(mock_drive_service):
    adapter = DriveStorageAdapter()
    assert adapter.service == mock_drive_service

def test_list_files(mock_drive_service):
    adapter = DriveStorageAdapter()
    
    # Mock response
    mock_files = mock_drive_service.files.return_value
    mock_files.list.return_value.execute.side_effect = [
        {'files': [{'id': '1', 'name': 'test', 'size': '100', 'mimeType': 'text/plain'}]},
        {'files': []} # End of pages
    ]
    
    results = adapter.list_files("root")
    assert len(results) == 1
    assert results[0]['name'] == 'test'
    assert results[0]['path'] == '1'

def test_create_file(mock_drive_service):
    adapter = DriveStorageAdapter()
    
    mock_files = mock_drive_service.files.return_value
    mock_files.create.return_value.execute.return_value = {'id': 'new_id'}
    
    res = adapter.create_file("test.txt", "root", "content")
    assert res['id'] == 'new_id'
    mock_files.create.assert_called_once()
