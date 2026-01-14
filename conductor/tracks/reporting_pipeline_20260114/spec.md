# Track Specification: Reporting & Data Review Pipeline

## Overview
This track implements a comprehensive workflow for users to review, refine, and report their collected data to insurance adjusters. It addresses three critical areas sequentially:
1.  **UI/UX:** Standardizing the data review interface for all collected data types (Amazon, Gmail, etc.) in the "Hopper" folders.
2.  **AI Quality:** improving the relevance of processed data.
3.  **Reporting:** Generating the final artifacts (PDF, Zip, Spreadsheet) for adjusters.

## Core Mandates
-   **Strict BYOS (Bring Your Own Storage):** All user data persists in the user's Google Drive. The application must treat Drive as the source of truth. Firestore or local state is strictly for transient processing/indexing.
-   **Non-Destructive Actions:** "Deleting" or "Excluding" files must move them to specific `_deleted` or `_excluded` subfolders within Drive, rather than permanently erasing them immediately.
-   **Engineering Rigor:**
    -   **Debug Mode:** All new code must respect the `/?debug=on` flag, triggering verbose diagnostic logging.
    -   **Root Cause First:** No fix shall be proposed or implemented without definitive proof of the root cause derived from error logs and Firestore data analysis.

## Functional Requirements

### Phase 1: Data Review UI (Skill: UI/UX Pro Max)
-   **Unified Folder View:** Create a consistent list view for all data types (Amazon, Gmail, etc.) residing in the "Hopper".
-   **File Previewers:**
    -   **HTML:** Render strictly as rendered HTML (not raw code) within the app.
    -   **JSON:** Render in a readable, collapsible tree structure.
    -   **Interaction:** Support both a "Quick-Action Sidebar" (for rapid browsing) and a "Modal/Full View" (for detailed inspection).
-   **Review Actions:**
    -   User must be able to mark items as **Keep**, **Exclude**, or **Delete**.
    -   Actions trigger the physical move of files (and their related artifacts like `.eml`, `.json`) to corresponding subfolders in Drive.

### Phase 2: AI Data Refinement (Skill: AI Pro Max)
-   **Noise Reduction:** Review current extraction logic (for Amazon/Gmail) to identify why "irrelevant data" is being captured.
-   **Refinement:** Tune prompts or filtering logic to improve the signal-to-noise ratio of the data presented in the Review UI.


### Phase 3: Reporting Engine (Skill: Senior Fullstack)
-   **Standard Formats:**
    -   **PDF Summary:** A professional-grade document listing all claimed items with totals, suitable for immediate adjuster review.
    -   **CSV/Excel:** A structured inventory list for importing into insurance software.
    -   **ZIP Archive:** A comprehensive bundle of all source files (PDFs, images) referenced in the report, maintaining the folder structure.
-   **Export Engine:**
    -   Build a backend service (Python) to aggregate "Keep" data.
    -   Support generation of all three target formats.
    -   Ensure the generated report is saved back to the user's Drive in a new "Reports" folder.


## Non-Functional Requirements
-   **Performance:** Previews of large HTML/JSON files should not freeze the UI.
-   **Consistency:** The UI pattern established here must be reusable for future data sources.
-   **Observability:** Comprehensive logging for file operations and API interactions when in debug mode.

## Out of Scope
-   Real-time submission to insurance APIs (Export artifacts only).
