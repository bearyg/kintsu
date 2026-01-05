import unittest
from unittest.mock import MagicMock, patch
from backend.processors.gmail import GmailProcessor

class TestGmailProcessor(unittest.TestCase):
    @patch('backend.processors.gmail.build')
    @patch('backend.processors.gmail.Credentials')
    def test_search_emails(self, mock_creds, mock_build):
        # Setup mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_list = mock_service.users().messages().list()
        mock_list.execute.return_value = {
            'messages': [{'id': 'msg123'}, {'id': 'msg456'}]
        }

        processor = GmailProcessor(access_token="fake_token")
        results = processor.search_emails(query="from:amazon.com")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], 'msg123')
        mock_service.users().messages().list.assert_called_with(
            userId='me', q='from:amazon.com', maxResults=10
        )
        print("✅ test_search_emails passed")

    @patch('backend.processors.gmail.build')
    @patch('backend.processors.gmail.Credentials')
    def test_get_email_details(self, mock_creds, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_get = mock_service.users().messages().get()
        mock_get.execute.return_value = {
            'id': 'msg123',
            'snippet': 'Your Amazon Order',
            'payload': {
                'headers': [{'name': 'Subject', 'value': 'Order Confirmation'}]
            }
        }

        processor = GmailProcessor(access_token="fake_token")
        details = processor.get_email_details('msg123')

        self.assertEqual(details['id'], 'msg123')
        self.assertEqual(details['snippet'], 'Your Amazon Order')
        print("✅ test_get_email_details passed")

    @patch('backend.processors.gmail.build')
    @patch('backend.processors.gmail.Credentials')
    def test_parse_body(self, mock_creds, mock_build):
        # Mocking body parsing (Base64 encoded "Hello World")
        import base64
        encoded_body = base64.urlsafe_b64encode(b"Hello World").decode('utf-8')
        
        message = {
            'payload': {
                'parts': [
                    {
                        'mimeType': 'text/plain',
                        'body': {'data': encoded_body}
                    }
                ]
            }
        }

        processor = GmailProcessor(access_token="fake_token")
        body = processor.parse_body(message)

        self.assertEqual(body, "Hello World")
        print("✅ test_parse_body passed")

    def test_extract_metadata(self):
        message = {
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'Amazon.com <auto-confirm@amazon.com>'},
                    {'name': 'Date', 'value': 'Mon, 5 Jan 2026 12:00:00 +0000'},
                    {'name': 'Subject', 'value': 'Your Amazon.com order'}
                ]
            }
        }
        
        processor = GmailProcessor(access_token="fake_token")
        metadata = processor.extract_metadata(message)
        
        self.assertEqual(metadata['from'], 'Amazon.com <auto-confirm@amazon.com>')
        self.assertEqual(metadata['subject'], 'Your Amazon.com order')
        print("✅ test_extract_metadata passed")

    @patch('backend.processors.gmail.build')
    @patch('backend.processors.gmail.Credentials')
    def test_extract_attachments(self, mock_creds, mock_build):
        import base64
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Mock attachment response
        mock_attachment_data = base64.urlsafe_b64encode(b"FAKE_PDF_CONTENT").decode('utf-8')
        mock_get = mock_service.users().messages().attachments().get()
        mock_get.execute.return_value = {'data': mock_attachment_data}

        processor = GmailProcessor(access_token="fake_token")
        
        part = {
            'body': {'attachmentId': 'attach123'},
            'filename': 'receipt.pdf'
        }
        
        data = processor.extract_attachments('msg123', part)
        
        self.assertEqual(data, b"FAKE_PDF_CONTENT")
        mock_service.users().messages().attachments().get.assert_called_with(
            userId='me', messageId='msg123', id='attach123'
        )
        print("✅ test_extract_attachments passed")

if __name__ == '__main__':
    unittest.main()
