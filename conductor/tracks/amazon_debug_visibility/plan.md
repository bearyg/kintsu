# Plan: Amazon Filtering Debug Visibility

## Phase 1: Base Processor Refactor
- [ ] Task: Update `BaseProcessor.process` signature.
    - **Details:** Change return type hint and docstring. It should support returning extra debug info. To avoid breaking everything immediately, we can make it return `(shards, debug_info)`.
    - **File:** `backend/processors/base.py`

## Phase 2: Amazon Processor Update
- [ ] Task: Update `AmazonProcessor.process` to collect excluded items.
    - **Details:**
        1. Accept `debug=False` kwarg.
        2. Initialize `excluded = []`.
        3. When `continue` is hit (returns, price, keywords), append to `excluded` with reason.
        4. Include `order_id` in valid shards.
        5. Return `(shards, excluded)`.
    - **File:** `backend/processors/amazon.py`

## Phase 3: Main Pipeline Integration
- [ ] Task: Update `process_drive_file_background` in `main.py`.
    - **Details:**
        1. Handle the new tuple return from `processor.process`.
        2. If `req.debug_mode` is True, iterate over `excluded` items.
        3. Save excluded items to a new Firestore collection `debug_excluded_items`.
        4. Ensure `order_id` is saved with valid shards.
    - **File:** `backend/main.py`

## Phase 4: Verification
- [ ] Task: Verify with `verify_amazon_filter.py`.
    - **Details:** Update the verification script to call `process` with `debug=True` and assert that "Returned Item" appears in the excluded list with the correct reason.
    - **File:** `verify_amazon_filter.py`
