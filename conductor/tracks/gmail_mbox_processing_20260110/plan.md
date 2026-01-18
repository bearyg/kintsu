# Plan: Gmail MBOX Processing & Extraction

This plan implements the extraction of individual emails from MBOX files into `.eml` and `.html` formats, followed by Gemini-powered inventory extraction.

## Phase 1: Preparation & Utilities
Focus: Establish foundational utilities for sanitization, logging, and environment setup.

- [ ] Task: Create `backend/workers/mbox/utils.py` with `sanitize_filename` function (handling `Message-ID` to filesystem-safe strings).
- [ ] Task: Create `backend/workers/mbox/logger.py` for handling the `processing_log.json` lifecycle on Google Drive.
- [ ] Task: Write unit tests for `sanitize_filename` and log utility.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Preparation & Utilities' (Protocol in workflow.md)

## Phase 2: MBOX Iteration & Hybrid Storage
Focus: Update the MBOX worker to iterate through messages and save the hybrid `.eml` and `.html` files.

- [ ] Task: Implement `EmailProcessor` class to extract `.eml` (raw) and `.html` (rendered body) from a `mailbox.Message`.
- [ ] Task: Integrate `EmailProcessor` into `backend/workers/mbox/main.py`.
- [ ] Task: Implement "Skip if exists" logic using GCS `blob.exists()`.
- [ ] Task: Update the output directory structure to `Hopper/gmail/extract_<zip_name>/`.
- [ ] Task: Write tests for `EmailProcessor` using a sample MBOX file.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: MBOX Iteration & Hybrid Storage' (Protocol in workflow.md)

## Phase 3: Gemini Inventory Extraction
Focus: Integrate Gemini to parse the extracted emails and save inventory data as JSON.

- [ ] Task: Define the Gemini prompt and JSON schema for inventory extraction (Item, Transaction, Vendor, Evidence).
- [ ] Task: Implement `InventoryExtractor` using Vertex AI / Gemini Pro.
- [ ] Task: Add task to `EmailProcessor` to trigger `InventoryExtractor` for each new (non-skipped) email.
- [ ] Task: Save resulting JSON to `<base_name>.json` in the extraction folder.
- [ ] Task: Write tests for `InventoryExtractor` with mocked Gemini responses.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Gemini Inventory Extraction' (Protocol in workflow.md)

## Phase 4: Logging & Final Integration
Focus: Ensure the processing log is correctly updated and the end-to-end flow is robust.

- [ ] Task: Implement final tallying and summary generation in `processing_log.json`.
- [ ] Task: Ensure errors during individual email processing are caught and logged without crashing the entire job.
- [ ] Task: Verify end-to-end flow with a real (or large sample) MBOX file.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Logging & Final Integration' (Protocol in workflow.md)
