# Specification: Gmail MBOX Processing & Extraction

## 1. Overview
The application currently ingests Gmail `.zip` Takeout files and extracts the contained `.mbox` files. This feature extends that pipeline to process the extracted `.mbox` files. It will iterate through individual emails, saving them to a dedicated directory in the user's BYOS (Google Drive) structure in both forensic (`.eml`) and viewable (`.html`) formats. Additionally, it will utilize Gemini to extract inventory data from each email into a JSON file, while maintaining a comprehensive local processing log.

## 2. Functional Requirements

### 2.1 File Organization
- **Destination:** Create a new folder for each processed MBOX content at: `Hopper/gmail/extract_<zip_filename_minus_extension>/`.
- **Naming Convention:** All generated files for a single email must share a common base name derived from the email's unique `Message-ID` header.
  - The `Message-ID` must be sanitized to be filesystem-safe.
  - **Example:** If `Message-ID` is `<abc-123@mail.gmail.com>`, base name is `abc-123_mail_gmail_com`.

### 2.2 Email Extraction & Storage
- **Hybrid Format:** For each email found in the MBOX:
  - **Forensic Copy (`.eml`):** Save the raw email content to preserve headers and chain of evidence.
  - **Viewable Copy (`.html`):** detailed HTML rendering of the email body for easy viewing in Google Drive/Browsers.
- **Handling Duplicates:**
  - If a file with the same `Message-ID` based name already exists in the destination folder, **SKIP** processing for that specific email.
  - Log the skip event.

### 2.3 Inventory Data Extraction (Gemini)
- **Processor:** Use Gemini to analyze the content of each email.
- **Target Data:** Extract the following fields if available:
  - **Item Details:** Name, description, brand, model number, category.
  - **Transaction Data:** Purchase date, price, tax, shipping, total amount.
  - **Vendor Info:** Merchant name, order number, tracking numbers.
  - **Evidence:** Condition notes and links/references to image attachments.
- **Output:** Save the extracted data to a JSON file: `<base_name>.json`.

### 2.4 Activity Logging
- **Log File:** Maintain a `processing_log.json` file within the `extract_<...>/` directory.
- **Content:** Record a chronological history of actions for that specific processing run.
  - **Events:** Start time, file processed (success), file skipped (duplicate), errors (with details), end time, total summary counts.

## 3. Non-Functional Requirements
- **BYOS (Bring Your Own Storage):** All data (emails, JSONs, logs) must remain within the user's Google Drive hierarchy (`Hopper/`).
- **Idempotency:** Re-running the processor on the same source should not duplicate data or corrupt existing valid files (handled via the "Skip" logic).

## 4. Acceptance Criteria
- [ ] A new folder `Hopper/gmail/extract_<zip_name>` is created upon processing.
- [ ] Emails are saved as both `.eml` and `.html` files using sanitized `Message-ID` filenames.
- [ ] A corresponding `.json` file exists for each email containing extracted inventory data.
- [ ] Re-running the process on an existing folder skips already processed emails.
- [ ] A `processing_log.json` is present in the folder, detailing the successful extraction and any skipped items.
- [ ] Valid `Message-ID`s are correctly extracted and sanitized.
