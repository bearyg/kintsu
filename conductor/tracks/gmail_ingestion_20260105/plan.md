# Plan: Gmail Integration for Automated Data Ingestion

## Phase 1: Authentication and Scope Expansion
- [x] Task: Update OAuth scopes in frontend and backend to include Gmail readonly access.
- [x] Task: Update `DriveService.ts` to request new scope.
- [x] Task: Verify token refresh logic handles the additional scope.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Authentication' (Protocol in workflow.md)

## Phase 2: Gmail Client and Search Logic
- [x] Task: Create `backend/processors/gmail.py` for Gmail-specific logic.
- [x] Task: Write Tests: Verify Gmail search query construction.
- [x] Task: Implement Feature: `GmailProcessor.search_emails` using Google API.
- [x] Task: Write Tests: Verify email metadata extraction (sender, date, subject).
- [x] Task: Implement Feature: `GmailProcessor.get_email_details`.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Discovery' (Protocol in workflow.md)

## Phase 3: Content Extraction and Parsing
- [x] Task: Write Tests: Verify attachment extraction for PDF/Image.
- [x] Task: Implement Feature: `GmailProcessor.extract_attachments`.
- [x] Task: Write Tests: Verify email body parsing for key financial data.
- [x] Task: Implement Feature: `GmailProcessor.parse_body`.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Extraction' (Protocol in workflow.md)

## Phase 4: Integration with Pipeline
- [x] Task: Update `backend/main.py` to support Gmail ingestion trigger.
- [x] Task: Integrate `GmailProcessor` output into Firestore `shards` collection.
- [x] Task: Update UI to add "Scan Gmail" button.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Full Integration' (Protocol in workflow.md)