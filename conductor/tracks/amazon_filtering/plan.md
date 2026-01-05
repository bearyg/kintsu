# Amazon Filtering Plan

## Phase 1: Context Awareness
- [x] Task: Refactor `AmazonProcessor.process` to accept `context` (sibling files).
    - **Details:** The `process` method currently takes a single file path. We need to pass the directory of the unzipped archive or a map of available files so it can "look around" for the Returns CSV.
    - **File:** `backend/processors/amazon.py` & `backend/processors/base.py`

## Phase 2: Returns Parsing
- [x] Task: Implement `parse_returns_csv` helper.
    - **Details:** Add a method to `AmazonProcessor` that reads `Retail.OrdersReturned.1.csv` and returns a Set of `OrderID` strings.
    - **File:** `backend/processors/amazon.py`

## Phase 3: Integration & Filtering
- [x] Task: Integrate Returns logic into the main processing loop.
    - **Details:** 
        1. In `process`, check if the returns file exists in the provided context/directory.
        2. If yes, call `parse_returns_csv`.
        3. In the row iteration loop, check `row['Order ID']` against the returned set.
        4. If matched, `continue` (skip) and log.
    - **File:** `backend/processors/amazon.py`

## Phase 4: Integration with Main Pipeline
- [x] Task: Update `process_drive_file_background` in `main.py`.
    - **Details:** When handling a ZIP file, identify the specific Amazon files. Instead of processing them in isolation, detect the "Amazon Dump" pattern and pass the full context to the `AmazonProcessor`.
    - **File:** `backend/main.py`

## Phase 5: Verification
- [x] Task: Verify with provided sample data.
    - **Details:** Run the processor against the `Retail.OrderHistory` and ensure items with IDs from `Retail.OrdersReturned` are NOT in the output shards.
