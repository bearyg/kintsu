import { useState, useEffect } from 'react';
import { Package, FileText, Image, CreditCard, HardDrive, Loader2, UploadCloud, LogOut, Lock, RefreshCw, Folder, ChevronRight, CornerLeftUp, Plus } from 'lucide-react';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';
import { collection, onSnapshot, query, orderBy, Timestamp } from 'firebase/firestore';
import { db } from './firebase';
import { DriveService } from './DriveService';
import { TakeoutWizard } from './components/TakeoutWizard';

// --- Configuration ---
const CLIENT_ID = "351476623210-j0s46m1ermc27qlret2rdn1iqg6re013.apps.googleusercontent.com";
const API_KEY = import.meta.env.VITE_GOOGLE_API_KEY;

// --- Types ---


interface ExtractedData {
  item_name?: string;
  total_amount?: number;
  currency?: string;
  merchant?: string;
  date?: string;
  confidence?: string;
}

interface Shard {
  id: string;
  fileName: string;
  sourceType: string;
  status: 'unprocessed' | 'refined' | 'error';
  driveFileId?: string;
  createdAt: Timestamp;
}

// --- Utils ---
function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs));
}

// --- Components ---

const RefinedShardItem = ({ shard, getIcon }: { shard: Shard, getIcon: (s: string) => any }) => {
  const [data, setData] = useState<ExtractedData | null>(null);
  const [loading, setLoading] = useState(false);
  const Icon = getIcon(shard.sourceType);
  const isRefined = shard.status === 'refined';

  useEffect(() => {
    if (isRefined && shard.driveFileId && !data) {
      const fetchData = async () => {
        setLoading(true);
        try {
          const content = await DriveService.getFileContent(shard.driveFileId!);
          setData(JSON.parse(content));
        } catch (e) {
          console.error("Error loading sidecar:", e);
        } finally {
          setLoading(false);
        }
      };
      fetchData();
    }
  }, [isRefined, shard.driveFileId, data]);

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-xl border transition-all p-5 flex gap-5 group bg-white",
        isRefined
          ? "border-[#D4AF37]/30 shadow-md shadow-orange-100"
          : "border-slate-200 opacity-80"
      )}
    >
      <div className={cn(
        "absolute left-0 top-0 bottom-0 w-1.5",
        isRefined ? "bg-[#D4AF37]" : "bg-slate-300"
      )} />

      <div className={cn(
        "w-12 h-12 rounded-lg flex items-center justify-center shrink-0",
        isRefined ? "bg-orange-50 text-[#D4AF37]" : "bg-slate-100 text-slate-400"
      )}>
        <Icon className="w-6 h-6" />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex justify-between items-start mb-2">
          <h4 className={cn("font-bold truncate pr-4", isRefined ? "text-slate-900" : "text-slate-500")}>
            {shard.fileName}
          </h4>
          <span className="text-xs font-mono text-slate-400 shrink-0">
            {shard.createdAt?.toDate().toLocaleTimeString()}
          </span>
        </div>

        {isRefined ? (
          loading ? (
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <Loader2 className="w-3 h-3 animate-spin" />
              <span>Loading from Drive...</span>
            </div>
          ) : data ? (
            <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm mt-1">
              <div className="flex items-center gap-2">
                <span className="text-slate-400 text-xs uppercase font-bold">Item</span>
                <span className="font-medium text-[#0F172A]">{data.item_name}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-400 text-xs uppercase font-bold">Value</span>
                <span className="font-bold text-[#D4AF37]">
                  {data.currency} {data.total_amount}
                </span>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <RefreshCw className="w-3 h-3" />
              <span>Waiting for record...</span>
            </div>
          )
        ) : (
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Loader2 className="w-3 h-3 animate-spin" />
            <span>Gemini is analyzing...</span>
          </div>
        )}
      </div>
    </div>
  );
};

const PhaseBadge = ({ step, label, current }: { step: number, label: string, current: number }) => {
  const isActive = step === current;
  const isPast = step < current;

  return (
    <div className={cn("flex items-center gap-2", isActive ? "opacity-100" : "opacity-50")}>
      <div className={cn(
        "w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm transition-all",
        isActive ? "bg-[#D4AF37] text-white shadow-lg shadow-yellow-500/20" :
          isPast ? "bg-slate-900 text-[#D4AF37]" : "bg-slate-200 text-slate-500"
      )}>
        {step}
      </div>
      <span className={cn("text-sm font-medium hidden md:block", isActive ? "text-slate-900" : "text-slate-500")}>
        {label}
      </span>
      {step < 4 && <div className="w-8 h-0.5 bg-slate-200 hidden md:block mx-2" />}
    </div>
  );
};

// --- Main App ---

