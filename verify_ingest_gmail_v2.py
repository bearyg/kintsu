import unittest
from unittest.mock import MagicMock, patch
import json
import logging
import sys
import os

# Add the function directory to path so we can import 'main'
sys.path.append(os.path.join(os.getcwd(), 'functions', 'ingest-gmail'))

# MOCK DEPENDENCIES BEFORE IMPORTING MAIN
# This allows testing the logic without installing Cloud Function dependencies locally
sys.modules['functions_framework'] = MagicMock()
# Make .http a pass-through decorator
sys.modules['functions_framework'].http.side_effect = lambda func: func

sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['google'] = MagicMock()
sys.modules['google.genai'] = MagicMock()
sys.modules['processor'] = MagicMock() # We mock local processor import too to be safe, though we patch it later

# Set env var before importing
os.environ["GEMINI_API_KEY"] = "fake_key"

# Now import main
import main as ingest_gmail_module
from main import ingest_gmail

class MockRequest:
    def __init__(self, json_data):
        self._json = json_data
    
    def get_json(self, silent=True):
        return self._json

class TestIngestGmail(unittest.TestCase):

    @patch('main.genai.Client')
    @patch('main.GmailProcessor')
    def test_ingest_gmail_flow(self, MockGmailProcessor, MockGenaiClient):
        # Setup Mocks
        
        # 1. Firestore (Configure the existing global 'db' mock)
        mock_db = ingest_gmail_module.db
        mock_collection = mock_db.collection.return_value
        mock_doc_ref = mock_collection.document.return_value
        # Simulate shard does not exist yet
        mock_doc_snapshot = MagicMock()
        mock_doc_snapshot.exists = False
        mock_doc_ref.get.return_value = mock_doc_snapshot
        
        # 2. GenAI
        mock_genai_client = MockGenaiClient.return_value
        mock_model_response = MagicMock()
        mock_model_response.text = '```json\n{"item_name": "Test Item", "total_amount": 10.00}\n```'
        mock_genai_client.models.generate_content.return_value = mock_model_response
        
        # 3. Gmail Processor
        mock_processor = MockGmailProcessor.return_value
        mock_processor.search_emails.return_value = ['msg1']
        mock_processor.get_email_details.return_value = {'id': 'msg1'}
        mock_processor.extract_metadata.return_value = {
            'subject': 'Order Confirmed', 'from': 'amazon.com', 'date': '2026-01-01'
        }
        mock_processor.parse_body.return_value = "This is a long enough body text to trigger analysis... " * 5

        # Run Function
        req_data = {
            'access_token': 'fake_token',
            'debug_mode': True,
            'trace_id': 'test-trace-123'
        }
        req = MockRequest(req_data)
        
        # We need to force the module to use our mock client if it was already initialized
        with patch('main.client', mock_genai_client):
             response = ingest_gmail(req)
        
        # Assertions
        self.assertEqual(response['status'], 'success')
        self.assertEqual(response['processed_count'], 1)
        
        # Verify GenAI was called
        mock_genai_client.models.generate_content.assert_called()
        call_args = mock_genai_client.models.generate_content.call_args
        self.assertEqual(call_args.kwargs['model'], 'gemini-2.5-pro')
        
        # Verify Firestore save
        mock_doc_ref.set.assert_called()
        saved_data = mock_doc_ref.set.call_args[0][0]
        self.assertEqual(saved_data['sourceType'], 'Gmail')
        self.assertEqual(saved_data['extractedData']['item_name'], 'Test Item')

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
