# Specification: Research Spike - Google Takeout Feasibility

## 1. Overview
We need a definitive alternative to the `gmail.readonly` OAuth scope to avoid CASA Tier 2 verification. The proposed solution is utilizing Google Takeout. This track is a **Research Spike** to deeply investigate the technical feasibility of this approach, specifically looking for ways to automate, wrap, or smoothen the user experience of generating and ingesting Takeout archives.

## 2. Research Objectives

### 2.1 Takeout Automation & APIs
- **Goal:** Determine if *any* official or unofficial APIs exist to trigger or configure a Takeout export on a user's behalf.
- **Investigation:**
    - Research the **Google Data Portability API** (specifically `portability.google.com`) for direct programmatic access to exports.
    - Research the **Data Transfer Project (DTP)** integration and service-to-service transfer capabilities.
    - Research **Google Takeout API** availability for verified partners or specific use cases.
- **Outcome:** A definitive "Yes/No/Partial" on automation. If "No", define the absolute minimum number of manual steps required by the user.

### 2.2 The "Wrapper" Strategy
- **Goal:** Define the technical approach for the "Guided Wrapper."
- **Investigation:**
    - Can we link the user directly to a pre-filled Takeout configuration URL?
    - Can we use a browser extension or script to select the correct boxes for the user?
    - How do we handle the "Query String" injection (`in:anywhere ...`) into the Takeout UI?
- **Outcome:** A recommendation on the UX approach (e.g., "Deep Link Strategy" vs. "Browser Extension" vs. "UI Wizard").

### 2.3 File Handling & Parsing Proof-of-Concept
- **Goal:** Verify we can handle the data efficiently.
- **Task:** Create a simple PoC script that:
    1.  Accepts a standard Google Takeout `.mbox` or `.zip` file.
    2.  Parses it (server-side).
    3.  Extracts a specific email based on headers.
- **Outcome:** Validated parser library (e.g., Python `mailbox` module) and benchmarks on processing speed for large files.

## 3. Deliverables
1.  **Feasibility Report:** A document detailing findings on Takeout automation, API availability, and the recommended "Wrapper" strategy.
2.  **Mbox Parser PoC:** A small, working script demonstrating the extraction of emails from a Takeout archive.
3.  **Go/No-Go Recommendation:** A final decision on whether to proceed with full implementation or pivot to a different strategy (e.g., "Forwarding Rules").

## 4. Success Criteria
- We have proof that a user can provide the data we need without Kintsu requiring restricted OAuth scopes.
- We know exactly how "friction-heavy" the process is for the user.
- We have validated that the Mbox format provided by Takeout is parseable and contains the necessary data (HTML body, headers) for our existing Refinery.
