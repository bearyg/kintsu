# Plan: Research Spike - Google Takeout Feasibility

## Phase 1: API & Automation Research
- [ ] Task: Investigate official Google Data Portability & Takeout APIs.
    - [ ] Sub-task: Research the "Google Data Portability API" (specifically `portability.google.com`) for direct programmatic access to exports.
    - [ ] Sub-task: Check Google Cloud documentation for "Data Transfer Project" integration and service-to-service transfer capabilities.
    - [ ] Sub-task: Search for "deep linking" capabilities in the Google Takeout web interface (e.g., pre-filling checkboxes or query strings via URL parameters).
- [ ] Task: Investigate "Browser Automation" & User-Side Helpers.
    - [ ] Sub-task: Evaluate if a simple "Bookmarklet" or Browser Extension could automate the form-filling (selecting Mail, entering the query string).
- [ ] Task: Document findings in `research_takeout_automation.md` (to be created in the track directory).
- [ ] Task: Conductor - User Manual Verification 'Phase 1: API & Automation Research' (Protocol in workflow.md)

## Phase 2: Mbox Parsing Proof-of-Concept
- [ ] Task: Create a directory `research/takeout_poc/` for the prototype.
- [ ] Task: Write a Python script (`parser.py`) to read a standard `.mbox` file.
    - [ ] Sub-task: Use the native `mailbox` library.
    - [ ] Sub-task: Implement iteration over messages.
- [ ] Task: Implement "Extraction Logic" in the script.
    - [ ] Sub-task: Extract Subject, From, Date, and HTML Body from a message.
    - [ ] Sub-task: Verify it handles "multipart" messages correctly (like our existing Gmail processor).
- [ ] Task: Test against a sample Mbox file (create a dummy one if needed).
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Mbox Parsing PoC' (Protocol in workflow.md)

## Phase 3: Synthesis & Recommendation
- [ ] Task: Compile the "Feasibility Report" combining API findings and Parser results.
- [ ] Task: Update the `spec.md` or create a new "Proposal" document with the Go/No-Go decision.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Final Recommendation' (Protocol in workflow.md)
