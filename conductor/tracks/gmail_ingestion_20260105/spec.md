# Specification: Gmail Integration for Automated Data Ingestion

## Overview
This track enables Kintsu to automatically ingest financial data (receipts, order confirmations, invoices) directly from a user's Gmail account. This reduces manual effort and ensures a more complete "Hopper" for forensic reconstruction.

## Goals
- Connect to Gmail via OAuth2 (using existing Google infrastructure).
- Search for and identify relevant emails based on keywords and sender patterns.
- Extract email content (body and attachments).
- Feed extracted data into the refinery pipeline (similar to how Amazon CSVs are processed).

## Functional Requirements
- **OAuth Scopes:** Add `https://www.googleapis.com/auth/gmail.readonly` to the requested scopes.
- **Email Discovery:** Implement a search mechanism to find emails from known merchants (e.g., Amazon, Apple, Uber, etc.).
- **Content Extraction:** Handle both HTML/Plain text bodies and common attachment types (PDF, Images).
- **Refinery Integration:** Convert email data into "shards" for Firestore, similar to the existing processing flow.

## Technical Constraints
- Must use existing `google-api-python-client` and `google-auth`.
- Backend processing should happen in the "Refinery" (Python/FastAPI).
- Respect Gmail API rate limits.

## Acceptance Criteria
- User can trigger a Gmail scan from the UI.
- Relevant emails are identified and processed into shards.
- Shards appear in the "Refinery Stream" in the UI.
- No sensitive or irrelevant personal emails are ingested.
