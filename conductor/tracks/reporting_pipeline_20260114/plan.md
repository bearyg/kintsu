# Implementation Plan - Reporting & Data Review Pipeline

## Phase 1: Data Review UI Foundation (Skill: UI/UX Pro Max)
This phase establishes the consistent "Hopper" review interface for all data types.

- [ ] Task: Create Universal "Hopper" List View Component
    - [ ] Create `components/Hopper/HopperList.tsx` for displaying files/folders.
    - [ ] Implement folder navigation logic (breadcrumbs, up one level).
    - [ ] Add "Quick Actions" sidebar support (layout structure).
    - [ ] Add diagnostic logging for all file list operations (`/?debug=on` check).
- [ ] Task: Implement HTML File Previewer
    - [ ] Create `components/Hopper/Previewers/HtmlPreview.tsx`.
    - [ ] Securely render HTML content (sanitized iframe or similar).
    - [ ] Ensure CSS isolation.
- [ ] Task: Implement JSON File Previewer
    - [ ] Create `components/Hopper/Previewers/JsonPreview.tsx`.
    - [ ] Use a collapsible tree view library or custom implementation for readability.
- [ ] Task: Implement "Review Actions" Logic
    - [ ] Implement `moveFile(fileId, destination)` service function (mocked or real Google Drive API wrapper).
    - [ ] Connect "Keep", "Exclude", "Delete" buttons to the move service.
    - [ ] Ensure "Exclude" moves to `_excluded/` and "Delete" to `_deleted/`.
    - [ ] Add comprehensive error logging for file operations.
- [ ] Task: Conductor - User Manual Verification 'Data Review UI Foundation' (Protocol in workflow.md)

## Phase 2: AI Data Refinement (Skill: AI Pro Max)
This phase focuses on improving the quality of the data *before* it reaches the reporting stage.

- [ ] Task: Analyze Current Extraction Quality
    - [ ] Run analysis script on sample Amazon/Gmail data.
    - [ ] Identify common "noise" patterns (headers, footers, ads).
    - [ ] Document findings in `research/noise_analysis.md`.
- [ ] Task: Refine Extraction/Filtering Logic
    - [ ] Update `backend/processors/` logic based on findings.
    - [ ] Implement stricter filtering rules or updated AI prompts.
    - [ ] Verify improvement with `verify_amazon_filter.py` or similar scripts.
- [ ] Task: Conductor - User Manual Verification 'AI Data Refinement' (Protocol in workflow.md)

## Phase 3: Reporting Engine (Skill: Senior Fullstack)
This phase builds the final export functionality for insurance adjusters.

- [ ] Task: Research Standard Insurance Formats
    - [ ] Quick research on standard claim file formats.
    - [ ] Document decision in `conductor/tracks/reporting_pipeline/spec.md`.
- [ ] Task: Implement Export Service
    - [ ] Create `backend/reporting/exporter.py` (or similar).
    - [ ] Implement aggregation logic (collect all "Keep" files).
    - [ ] Implement PDF generation (summary report).
    - [ ] Implement ZIP generation (attachments/evidence).
    - [ ] Ensure final artifacts are saved to User's Drive.
- [ ] Task: Integrate Export UI
    - [ ] Add "Generate Report" button to the Hopper UI.
    - [ ] Handle loading states and success/error notifications.
- [ ] Task: Conductor - User Manual Verification 'Reporting Engine' (Protocol in workflow.md)
