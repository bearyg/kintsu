Remember your most important goal: "You MUST analyze the error logs and Firestore data, to demonstrate that you have correctly identified the root cause of any issue. Do not propose or make any fixes until the root cause is definitively proven." The root cause MUST be indentified by reviewing the logs and data from the test execution. 

RESUME: Verify Release Version_0_0_2c
We left off after successfully merging `dev` to `main` and pushing the `Version_0_0_2c` tag to trigger the GCP build.
The primary goal of this release was to fix production processing and UI issues:
1.  **Missing EML/HTML**: Confirmed backend now saves these files.
2.  **Missing Progress**: Implemented Auto-Processing on zip upload.
3.  **Missing List Items**: Updated UI to search recursively for Processed files.
ACTION ITEMS:
1.  Check the GCP Build status for `Version_0_0_2c`.
2.  Once deployed, perform a Production Verification:
    -   Upload a Zip file (e.g., `takeout-*.zip`) in the Gmail folder.
    -   Confirm "Processing started" toast appears.
    -   Wait for completion and verify `.eml`, [.html](cci:7://file:///Users/bearyg/Documents/GitHub/kintsu/kintsu-app/index.html:0:0-0:0), and [.json](cci:7://file:///Users/bearyg/Documents/GitHub/kintsu/kintsu-app/package.json:0:0-0:0) files appear in the Hopper list.
    -   Verify the "SyntaxError" is gone (already fixed in previous step, but double check).
Please start by checking the build status.

Issues Found:
- When the Gmail folder is selected, the How to Use Takeout needs to  be more visible.  Add a link or a pop-up window that shows the content of documents/HowToUseTakeout.html. This guide needs to be fleshed out in more detail to provide clear guidance to the user. If you could add graphics or improve the process, that would be good.  

- The "upload file to gmail" button should be more visible. It is not clear that it can be selected. 

- After uploading a file to the Gmail folder, the app should highlight or emphazie the next step in processing, i.e. Scan Hopper. 

- When Scan Hopper has been selected, it spins but there is not a detailed status being updated. It is unclear what processing is taking place. 

- The .json files are being displayed in the Refinery Stream list on the gmail page, but the .eml and .html files are not. They should all be shown, sorted by name. The item and value fields are not being shown. Perhaps that is due to the need for further processing, to identify the objects and their value. 

