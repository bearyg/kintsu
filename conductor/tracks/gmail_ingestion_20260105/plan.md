# Plan: Gmail Integration for Automated Data Ingestion

## Phase 1: Authentication and Scope Expansion
- [ ] Task: Update OAuth scopes in frontend and backend to include Gmail readonly access.
- [ ] Task: Update `DriveService.ts` to request new scope.
- [ ] Task: Verify token refresh logic handles the additional scope.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Authentication' (Protocol in workflow.md)

## Phase 2: Gmail Client and Search Logic
- [ ] Task: Create `backend/processors/gmail.py` for Gmail-specific logic.
- [ ] Task: Write Tests: Verify Gmail search query construction.
- [ ] Task: Implement Feature: `GmailProcessor.search_emails` using Google API.
- [ ] Task: Write Tests: Verify email metadata extraction (sender, date, subject).
- [ ] Task: Implement Feature: `GmailProcessor.get_email_details`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Discovery' (Protocol in workflow.md)

## Phase 3: Content Extraction and Parsing
- [ ] Task: Write Tests: Verify attachment extraction for PDF/Image.
- [ ] Task: Implement Feature: `GmailProcessor.extract_attachments`.
- [ ] Task: Write Tests: Verify email body parsing for key financial data.
- [ ] Task: Implement Feature: `GmailProcessor.parse_body`.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Extraction' (Protocol in workflow.md)

## Phase 4: Integration with Pipeline
- [ ] Task: Update `backend/main.py` to support Gmail ingestion trigger.
- [ ] Task: Integrate `GmailProcessor` output into Firestore `shards` collection.
- [ ] Task: Update UI to add "Scan Gmail" button.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Full Integration' (Protocol in workflow.md)
