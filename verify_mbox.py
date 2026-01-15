import asyncio
import os
import logging
import sys

# Add backend to path so we can import processors
sys.path.append(os.path.abspath("backend"))

from backend.processors.mbox_processor import MboxProcessor

# Mock Drive Service
class MockDriveService:
    async def ensure_folder(self, name, parent_id):
        print(f"[MockDrive] ensure_folder: name='{name}', parent_id='{parent_id}'")
        return "mock_folder_id"
    
    async def upload_file_content(self, filename, content, mimetype, folder_id):
        print(f"[MockDrive] upload_file_content: filename='{filename}', folder_id='{folder_id}'")
        print(f"--- Content Preview (First 500 chars) ---\n{content[:500]}\n-----------------------------------------")
        return "mock_file_id"

async def main():
    # Setup
    test_file = "/Users/bearyg/Documents/GitHub/kintsu/gdrive_Kintsu_design/gmail data/takeout-20260109T213326Z-3-001.zip"
    
    if not os.path.exists(test_file):
        print(f"Error: Test file not found at {test_file}")
        return

    print(f"Starting verification with file: {test_file}")
    
    mock_drive = MockDriveService()
    processor = MboxProcessor(mock_drive)
    
    # We need a valid API KEY for this to work effectively, otherwise Gemini calls fail
    # Assuming it's in env or we might need to mock Gemini if we just want to test MBOX parsing
    if not os.getenv("GEMINI_API_KEY"):
         print("WARNING: GEMINI_API_KEY not found in env. Gemini calls might fail or need mocking if not handled.")

    try:
        await processor.process_file(test_file, "root_folder_id")
        print("Verification Successful!")
    except Exception as e:
        print(f"Verification Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
