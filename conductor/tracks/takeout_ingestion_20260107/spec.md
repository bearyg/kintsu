# Specification: Google Takeout Ingestion Pipeline

## 1. Overview
This track implements the production-ready pipeline for ingesting Google Takeout (`.mbox`) archives. This replaces the direct Gmail API integration. The system will guide the user through creating a filtered export (via a "Label-First" manual workflow), uploading the large archive, and processing it cloud-side to extract financial records (receipts, orders).

## 2. Functional Requirements

### 2.1 Frontend: The Takeout Wizard
- **UI:** A multi-step React component ("Wizard") guiding the user:
    1.  **Search & Label:** Provide the search query text and instructions to create a "Kintsu_Export" label in Gmail.
    2.  **Export:** Guide the user to `takeout.google.com` to export *only* that label.
    3.  **Upload:** A drag-and-drop zone for the resulting `.zip` or `.mbox` file.
    4.  **Status Dashboard:** A dedicated view showing the status of current and past jobs (Queued, Processing, Completed, Failed).
- **UX:**
    - "Fire and Forget": Users can navigate away or close the tab; processing continues in the background.
    - "Watch Mode": Real-time progress bar/log for active jobs (powered by SSE or Polling).
- **Options:** 
    - Allow users to toggle "Force Reprocess" (ignore duplicate checks).

### 2.2 Backend: Asynchronous Processing Architecture
- **Architecture:** 
    - **Upload Endpoint:** Accepts the file, saves it to a temporary bucket, creates a "Job" record (Firestore), and acknowledges receipt immediately.
    - **Worker Service (Cloud Run):** Triggered asynchronously (e.g., via Pub/Sub or Cloud Storage Event) to process the file.
- **Protocol:** Use **Server-Sent Events (SSE)** or Polling on the "Job" record to stream progress back to the active client.
- **Parsing Logic:**
    - Stream the Mbox file (avoid loading 2GB+ into memory if possible, or use high-memory instance).
    - **Filtering:** 
        - Primary: Trust the user's data (if they uploaded it, process it).
        - Heuristic: Perform lightweight checks (currency symbols, "Order" keywords) to prioritize Gemini calls, but default to processing.
    - **Extraction:** Send relevant email bodies (HTML preferred) to the existing Gemini refinery logic.

### 2.3 Artifact Generation & Storage (BYOS)
- **Output:**
    - Save extracted email bodies (HTML/PDF) to `Hopper/Gmail/` in the user's Drive.
    - Update `Kintsu_Inventory.xlsx` with extracted line items.
- **Cleanup:** The uploaded Mbox/Zip file MUST be deleted from Kintsu's temporary storage immediately after processing.

### 2.4 Deduplication Strategy
- **Default:** Check `Message-ID` against a history of processed IDs. Skip if found.
- **Override:** If the user selected "Force Reprocess" (or "Start Over"), ignore the history and re-extract/overwrite.

### 2.5 Diagnostics & Observability
- **Debug Mode:** All services must respect the `?debug=on` flag (or a `debugMode` boolean in the Job config).
    - When enabled, produce verbose logs (e.g., "Skipping email ID 123 due to duplicate check", "Gemini Extraction Confidence: 0.85").
    - Make these logs visible in the UI "Console" or a dedicated debug view.

## 3. Non-Functional Requirements
- **Asynchrony:** The system must be fully asynchronous. The upload action starts a job; the completion of that job happens independently of the user's session.
- **Performance:** Must handle archives up to 2GB without timeout.
- **Privacy:** Strict Zero-Retention for the raw archive.

## 4. Acceptance Criteria
- User can successfully upload a sample Mbox file via the UI.
- The UI immediately confirms upload and allows the user to navigate away.
- Returning to the UI shows the correct status (Processing/Complete).
- Cloud Run service processes the file asynchronously.
- Duplicate emails are skipped by default.
- "Force Reprocess" option works.
- Extracted data appears in the user's Drive.
- `debug=on` enables verbose logging visible to the developer/user.

## 5. Out of Scope
- Automatic triggering of the Takeout export.
