# Plan: True BYOS & Zero-Retention Refactor

## Phase 1: Storage Adapter & Artifact Generation (Backend)
- [x] Task: Create `DriveStorageAdapter` class in `backend/` and Cloud Functions to handle writing `.kintsu.json` sidecars to Drive.
- [x] Task: Implement `InventoryAggregator` logic to append extracted data to a master `Kintsu_Inventory.xlsx` in the user's Drive root.
    - [x] Sub-task: Handle locking/concurrency (or simple append-only strategy) for the master file.
- [x] Task: Refactor `ingest-shard` function to:
    1. Perform Gemini extraction.
    2. Write result to Drive (`.kintsu.json` + update `.xlsx`).
    3. Update Firestore with STATUS ONLY (no data).
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Backend Storage' (Protocol in workflow.md)

## Phase 2: Gmail Synthetic Artifacts
- [ ] Task: Update `ingest-gmail` to render email body as HTML/PDF.
- [ ] Task: Modify `ingest-gmail` to upload this artifact to `Hopper/Gmail/` instead of triggering Gemini directly.
    - *Note:* The upload to `Hopper/` should naturally trigger the `ingest-shard` GCS trigger, standardizing the flow.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Gmail Artifacts' (Protocol in workflow.md)

## Phase 3: Frontend Data Fetching Refactor
- [ ] Task: Update `DriveService.ts` to add methods for reading `.kintsu.json` sidecar files given a file ID.
- [ ] Task: Refactor `App.tsx` and data hooks:
    - Listen to Firestore for *list* of items and status.
    - When an item is "Refined", asynchronously fetch its content from Drive (lazy load).
- [ ] Task: Remove all code relying on `shard.extractedData` from Firestore.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Frontend Refactor' (Protocol in workflow.md)

## Phase 4: Cleanup & Migration
- [ ] Task: Write a script (or Cloud Function) to retroactive "purge" extracted data from existing Firestore documents (if any exist in prod).
- [ ] Task: Final end-to-end verification of the privacy promise (data in Drive, nothing in Firestore).
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Final Validation' (Protocol in workflow.md)
