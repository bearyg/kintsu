# Research Findings: Google Takeout Automation

## 1. Google Data Portability API
*   **Status:** **Promising but restricted.**
*   **Overview:** The Data Portability API (`dataportability.googleapis.com`) allows applications to request user authorization to transfer data directly from Google services.
*   **Pros:**
    *   Official, supported API.
    *   Designed specifically for data transfer.
    *   Supports "Mail" (Gmail) export.
*   **Cons:**
    *   **Restricted Access:** Requires completing a **verification process** because it accesses sensitive data scopes. This might be just as difficult as the `gmail.readonly` verification we are trying to avoid.
    *   **Scope Sensitivity:** The scopes required (`https://www.googleapis.com/auth/dataportability.mail.export`) are likely classified as "Restricted" or "Sensitive," triggering CASA Tier 2 requirements.
*   **Conclusion:** This is likely a dead end for *avoiding* verification, but it is the most robust technical solution if verification were acceptable.

## 2. Data Transfer Project (DTP)
*   **Status:** **Framework, not a public API for 3rd parties.**
*   **Overview:** DTP is the underlying open-source framework Google uses for its own "Transfer" tools (e.g., Transfer to generic services).
*   **Findings:** There is no public "DTP API" that a third-party app can hit to trigger a transfer *without* being a recognized major partner integration. It relies on the same underlying mechanics as the Data Portability API.

## 3. Deep Linking / URL Parameters
*   **Status:** **Partial Success (Unofficial).**
*   **Overview:** Google Takeout supports some internal parameters, but there is no documented public URL schema for pre-filling the "Query" field for Gmail.
*   **Deep Link Capability:**
    *   Can potentially select *only* specific products (e.g., `?products=MAIL`).
    *   **Critical Gap:** There is **NO** known URL parameter to inject the specific search query (`in:anywhere ...`) into the Gmail export settings. This must be done manually by the user in the UI.
*   **UX Implication:** We can link the user to the "Mail" selection page, but they *must* manually click "All Mail data included", uncheck "Include all messages in Mail", and paste our query string.

## 4. Browser Automation / Extensions
*   **Status:** **Feasible but high friction.**
*   **Approach:** A Chrome Extension could theoretically inject the query string into the Takeout DOM.
*   **Cons:**
    *   Requires user to install an extension (high friction).
    *   Google's DOM changes could break the extension.
    *   Security risk perception for the user.

## 5. Summary & Recommendation
*   **Automation:** Full automation via API is blocked by the same verification requirements we want to avoid.
*   **"Wrapper" Strategy:** The most viable "No-Verification" path is a **Guided Manual Workflow**.
    *   **Step 1:** Link user to `takeout.google.com` (possibly with product pre-selected if we find the exact param).
    *   **Step 2:** User manually clicks the settings.
    *   **Step 3:** Kintsu provides a "Copy to Clipboard" button for the complex query string.
    *   **Step 4:** User pastes the query and starts the export.
    *   **Step 5:** User drags the resulting `.mbox` file into Kintsu.

This "Low Tech" approach is the only one that guarantees bypassing the OAuth Verification process while still getting the filtered data.
