# Feasibility Report: Google Takeout as OAuth Alternative

## 1. Executive Summary
**Recommendation: GO** (with caveats).

The research confirms that utilizing Google Takeout is a technically viable alternative to the `gmail.readonly` OAuth scope, effectively bypassing the requirement for CASA Tier 2 security verification. While full automation is impossible (as it requires the same restricted scopes), a "Guided Manual Workflow" is feasible and can be streamlined to be user-friendly.

## 2. Key Findings

### 2.1 API & Automation
- **No Public API:** There is no public API to trigger a Takeout export without requiring restricted/sensitive scopes (`dataportability.mail.export`). Using the official API would not solve the verification problem.
- **No Deep Linking:** We cannot inject a complex search query (e.g., `in:anywhere ...`) directly into the Takeout URL.
- **Workaround:** The "Label-First" strategy is the only robust way to filter data. The user creates a label in Gmail (guided by our app) and then selects *only* that label in Takeout.

### 2.2 Technical Feasibility (Parsing)
- **Mbox Format:** The `.mbox` format provided by Takeout is standard and easily parseable using Python's native `mailbox` library.
- **Data Fidelity:** The archive contains full email headers and HTML bodies, which is sufficient for our existing Gemini-based extraction pipeline (The Refinery).
- **Proof-of-Concept:** A prototype script (`research/takeout_poc/parser.py`) successfully extracted metadata and content from a sample archive.

### 2.3 User Experience (UX) Friction
The process is high-friction compared to "Sign in with Google," but necessary for privacy-conscious users or to avoid verification delays.

**The Workflow:**
1.  **Search & Label:** User copies a search query from Kintsu -> Pastes in Gmail -> Creates Label "Kintsu_Export".
2.  **Export:** User goes to Takeout -> Selects *only* "Kintsu_Export" label -> Downloads Zip.
3.  **Upload:** User drags Zip to Kintsu.

## 3. Proposed Implementation Plan (Next Steps)
To move from Research to Production, we should create a new Feature Track ("Takeout Ingestion Pipeline") with the following scope:

1.  **Frontend:** Build the "Takeout Wizard" (React) implementing the steps defined in the `takeout_user_guide_draft.md`.
2.  **Backend:** Implement a scalable Mbox parser (Cloud Function) that can handle large Zip uploads.
3.  **Integration:** Connect the parser to the existing `ingest-shard` -> Gemini pipeline.
4.  **Cleanup:** Ensure massive Takeout archives are deleted immediately after extraction.

## 4. Conclusion
Proceed with the "Guided Manual Workflow." It provides the required data, adheres to BYOS principles, and completely avoids the blocked OAuth verification path.
