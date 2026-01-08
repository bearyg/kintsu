# Plan: Research Spike - Google Takeout Feasibility

## Phase 1: API & Automation Research [checkpoint: 75064d9]
- [x] Task: Investigate official Google Data Portability & Takeout APIs.
    - [x] Sub-task: Research the "Google Data Portability API" (specifically `portability.google.com`) for direct programmatic access to exports.
    - [x] Sub-task: Check Google Cloud documentation for "Data Transfer Project" integration and service-to-service transfer capabilities.
    - [x] Sub-task: Search for "deep linking" capabilities in the Google Takeout web interface (e.g., pre-filling checkboxes or query strings via URL parameters).
- [x] Task: Investigate "Browser Automation" & User-Side Helpers.
    - [x] Sub-task: Evaluate if a simple "Bookmarklet" or Browser Extension could automate the form-filling (selecting Mail, entering the query string).
- [x] Task: Document findings in `research_takeout_automation.md` (to be created in the track directory).
- [ ] Task: Conductor - User Manual Verification 'Phase 1: API & Automation Research' (Protocol in workflow.md)

## Phase 2: Mbox Parsing Proof-of-Concept [checkpoint: 83e7e58]
- [x] Task: Create a directory `research/takeout_poc/` for the prototype.
- [x] Task: Write a Python script (`parser.py`) to read a standard `.mbox` file.
    - [x] Sub-task: Use the native `mailbox` library.
    - [x] Sub-task: Implement iteration over messages.
- [x] Task: Implement "Extraction Logic" in the script.
    - [x] Sub-task: Extract Subject, From, Date, and HTML Body from a message.
    - [x] Sub-task: Verify it handles "multipart" messages correctly (like our existing Gmail processor).
- [x] Task: Test against a sample Mbox file (create a dummy one if needed).
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Mbox Parsing PoC' (Protocol in workflow.md)

## Phase 3: Synthesis & Recommendation
- [x] Task: Compile the "Feasibility Report" combining API findings and Parser results.
- [x] Task: Update the `spec.md` or create a new "Proposal" document with the Go/No-Go decision.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Final Recommendation' (Protocol in workflow.md)
