# Plan: Google Takeout Ingestion Pipeline

## Phase 0: Deprecation & Cleanup [checkpoint: 68fe139]
- [x] Task: Remove `gmail.readonly` scope from the OAuth configuration (Frontend & Backend).
- [x] Task: Deprecate/Remove the old `ingest-gmail` Cloud Function (direct API access).
- [x] Task: Clean up Frontend: Remove "Connect Gmail" buttons/flows that relied on the old method.
- [ ] Task: Conductor - User Manual Verification 'Phase 0: Deprecation' (Protocol in workflow.md)

## Phase 1: Architecture & Asynchronous Job Infrastructure
- [x] Task: Create `JobService` (Backend) to manage async processing jobs.
    - [x] Sub-task: Define Firestore schema for `jobs` collection (status, progress, debug logs).
    - [x] Sub-task: Implement `create_job` endpoint (generates Signed URL for GCS upload).
- [x] Task: Configure Pub/Sub trigger for "File Uploaded" events to decouple upload from processing.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Architecture' (Protocol in workflow.md)

## Phase 2: Backend Mbox Worker (Cloud Run)
- [x] Task: Create `worker-mbox` Cloud Run service.
    - [x] Sub-task: Implement the Mbox streaming parser (based on PoC).
    - [x] Sub-task: Integrate with `JobService` to update status/progress.
    - [x] Sub-task: Implement `debug=on` logic for verbose logging.
- [x] Task: Implement Extraction & BYOS Logic.
    - [x] Sub-task: Integrate with `GmailProcessor` (or similar) to format email for Gemini.
    - [x] Sub-task: Use `DriveStorageAdapter` to write artifacts to User Drive (`Hopper/Gmail/`).
    - [x] Sub-task: Implement Deduplication logic (check `Message-ID`).
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Mbox Worker' (Protocol in workflow.md)

## Phase 3: Frontend "Takeout Wizard"
- [x] Task: Create `TakeoutWizard` React component.
    - [x] Sub-task: Step 1 & 2: Static instructions for Labeling & Exporting (with screenshots).
    - [x] Sub-task: Step 3: Drag-and-Drop Upload (using Signed URL from Phase 1).
- [x] Task: Create `JobStatus` component.
    - [x] Sub-task: Poll (or listen to) `jobs` collection for progress updates.
    - [x] Sub-task: Display "Console" log if `debug=on` was requested.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Frontend Wizard' (Protocol in workflow.md)

## Phase 4: Integration & Cleanup
- [x] Task: Implement Automatic Cleanup.
    - [x] Sub-task: Ensure Worker deletes the raw GCS file upon Job completion (Success or Failure).
- [x] Task: End-to-End Testing.
    - [x] Sub-task: Verify flow: User Uploads -> Async Job Starts -> Worker Extracts -> Drive Updated -> UI Shows Success.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Final Validation' (Protocol in workflow.md)
