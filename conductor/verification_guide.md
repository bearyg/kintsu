# Resolving "Google hasn't verified this app" Warning

You are seeing this warning because your application is configured with the **Testing** status or has not completed the verification process for the scopes it requests.

Even though we removed `gmail.readonly`, the app still requests `https://www.googleapis.com/auth/drive.file` to create and manage the Hopper. This is considered a **Sensitive Scope** by Google (level 2), which triggers the unverified warning until the app is verified.

## Immediate Workaround (for Development)
You can bypass this warning safely since you are the developer:
1.  When the warning appears, click the **Advanced** link (usually on the left).
2.  Click **Go to Kintsu (unsafe)** at the bottom.
3.  Type "continue" if prompted.

## Permanent Fixes

### Option A: Internal App (Best for Workspace/Organization)
If `admin@homesteadinventory.com` is part of a Google Workspace organization:
1.  Go to the [Google Cloud Console > APIs & Services > OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent).
2.  Click **Edit App**.
3.  Change the **User Type** to **Internal**.
4.  Save.
    *   *Result:* Users within your organization (`@homesteadinventory.com`) will not see the warning. External users cannot access it.

### Option B: External App (Testing Mode)
If you want to keep it strictly for yourself and a few testers:
1.  Go to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent).
2.  Ensure **Publishing Status** is **Testing**.
3.  Under **Test Users**, ensure your email (`admin@homesteadinventory.com`) is added.
    *   *Result:* You will still see the warning, but you can bypass it via the "Advanced" link.

### Option C: Production Verification (Public App)
If you want to release this to the public:
1.  Go to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent).
2.  Click **Publish App**.
3.  Submit the app for verification. You will need to provide:
    *   A privacy policy URL.
    *   A YouTube video demonstrating how you use the `drive.file` scope.
    *   A written explanation of why this scope is necessary (e.g., "The app creates a dedicated folder 'Kintsu/Hopper' to store and organize the user's forensic data locally in their Drive.").

## Scope Details
The current codebase only requests:
*   `https://www.googleapis.com/auth/drive.file`: "View and manage Google Drive files and folders that you have opened or created with this app."
