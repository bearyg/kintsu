import { gapi } from 'gapi-script';

declare global {
  interface Window {
    google: any;
  }
}



const SCOPES_LIST = [
  'https://www.googleapis.com/auth/drive.file'
];

const SCOPES = SCOPES_LIST.join(' ');

export class DriveService {
  static tokenClient: any;
  static accessToken: string | null = null;
  static grantedScopes: Set<string> = new Set();



  // Initialize GAPI client (for requests) and GIS (for auth)
  static async init(clientId: string, apiKey: string) {
    return new Promise<void>((resolve, reject) => {
      // 1. Load GAPI Client
      gapi.load('client', async () => {
        let retries = 3;
        while (retries > 0) {
          try {
            await gapi.client.init({
              apiKey: apiKey,
              // discoveryDocs: [DISCOVERY_DOC], // Removed due to 502 errors
            });
            // Skip loading Drive API via GAPI (502 error on discovery).
            // We will use raw fetch instead.
            // await gapi.client.load('drive', 'v3');
            break; // Success
          } catch (e: any) {
            console.warn(`GAPI Init failed, retrying... (${retries} left)`, e);
            retries--;
            if (retries === 0) {
              reject(e);
              return;
            }
            // Wait 1s before retry
            await new Promise(r => setTimeout(r, 1000));
          }
        }

        try {
          // 2. Init GIS Token Client
          // @ts-ignore - google global is loaded by script tag in index.html
          if (window.google) {
            if (window.location.search.includes('debug=on')) {
              console.group('OAuth Init');
              console.log('Requesting Scopes:', SCOPES_LIST);
              console.groupEnd();
            }

            this.tokenClient = window.google.accounts.oauth2.initTokenClient({
              client_id: clientId,
              scope: SCOPES,
              callback: (tokenResponse: any) => {
                if (window.location.search.includes('debug=on')) {
                  console.group('OAuth Callback');
                  console.log('Token Response:', tokenResponse);
                }

                if (tokenResponse && tokenResponse.access_token) {
                  this.accessToken = tokenResponse.access_token;

                  // Track scopes granted
                  if (tokenResponse.scope) {
                    const granted = tokenResponse.scope.split(' ');
                    granted.forEach((s: string) => this.grantedScopes.add(s));

                    if (window.location.search.includes('debug=on')) {
                      console.log('Granted Scopes:', granted);
                      const missing = SCOPES_LIST.filter(s => !granted.includes(s));
                      if (missing.length > 0) {
                        console.warn('MISMATCH! Missing Scopes:', missing);
                      } else {
                        console.log('All requested scopes granted.');
                      }
                    }
                  }

                  if (window.location.search.includes('debug=on')) {
                    if (tokenResponse.error) {
                      console.error('OAuth Error:', tokenResponse.error);
                    }
                    console.groupEnd();
                  }

                  // Set token for GAPI calls (legacy support if needed)
                  gapi.client.setToken(tokenResponse);
                }
              },
            });
            resolve();
          } else {
            reject("Google Identity Services script not loaded");
          }
        } catch (e) {
          reject(e);
        }
      });
    });
  }

  static async signIn(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.tokenClient) return reject("Token Client not initialized");

      // Override callback to resolve this specific request
      this.tokenClient.callback = (resp: any) => {
        if (window.location.search.includes('debug=on')) {
          console.group('OAuth Callback (SignIn)');
          console.log('Response:', resp);
        }

        if (resp.error) {
          if (window.location.search.includes('debug=on')) {
            console.error('SignIn Error:', resp);
            console.groupEnd();
          }
          reject(resp);
        } else {
          this.accessToken = resp.access_token;
          if (resp.scope) {
            const granted = resp.scope.split(' ');
            granted.forEach((s: string) => this.grantedScopes.add(s));

            if (window.location.search.includes('debug=on')) {
              const missing = SCOPES_LIST.filter(s => !granted.includes(s));
              if (missing.length > 0) {
                console.warn('MISMATCH! Missing Scopes:', missing);
              }
            }
          }

          if (window.location.search.includes('debug=on')) {
            console.groupEnd();
          }

          // IMPORTANT: Set the token for future GAPI requests
          gapi.client.setToken(resp);
          resolve();
        }
      };

