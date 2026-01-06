# Plan: Backend Refactoring to Microservices (Cloud Functions)

## Goals
- Decouple specialized processors (Amazon, Gmail) from the main backend monolith.
- Deploy each processor as an independent Google Cloud Function.
- Update the main backend to orchestrate these functions.

## Phase 1: Shared Library Strategy
- [x] Task: Create `functions/common` directory. (Skipped: Decided on self-contained functions for simplicity)
- [x] Task: Move `backend/processors/base.py` to `functions/common/base_processor.py`. (Skipped)
- [x] Task: Copy/Vendor necessary utils (Firestore logic if needed) to `functions/common`. (Implemented: Inline or duplicated for independence)

## Phase 2: Amazon Processor Function
- [x] Task: Create `functions/processor-amazon`.
- [x] Task: Move `backend/processors/amazon.py` logic to `functions/processor-amazon/main.py`.
- [x] Task: Create `functions/processor-amazon/requirements.txt`.
- [x] Task: Ensure it accepts HTTP requests (or Pub/Sub events) with file references.

## Phase 3: Gmail Processor Function
- [x] Task: Create `functions/ingest-gmail`.
- [x] Task: Move `backend/processors/gmail.py` logic to `functions/ingest-gmail/main.py`.
- [x] Task: Create `functions/ingest-gmail/requirements.txt`.
- [x] Task: Ensure it accepts HTTP requests with Access Token and Query.

## Phase 4: Orchestrator Update
- [x] Task: Update `backend/main.py` to remove local processor imports.
- [x] Task: Implement HTTP clients in `backend/main.py` to call the new Cloud Function URLs.
- [x] Task: Update `cloudbuild.yaml` to deploy the new functions.

## Phase 5: Verification
- [ ] Task: Deploy and verify `scan-gmail` flows through the new function.
- [ ] Task: Deploy and verify `refine-drive-file` flows through the Amazon function.