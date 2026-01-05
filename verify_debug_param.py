import asyncio
from backend.main import refine_drive_file, RefineRequest
from fastapi import BackgroundTasks

# Mock BackgroundTasks
class MockBackgroundTasks(BackgroundTasks):
    def add_task(self, func, *args, **kwargs):
        print(f"Task added: {func.__name__} with args: {args}")

async def test_debug_param():
    print("Testing ?debug=on...")
    req = RefineRequest(
        file_id="123", 
        fileName="test.zip", 
        access_token="token", 
        source_type="Amazon", 
        debug_mode=False # Default in body is False
    )
    
    mock_bg = MockBackgroundTasks()
    
    # Simulate request with query param debug='on'
    response = await refine_drive_file(req, mock_bg, debug="on")
    
    print(f"Response: {response}")
    
    # Check if the modified request inside the function (which is passed to background task) has debug_mode=True
    # The 'req' object is mutable, so let's check if it was mutated in place.
    if req.debug_mode:
        print("✅ SUCCESS: debug='on' query param correctly enabled debug_mode.")
    else:
        print("❌ FAILURE: debug_mode remained False.")

    # Test 'true' case
    print("\nTesting ?debug=true...")
    req.debug_mode = False
    await refine_drive_file(req, mock_bg, debug="true")
    if req.debug_mode:
        print("✅ SUCCESS: debug='true' query param correctly enabled debug_mode.")
    else:
        print("❌ FAILURE: debug_mode remained False.")

    # Test without param
    print("\nTesting no debug param...")
    req.debug_mode = False
    await refine_drive_file(req, mock_bg, debug=None)
    if not req.debug_mode:
        print("✅ SUCCESS: No debug param kept debug_mode as False.")
    else:
        print("❌ FAILURE: debug_mode was incorrectly enabled.")

if __name__ == "__main__":
    asyncio.run(test_debug_param())
