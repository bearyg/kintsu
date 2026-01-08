# Guide: Exporting Your Gmail for Kintsu

Kintsu needs access to your receipts and order confirmations to process your claims. To keep your data private and secure, we ask you to provide a filtered export from Google Takeout instead of giving us full access to your email.

Follow these steps to generate the file we need.

## Step 1: Go to Google Takeout
1.  Open your browser and navigate to: **[https://takeout.google.com/](https://takeout.google.com/)**
2.  Make sure you are signed in to the correct Google account.

## Step 2: Deselect Everything
By default, Google selects *all* your data (Photos, Drive, Maps, etc.). We don't want that!
1.  Look for the "Select data to include" section.
2.  Click the **"Deselect all"** button at the top of the list.
    *(Placeholder: Screenshot of 'Deselect all' button)*

## Step 3: Select Only "Mail"
1.  Scroll down until you find **"Mail"**.
2.  Check the box next to "Mail".
    *(Placeholder: Screenshot of 'Mail' checkbox)*

## Step 4: Filter Your Data (Crucial Step!)
We only want specific emails (receipts & orders). Filtering reduces the file size and protects your privacy.
1.  Click on the button labeled **"All Mail data included"** inside the Mail section.
2.  Uncheck "Include all messages in Mail".
3.  (Optional) If you use labels for receipts, select those labels. Otherwise, leave this section and click **"Cancel"** if you want to use the Advanced Search (recommended below).

**Better Method: Advanced Search**
*Note: As of our latest research, Takeout's UI for filtering by query is hidden inside "All Mail data included" -> "Advanced Settings" (if available) or relies on Label selection. Since query injection isn't directly supported in the UI simply, we recommend Labeling.*

**Revised Strategy: Create a Temporary Label in Gmail First**
Since Takeout works best with Labels, let's create a "Kintsu_Export" label first.

### Pre-Step: Create the Label in Gmail
1.  Open Gmail.
2.  In the search bar, paste this exact search:
    ```
    in:anywhere (receipt OR order OR "sales invoice") OR label:(^cob_sm_order OR ^cob_sm_cl_jc_order OR ^cob_sm_cl_llm_order)
    ```
3.  Click the "Select All" checkbox (and "Select all conversations that match this search").
4.  Click the "Labels" icon -> "Create new" -> Name it **"Kintsu_Export"**.

### Back to Takeout (Step 4 continued)
1.  Click **"All Mail data included"**.
2.  **Uncheck** "Include all messages in Mail".
3.  **Check ONLY** the **"Kintsu_Export"** label.
4.  Click **"OK"**.
    *(Placeholder: Screenshot of Label selection)*

## Step 5: Create Export
1.  Scroll to the very bottom and click **"Next step"**.
2.  **Destination:** "Send download link via email" (or "Add to Drive" if you prefer).
3.  **Frequency:** "Export once".
4.  **File type & size:** Leave as `.zip` and `2 GB`.
5.  Click **"Create export"**.

## Step 6: Upload to Kintsu
1.  Wait for the email from Google (usually takes a few minutes for filtered exports).
2.  Download the `.zip` file.
3.  Drag and drop that `.zip` file into the Kintsu "Drop Zone".

---
**Why this method?**
- **Privacy:** You only share specific emails.
- **Security:** You don't give any app permanent access to your inbox.
- **Control:** You can see exactly what is being exported before you send it.