function App() {
  const [shards, setShards] = useState<Shard[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPhase] = useState(2);
  const [isSignedIn, setIsSignedIn] = useState(false);

  const [isInitializing, setIsInitializing] = useState(true);
  const [isScanning, setIsScanning] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  // Drive Browser State
  const [currentFolderId, setCurrentFolderId] = useState<string | null>(null);
  const [driveItems, setDriveItems] = useState<any[]>([]);
  const [breadcrumbs, setBreadcrumbs] = useState<{ id: string, name: string }[]>([]);
  const [browserLoading, setBrowserLoading] = useState(false);

  const API_BASE = "https://kintsu-backend-351476623210.us-central1.run.app";



  // Init App
  useEffect(() => {
    const initApp = async () => {
      try {
        await DriveService.init(CLIENT_ID, API_KEY);
        setIsSignedIn(DriveService.isSignedIn);
        if (DriveService.isSignedIn) {
          const kintsuId = await DriveService.findFolder('Kintsu');
          if (kintsuId) {
            const hopperId = await DriveService.findFolder('Hopper', kintsuId);
            if (hopperId) {
              setCurrentFolderId(hopperId);
              setBreadcrumbs([{ id: hopperId, name: 'Hopper' }]);
            }
          }

          // Initial Fetch of Refinery Stream (from Drive)
          refreshRefineryStream();
        }
      } catch (error) {
        console.error("Failed to init Drive:", error);
      } finally {
        setIsInitializing(false);
      }
    };
    initApp();
  }, []);

  const refreshRefineryStream = async () => {
    if (!DriveService.isSignedIn) return;
    setLoading(true);
    try {
      const files = await DriveService.listRefinedFiles();
      // Map Drive files to Shard interface
      const driveShards: Shard[] = files.map(f => ({
        id: f.id,
        fileName: f.name,
        sourceType: f.sourceType || 'Unknown',
        status: 'refined', // Assume anything in Hopper is "processed"
        driveFileId: f.id,
        webViewLink: f.webViewLink,
        createdAt: Timestamp.now() // Estimate or use createdTime if we ask for it
      }));
      setShards(driveShards);
    } catch (e) {
      console.error("Failed to refresh stream:", e);
    } finally {
      setLoading(false);
    }
  };

  // Fetch Drive Items when folder changes
  useEffect(() => {
    if (!currentFolderId || !isSignedIn) return;
    const fetchItems = async () => {
      setBrowserLoading(true);
      const items = await DriveService.listChildren(currentFolderId);
      setDriveItems(items);
      setBrowserLoading(false);
    };
    fetchItems();
  }, [currentFolderId, isSignedIn]);

  const handleNavigate = (folderId: string, folderName: string) => {
    setCurrentFolderId(folderId);
    setBreadcrumbs(prev => [...prev, { id: folderId, name: folderName }]);
  };

  const handleNavigateUp = () => {
    if (breadcrumbs.length <= 1) return;
    const newBreadcrumbs = [...breadcrumbs];
    newBreadcrumbs.pop();
    const parent = newBreadcrumbs[newBreadcrumbs.length - 1];
    setBreadcrumbs(newBreadcrumbs);
    setCurrentFolderId(parent.id);
  };

  const handleBreadcrumbClick = (index: number) => {
    // If clicking the last item (current), do nothing
    if (index === breadcrumbs.length - 1) return;

    const targetCrumb = breadcrumbs[index];
    const newBreadcrumbs = breadcrumbs.slice(0, index + 1);

    setBreadcrumbs(newBreadcrumbs);
    setCurrentFolderId(targetCrumb.id);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0 || !currentFolderId) return;
    const file = e.target.files[0];

    setIsUploading(true);
    try {
      await DriveService.uploadFile(file, currentFolderId);
      // Refresh view
      const items = await DriveService.listChildren(currentFolderId);
      setDriveItems(items);

      // Auto-Scan this single file (optional, or rely on Scan button)
      console.log(`Sending for refinement: ${file.name}`);
      // For MVP, user will click Scan All to process batch

    } catch (error) {
      console.error("Upload failed:", error);
      alert("Upload failed.");
    } finally {
      setIsUploading(false);
      e.target.value = "";
    }
  };

  const handleCreateFolder = async () => {
    const name = prompt("Enter folder name:");
    if (name && currentFolderId) {
      await DriveService.createFolder(name, currentFolderId);
      const items = await DriveService.listChildren(currentFolderId);
      setDriveItems(items);
    }
  };

  const handleScan = async () => {
    setIsScanning(true);
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const isDebug = urlParams.get('debug') === 'on';

      const files = await DriveService.listHopperFiles();
      const existingIds = new Set(shards.map(s => s.id));

      for (const file of files) {
        const shardId = `drive_${file.id}`;
        if (!existingIds.has(shardId)) {
          console.log(`Sending for refinement: ${file.name}${isDebug ? ' (DEBUG ON)' : ''}`);

          const apiUrl = new URL(`${API_BASE}/api/refine-drive-file`);
          if (isDebug) {
            apiUrl.searchParams.append('debug', 'on');
          }

          await fetch(apiUrl.toString(), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              file_id: file.id,
              fileName: file.name,
              access_token: DriveService.accessToken,
              source_type: file.sourceType || 'Upload'
            })
          });
        }
      }
    } catch (e) {
      console.error("Scan error:", e);
    } finally {
      setIsScanning(false);
    }
  };

  const handleLogin = async () => {
    try {
      await DriveService.signIn();
      setIsSignedIn(true);

      // User registration removed for strict scope compliance


      await DriveService.ensureHopperStructure();

      const kintsuId = await DriveService.findFolder('Kintsu');
      if (kintsuId) {
        const hopperId = await DriveService.findFolder('Hopper', kintsuId);
        if (hopperId) {
          setCurrentFolderId(hopperId);
          setBreadcrumbs([{ id: hopperId, name: 'Hopper' }]);
        }
      }

    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  const handleLogout = async () => {
    await DriveService.signOut();
    setIsSignedIn(false);
    // User state removed
    setCurrentFolderId(null);
    setBreadcrumbs([]);
  };

  const getIcon = (source: string) => {
    switch (source) {
      case 'Amazon': return Package;
      case 'Banking': return CreditCard;
      case 'Gmail': return FileText;
      case 'Photos': return Image;
      default: return HardDrive;
    }
  };

  // --- Auth Loading Screen ---
  if (isInitializing) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Loader2 className="w-10 h-10 animate-spin text-[#D4AF37]" />
      </div>
    );
  }

  // --- Login Screen ---
  if (!isSignedIn) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex flex-col items-center justify-center p-6">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-slate-100 p-10 text-center">
          <img src="/kintsu-icon.jpeg" alt="Kintsu" className="w-20 h-20 rounded-2xl mx-auto mb-6 shadow-md" />
          <h1 className="text-3xl font-bold text-[#0F172A] mb-2">Welcome to Kintsu</h1>
          <p className="text-xs font-mono text-slate-400 mb-6">({import.meta.env.VITE_COMMIT_HASH || 'local'})</p>
          <p className="text-slate-500 mb-8">
            Your private forensic recovery workspace.
            Connect your Google Drive to begin building your Hopper.
          </p>

          <button
            onClick={handleLogin}
            className="w-full py-3 px-6 bg-[#0F172A] text-white rounded-xl font-bold hover:bg-slate-800 transition-all flex items-center justify-center gap-3"
          >
            <Lock className="w-5 h-5" />
            Connect Google Drive
          </button>
          <p className="mt-4 text-xs text-slate-400">
            We only access files created by Kintsu. Your existing data remains private.
          </p>
        </div>
      </div>
    );
  }

  const isGmailFolder = breadcrumbs.some(b => b.name === 'Gmail');

  // --- Main Interface ---
  return (
    <div className="min-h-screen bg-[#F8FAFC] font-sans text-slate-900 flex flex-col">

      {/* Top Navigation */}
      <nav className="bg-white border-b border-slate-200 px-6 py-4 sticky top-0 z-20">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <img src="/kintsu-icon.jpeg" alt="Kintsu Logo" className="w-10 h-10 rounded-lg object-cover shadow-sm border border-slate-100" />
            <div>
              <h1 className="text-xl font-bold tracking-tight text-[#0F172A]">Kintsu</h1>
              <p className="text-xs text-slate-500 uppercase tracking-wider font-medium">Forensic Recovery</p>
            </div>
          </div>

          <div className="flex items-center gap-6">
            {/* Timeline */}
            <div className="hidden md:flex items-center gap-1">
              <PhaseBadge step={1} label="Stabilize" current={currentPhase} />
              <PhaseBadge step={2} label="Collect" current={currentPhase} />
              <PhaseBadge step={3} label="Reconstruct" current={currentPhase} />
              <PhaseBadge step={4} label="Maximize" current={currentPhase} />
            </div>



            <button onClick={handleLogout} className="text-slate-400 hover:text-slate-600">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 max-w-5xl mx-auto w-full px-6 py-12">

        <div className="mb-12 text-center">
          <span className="inline-block px-3 py-1 bg-blue-50 text-[#0F172A] text-xs font-bold uppercase tracking-widest rounded-full mb-3">
            Phase 2: The Raw Data Dump
          </span>
          <h2 className="text-4xl font-bold text-[#0F172A] mb-4">Let's gather the pieces.</h2>
          <p className="text-slate-500 max-w-2xl mx-auto text-lg leading-relaxed">
            Your "Hopper" has been created in your Google Drive. Drop your files there.
          </p>
        </div>

        {/* Drive Browser */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden mb-12">
          {/* Browser Header */}
          <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-600">
              <HardDrive className="w-4 h-4" />
              {breadcrumbs.map((crumb, i) => (
                <div
                  key={crumb.id}
                  className="flex items-center gap-2"
                  onClick={() => handleBreadcrumbClick(i)}
                >
                  {i > 0 && <ChevronRight className="w-3 h-3 text-slate-400" />}
                  <span className={cn(
                    i === breadcrumbs.length - 1
                      ? "text-[#0F172A] font-bold cursor-default"
                      : "cursor-pointer hover:text-[#D4AF37] hover:underline transition-colors"
                  )}>
                    {crumb.name}
                  </span>
                </div>
              ))}
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleCreateFolder}
                className="p-2 hover:bg-white rounded-lg text-slate-500 transition-colors"
                title="New Folder"
              >
                <Plus className="w-4 h-4" />
              </button>
              {/* Scan All Button */}
              <button
                onClick={handleScan}
                disabled={isScanning}
                className={cn(
                  "p-2 hover:bg-white rounded-lg transition-colors",
                  isScanning ? "text-[#D4AF37] animate-spin" : "text-slate-500"
                )}
                title="Scan All Drive Files"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Browser Content */}
          <div className="p-6 min-h-[200px]">
            {browserLoading ? (
              <div className="flex justify-center py-10">
                <Loader2 className="w-6 h-6 animate-spin text-slate-300" />
              </div>
            ) : driveItems.length === 0 ? (
              isGmailFolder ? (
                <TakeoutWizard userId="user-default" />
              ) : (
                <div className="text-center py-10 text-slate-400 border-2 border-dashed border-slate-100 rounded-lg">
                  Empty Folder
                </div>
              )
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {/* Back Button (if not at root) */}
                {breadcrumbs.length > 1 && (
                  <div
                    onClick={handleNavigateUp}
                    className="p-4 rounded-lg border border-dashed border-slate-200 flex flex-col items-center justify-center gap-2 cursor-pointer hover:bg-slate-50 text-slate-400"
                  >
                    <CornerLeftUp className="w-6 h-6" />
                    <span className="text-xs font-medium">Back</span>
                  </div>
                )}

                {driveItems.map(item => {
                  const isFolder = item.mimeType === 'application/vnd.google-apps.folder';
                  return (
                    <div
                      key={item.id}
                      onClick={() => isFolder ? handleNavigate(item.id, item.name) : window.open(item.webViewLink, '_blank')}
                      className={cn(
                        "p-4 rounded-lg border flex flex-col items-center justify-center gap-3 text-center transition-all group",
                        isFolder
                          ? "cursor-pointer hover:border-[#D4AF37] hover:bg-orange-50/10 border-slate-200"
                          : "cursor-pointer hover:border-blue-300 hover:bg-blue-50/10 border-slate-100 bg-slate-50 opacity-75"
                      )}
                    >
                      {isFolder
                        ? <Folder className="w-8 h-8 text-[#D4AF37]" />
                        : <FileText className="w-8 h-8 text-slate-400" />
                      }
                      <span className="text-xs font-medium truncate w-full px-2">
                        {item.name}
                      </span>
                    </div>
                  )
                })}
              </div>
            )}
          </div>

          {/* Browser Footer (Actions) */}
          <div className="bg-slate-50 px-6 py-4 border-t border-slate-200 flex justify-center">
            {/* 1. Root Upload Restriction: Only show if breadcrumbs > 1 (i.e., inside a subfolder, not root Hopper) */}
            {breadcrumbs.length > 1 ? (
              <label
                className={cn(
                  "inline-flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-colors cursor-pointer",
                  !isUploading
                    ? "bg-[#0F172A] text-white hover:bg-slate-800"
                    : "bg-slate-200 text-slate-400 cursor-not-allowed"
                )}
              >
                {isUploading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <UploadCloud className="w-4 h-4" />
                    Upload File Here
                  </>
                )}
                <input
                  type="file"
                  className="hidden"
                  disabled={isUploading}
                  onChange={handleFileUpload}
                />
              </label>
            ) : (
              <div className="text-sm text-slate-400 flex items-center gap-2 italic">
                <Lock className="w-4 h-4" />
                Open a folder above to upload files
              </div>
            )}
          </div>
        </div>

        {/* Refinery Feed */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-[#0F172A] flex items-center gap-2">
              Refinery Stream
              {loading && <Loader2 className="w-4 h-4 animate-spin text-slate-400" />}
            </h3>
            <span className="text-sm text-slate-500 font-medium">
              {shards.filter(s => s.status === 'refined').length} Golden Records Found
            </span>
          </div>

          <div className="grid gap-4">
            {shards.map((shard) => (
              <RefinedShardItem key={shard.id} shard={shard} getIcon={getIcon} />
            ))}
          </div>
        </div>

      </main>
    </div>
  );
}

export default App;