      // Request token (triggers popup) with base scopes
      if (window.location.search.includes('debug=on')) {
        console.log('Triggering RequestAccessToken with:', SCOPES);
      }
      this.tokenClient.requestAccessToken({ prompt: 'consent', scope: SCOPES });
    });
  }

  static async signOut() {
    const token = gapi.client.getToken();
    if (token !== null) {
      // @ts-ignore
      window.google.accounts.oauth2.revoke(token.access_token, () => { });
      gapi.client.setToken(null);
      this.accessToken = null;
    }
  }

  static get isSignedIn() {
    return !!this.accessToken;
  }

  // --- Helper for Fetch calls ---
  static async _fetch(endpoint: string, options: RequestInit = {}) {
    if (!this.accessToken) throw new Error("Not signed in");

    const headers = new Headers(options.headers || {});
    headers.append('Authorization', `Bearer ${this.accessToken}`);

    try {
      const response = await fetch(endpoint, {
        ...options,
        headers: headers
      });

      if (!response.ok) {
        const errBody = await response.text();
        throw new Error(`Drive API Error ${response.status}: ${errBody}`);
      }
      return response;
    } catch (e) {
      throw e;
    }
  }

  // --- Folder Management ---

  static async findFolder(name: string, parentId: string = 'root'): Promise<string | null> {
    return this.findFile(name, parentId, 'application/vnd.google-apps.folder');
  }

  static async findFile(name: string, parentId: string = 'root', mimeType?: string): Promise<string | null> {
    try {
      let q = `name='${name}' and '${parentId}' in parents and trashed=false`;
      if (mimeType) {
        q += ` and mimeType='${mimeType}'`;
      }

      const params = new URLSearchParams({
        q: q,
        fields: 'files(id, name)',
        spaces: 'drive'
      });

      const response = await this._fetch(`https://www.googleapis.com/drive/v3/files?${params.toString()}`);
      const data = await response.json();
      const files = data.files;
      return files && files.length > 0 ? files[0].id : null;
    } catch (e) {
      console.error("Error finding file:", e);
      return null;
    }
  }

  static async getFileContent(fileId: string): Promise<string> {
    try {
      const response = await this._fetch(`https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`);
      const text = await response.text();
      return text;
    } catch (e) {
      console.error("Error getting file content:", e);
      throw e;
    }
  }

  static async createFolder(name: string, parentId: string = 'root'): Promise<string> {
    const fileMetadata = {
      name: name,
      mimeType: 'application/vnd.google-apps.folder',
      parents: [parentId],
    };

    const response = await this._fetch('https://www.googleapis.com/drive/v3/files?fields=id', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(fileMetadata)
    });

    const data = await response.json();
    return data.id;
  }

  static async ensureHopperStructure(): Promise<void> {
    try {
      // 1. Check/Create Root 'Kintsu'
      let kintsuId = await this.findFolder('Kintsu');
      if (!kintsuId) {
        console.log("Creating Kintsu root folder...");
        kintsuId = await this.createFolder('Kintsu');
      }

      // 2. Check/Create 'Hopper'
      let hopperId = await this.findFolder('Hopper', kintsuId);
      if (!hopperId) {
        console.log("Creating Hopper folder...");
        hopperId = await this.createFolder('Hopper', kintsuId);
      }

      // 3. Create Sub-containers
      const containers = ['Amazon', 'Banking', 'Gmail', 'Photos', 'Receipts'];
      for (const container of containers) {
        const subId = await this.findFolder(container, hopperId);
        if (!subId) {
          console.log(`Creating ${container} container...`);
          await this.createFolder(container, hopperId);
        }
      }

      console.log("Hopper Structure Verified.");

    } catch (error) {
      console.error("Error setting up Drive folders:", error);
      throw error;
    }
  }

  static async uploadFile(file: File, parentId: string): Promise<any> {
    const metadata = {
      name: file.name,
      mimeType: file.type,
      parents: [parentId],
    };

    const form = new FormData();
    form.append('metadata', new Blob([JSON.stringify(metadata)], { type: 'application/json' }));
    form.append('file', file);

    const response = await fetch('https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,mimeType', {
      method: 'POST',
      headers: new Headers({ 'Authorization': 'Bearer ' + this.accessToken }),
      body: form,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    return await response.json();
  }

  static async listChildren(folderId: string): Promise<any[]> {
    try {
      const params = new URLSearchParams({
        q: `'${folderId}' in parents and trashed=false`,
        fields: 'files(id, name, mimeType, webViewLink)',
        pageSize: '100',
        orderBy: 'folder,name'
      });

      const response = await this._fetch(`https://www.googleapis.com/drive/v3/files?${params.toString()}`);
      const data = await response.json();
      return data.files || [];
    } catch (e) {
      console.error("List children error:", e);
      return [];
    }
  }

  static async listHopperFiles(): Promise<any[]> {
    try {
      console.log("Starting Hopper Scan...");
      const kintsuId = await this.findFolder('Kintsu');
      if (!kintsuId) {
        console.warn("Kintsu folder not found");
        return [];
      }

      const hopperId = await this.findFolder('Hopper', kintsuId);
      if (!hopperId) {
        console.warn("Hopper folder not found");
        return [];
      }

      console.log(`Found Hopper ID: ${hopperId}`);

      // Recursive Walker
      const allFiles: any[] = [];
      const _this = this; // Capture static context

      async function walk(folderId: string, folderName: string, depth: number = 0) {
        console.log(`[Scan] Walking ${folderName} (${folderId}), depth ${depth}`);
        if (depth > 4) return;

        try {
          const params = new URLSearchParams({
            q: `'${folderId}' in parents and trashed=false`,
            fields: 'files(id, name, mimeType)',
            pageSize: '100'
          });

          const response = await _this._fetch(`https://www.googleapis.com/drive/v3/files?${params.toString()}`);
          const data = await response.json();
          const items = data.files || [];

          console.log(`[Scan] Found ${items.length} items in ${folderName}`);

          for (const item of items) {
            // Log every item seen
            console.log(`[Scan] Item: ${item.name} (${item.mimeType})`);

            if (item.mimeType === 'application/vnd.google-apps.folder') {
              await walk(item.id, item.name, depth + 1);
            } else {
              // It's a file
              console.log(`[Scan] >>> Candidate File: ${item.name}`);
              allFiles.push({ ...item, sourceType: folderName });
            }
          }
        } catch (err) {
          console.error(`[Scan] Error walking ${folderName}:`, err);
        }
      }

      // Start scan at Hopper
      await walk(hopperId, 'Hopper');
      console.log(`[Scan] Complete. Total candidates: ${allFiles.length}`);
      return allFiles;

    } catch (e) {
      console.error("List files error:", e);
      return [];
    }
  }
}