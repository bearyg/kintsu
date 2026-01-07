# Specification: True BYOS (Bring Your Own Storage) & Zero-Retention Refactor

## Overview
This track refactors the Kintsu data pipeline to align with the Privacy Policy: "We do not maintain or store information regarding the contents of your original files outside of the processing time." Currently, Firestore stores extracted PII (item names, amounts). This implementation will move all persistent "Golden Record" data to the user's Google Drive.

## Goals
- **Privacy Compliance:** Remove PII and financial extraction results from Firestore.
- **Data Sovereignty:** Use Google Drive as the primary and only persistent store for extracted data.
- **Evidence Persistence:** Ensure Gmail extractions are backed by physical artifacts (PDF/HTML) in Drive.

## Functional Requirements
1.  **Hybrid Output Format:** 
    - For every file in the Hopper, generate a `.kintsu.json` sidecar file in a hidden or specific sub-folder containing the Gemini extraction results.
    - Maintain an aggregated `Kintsu_Inventory` (Excel or Google Sheets) in the root of the Kintsu folder that is updated as files are processed.
2.  **Pointer-Only Firestore:**
    - Refactor `shards` collection to store only: `id`, `file_id`, `source_type`, `status`, `createdAt`, and `refinedAt`.
    - Remove `extractedData` field from Firestore.
    - Firestore acts solely as a real-time event signaling mechanism (pub/sub for the UI).
3.  **Asynchronous UI Pattern:**
    - The UI receives status updates (e.g., "Refined") via Firestore listeners.
    - The UI fetches the actual data (JSON sidecar) from Drive *only* when the user drills down or requests the view, accepting the inherent latency of Drive API calls.
    - The experience is "Fire and Return": User drops files, sees "Processing..." status, can leave, and comes back to find the data in their Drive.
4.  **Gmail Synthetic Artifacts:**
    - The Gmail Ingest function will save the email body as a PDF/HTML file into `Hopper/Gmail/` before processing.
    - This file will then trigger the standard `ingest-shard` flow, creating a sidecar JSON.

## Technical Constraints
- **Performance:** UI must handle the latency of fetching JSON files from Google Drive on-demand. Implement caching or batch-reading if possible.
- **Concurrency:** Ensure the aggregated master spreadsheet handles concurrent updates from multiple cloud function triggers safely.

## Acceptance Criteria
- Firestore contains no item names, prices, or merchant details.
- Deleting the Firestore "shard" record does not delete the extracted data from Google Drive.
- Users can see their extraction results in a spreadsheet in their own Google Drive.
- "Scan Gmail" results in a new file in Drive + a corresponding extraction record.
