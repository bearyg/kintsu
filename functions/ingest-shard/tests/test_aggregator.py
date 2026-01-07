import pytest
from unittest.mock import MagicMock, patch
import sys
import os
import io
import openpyxl

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aggregator import InventoryAggregator

@pytest.fixture
def mock_drive_adapter():
    return MagicMock()

def test_ensure_inventory_file_exists(mock_drive_adapter):
    agg = InventoryAggregator(mock_drive_adapter)
    
    mock_drive_adapter.find_file_by_name.return_value = {'id': 'existing_id'}
    
    res = agg.ensure_inventory_file("folder_id")
    assert res == 'existing_id'
    mock_drive_adapter.create_file.assert_not_called()

def test_ensure_inventory_file_creates_new(mock_drive_adapter):
    agg = InventoryAggregator(mock_drive_adapter)
    
    mock_drive_adapter.find_file_by_name.return_value = None
    mock_drive_adapter.create_file.return_value = {'id': 'new_id'}
    
    res = agg.ensure_inventory_file("folder_id")
    assert res == 'new_id'
    mock_drive_adapter.create_file.assert_called_once()

def test_append_item(mock_drive_adapter):
    agg = InventoryAggregator(mock_drive_adapter)
    
    # Mock existing file
    mock_drive_adapter.find_file_by_name.return_value = {'id': 'file_id'}
    
    # Mock download content (empty excel)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Header"])
    buffer = io.BytesIO()
    wb.save(buffer)
    mock_drive_adapter.download_file.return_value = buffer.getvalue()
    
    item_data = {
        "date": "2023-01-01",
        "item_name": "Test Item",
        "total_amount": 100
    }
    
    agg.append_item("folder_id", item_data, "source.jpg")
    
    # Verify update called
    mock_drive_adapter.update_file.assert_called_once()
    # verify content?
    call_args = mock_drive_adapter.update_file.call_args
    assert call_args[1]['file_id'] == 'file_id'
