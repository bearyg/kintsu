# Plan: Gmail Integration Debugging & Diagnostics

## Context
The initial Gmail integration deployment (V_0_0_1b) resulted in successful HTTP 200 responses but no visible processing side effects or application logs in the production environment. The goal is to improve observability, specifically when `debug=on` is used, to identify why the background tasks aren't producing results.

## Phase 1: Logging Infrastructure Improvement
- [x] Task: specific `logging` configuration in `backend/main.py` ensuring stdout is flushed.
- [x] Task: Wrap `process_gmail_scan_background` in a broad try/except block to catch and log startup failures.
- [x] Task: Add "heartbeat" logs at the very start of the background task.

## Phase 2: Gmail Processor Diagnostics
- [x] Task: Add detailed debug logging to `backend/processors/gmail.py` (API response sizes, specific error messages).
- [x] Task: Verify token validity check before attempting API calls.

## Phase 3: Frontend & Verification
- [x] Task: Update Frontend to pass a distinct `trace_id` if possible (optional, but good for correlating).
- [x] Task: Verify locally with `verify_gmail_processor.py` using the new logging setup.
