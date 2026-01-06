import { gapi } from 'gapi-script';

declare global {
  interface Window {
    google: any;
  }
}

const DISCOVERY_DOC = 'https://www.googleapis.com/discovery/v1/apis/drive/v3/rest';

const SCOPES = {
  DRIVE: 'https://www.googleapis.com/auth/drive.file',
  GMAIL: 'https://www.googleapis.com/auth/gmail.readonly'
};

export class DriveService {
  static tokenClient: any;
  static accessToken: string | null = null;
  static grantedScopes: Set<string> = new Set();

  // Initialize GAPI client (for requests) and GIS (for auth)
  static async init(clientId: string, apiKey: string) {
    return new Promise<void>((resolve, reject) => {
      // 1. Load GAPI Client
      gapi.load('client', async () => {
        try {
          await gapi.client.init({
            apiKey: apiKey,
            discoveryDocs: [DISCOVERY_DOC],
          });

          // 2. Init GIS Token Client
          // @ts-ignore - google global is loaded by script tag in index.html
          if (window.google) {
            this.tokenClient = window.google.accounts.oauth2.initTokenClient({
              client_id: clientId,
              scope: SCOPES.DRIVE, // STRICTLY Drive scope only for init
              callback: (tokenResponse: any) => {
                if (tokenResponse && tokenResponse.access_token) {
                  this.accessToken = tokenResponse.access_token;
                  // Track scopes granted (simple heuristic)
                  if (tokenResponse.scope) {
                      tokenResponse.scope.split(' ').forEach((s: string) => this.grantedScopes.add(s));
                  }
                  // Set token for GAPI calls
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
        if (resp.error) {
          reject(resp);
        } else {
          this.accessToken = resp.access_token;
          if (resp.scope) {
             resp.scope.split(' ').forEach((s: string) => this.grantedScopes.add(s));
          }
          // IMPORTANT: Set the token for future GAPI requests
          gapi.client.setToken(resp);
          resolve();
        }
      };

      // Request token (triggers popup) with base scopes ONLY
      this.tokenClient.requestAccessToken({ prompt: 'consent', scope: SCOPES.DRIVE });
    });
  }

  static async requestGmailAccess(): Promise<void> {
      return new Promise((resolve, reject) => {
        if (!this.tokenClient) return reject("Token Client not initialized");

        // Check if we already have it
        if (this.grantedScopes.has(SCOPES.GMAIL)) {
            resolve();
            return;
        }

        this.tokenClient.callback = (resp: any) => {
            if (resp.error) {
                reject(resp);
            } else {
                this.accessToken = resp.access_token;
                if (resp.scope) {
                    resp.scope.split(' ').forEach((s: string) => this.grantedScopes.add(s));
                }
                gapi.client.setToken(resp);
                resolve();
            }
        };

        // Incremental auth: Request BOTH scopes to get a combined token
        const combinedScopes = `${SCOPES.DRIVE} ${SCOPES.GMAIL}`;
        this.tokenClient.requestAccessToken({ prompt: 'consent', scope: combinedScopes });
      });
  }

  static async signOut() {
    const token = gapi.client.getToken();
    if (token !== null) {
      // @ts-ignore
      window.google.accounts.oauth2.revoke(token.access_token, () => {});
      gapi.client.setToken(null);
      this.accessToken = null;
    }
  }

  static get isSignedIn() {
    return !!this.accessToken;
  }

  // --- Folder Management ---

  static async findFolder(name: string, parentId: string = 'root'): Promise<string | null> {
    try {
      const query = `mimeType='application/vnd.google-apps.folder' and name='${name}' and '${parentId}' in parents and trashed=false`;
      const response = await gapi.client.drive.files.list({
        q: query,
        fields: 'files(id, name)',
        spaces: 'drive',
      });
      const files = response.result.files;
      return files && files.length > 0 ? files[0].id : null;
    } catch (e) {
      console.error("Error finding folder:", e);
      return null;
    }
  }

  static async createFolder(name: string, parentId: string = 'root'): Promise<string> {
    const fileMetadata = {
      name: name,
      mimeType: 'application/vnd.google-apps.folder',
      parents: [parentId],
    };
    const response = await gapi.client.drive.files.create({
      resource: fileMetadata,
      fields: 'id',
    });
    return response.result.id;
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
      const resp = await gapi.client.drive.files.list({
        q: `'${folderId}' in parents and trashed=false`,
        fields: 'files(id, name, mimeType)',
        pageSize: 100,
        orderBy: 'folder,name'
      });
      return resp.result.files || [];
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
      
      async function walk(folderId: string, folderName: string, depth: number = 0) {
        console.log(`[Scan] Walking ${folderName} (${folderId}), depth ${depth}`);
        if (depth > 4) return;

        try {
            const resp = await gapi.client.drive.files.list({
              q: `'${folderId}' in parents and trashed=false`,
              fields: 'files(id, name, mimeType)',
              pageSize: 100
            });
            
            const items = resp.result.files || [];
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