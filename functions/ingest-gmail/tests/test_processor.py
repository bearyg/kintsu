import pytest
from unittest.mock import MagicMock, patch
import sys
import os
import base64

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from processor import GmailProcessor

@pytest.fixture
def mock_gmail_processor():
    with patch('processor.build'):
        with patch('processor.Credentials'):
            return GmailProcessor("fake_token")

def test_get_raw_html_simple(mock_gmail_processor):
    html_content = "<html><body>Hello</body></html>"
    encoded_content = base64.urlsafe_b64encode(html_content.encode('utf-8')).decode('utf-8')
    
    message = {
        'payload': {
            'parts': [
                {
                    'mimeType': 'text/html',
                    'body': {'data': encoded_content}
                }
            ]
        }
    }
    
    res = mock_gmail_processor.get_raw_html(message)
    assert res == html_content

def test_get_raw_html_nested(mock_gmail_processor):
    html_content = "<html><body>Nested</body></html>"
    encoded_content = base64.urlsafe_b64encode(html_content.encode('utf-8')).decode('utf-8')
    
    message = {
        'payload': {
            'parts': [
                {
                    'mimeType': 'multipart/related',
                    'parts': [
                        {
                            'mimeType': 'text/html',
                            'body': {'data': encoded_content}
                        }
                    ]
                }
            ]
        }
    }
    
    res = mock_gmail_processor.get_raw_html(message)
    assert res == html_content

def test_get_raw_html_none(mock_gmail_processor):
    message = {
        'payload': {
            'parts': [
                {
                    'mimeType': 'text/plain',
                    'body': {'data': 'some_data'}
                }
            ]
        }
    }
    
    res = mock_gmail_processor.get_raw_html(message)
    assert res == ""
