import { useState, useEffect } from 'react';
import { Package, FileText, Image, CreditCard, HardDrive, Loader2, LogOut, Lock, RefreshCw, HelpCircle, X } from 'lucide-react';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';
import { Timestamp } from 'firebase/firestore';
import { DriveService } from './DriveService';
import { HopperList } from './components/Hopper/HopperList';
import { FilePreviewModal } from './components/Hopper/FilePreviewModal';
import type { DriveItem } from './components/Hopper/types';

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
  webViewLink?: string;
  createdAt: Timestamp;
}

// --- Utils ---
function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs));
}

// --- Components ---

const TakeoutHelpModal = ({ onClose }: { onClose: () => void }) => (
  <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 animate-in fade-in">
    <div className="bg-white rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
      <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between sticky top-0">
        <h3 className="font-bold text-lg text-slate-900 flex items-center gap-2">
          <HardDrive className="w-5 h-5 text-[#D4AF37]" />
          How to Export from Gmail
        </h3>
        <button onClick={onClose} className="p-2 hover:bg-slate-200 rounded-full transition-colors">
          <X className="w-5 h-5 text-slate-400" />
        </button>
      </div>

      <div className="p-6 overflow-y-auto">
        <div className="prose prose-slate max-w-none">
          <p className="lead text-lg text-slate-600 mb-6">
            Kintsu uses <strong>Google Takeout</strong> to securely process your email history without requiring full inbox access.
          </p>

          <ol className="space-y-6 list-decimal list-outside ml-5">
            <li className="pl-2">
              <strong className="block text-slate-900 mb-1">Go to Google Takeout</strong>
              <a href="https://takeout.google.com" target="_blank" rel="noreferrer" className="text-blue-600 hover:underline font-medium">
                takeout.google.com
              </a>
            </li>

            <li className="pl-2">
              <strong className="block text-slate-900 mb-1">Deselect All</strong>
              <span className="text-slate-500">Click "Deselect all" at the top of the list. We only need Mail.</span>
            </li>

            <li className="pl-2">
              <strong className="block text-slate-900 mb-1">Select "Mail"</strong>
              <span className="text-slate-500">Scroll down to "Mail" and check the box.</span>
              <div className="mt-2 bg-blue-50 p-3 rounded-lg text-sm text-blue-800 border border-blue-100">
                <strong>Tip:</strong> Click "All Mail data included" to filter for specific labels (e.g. "Purchases", "Amazon") to reduce file size.
              </div>
            </li>

            <li className="pl-2">
              <strong className="block text-slate-900 mb-1">Create Export</strong>
              <span className="text-slate-500">Click "Next step", keep "Export once" selected, and click "Create export".</span>
            </li>

            <li className="pl-2">
              <strong className="block text-slate-900 mb-1">Download & Upload</strong>
              <span className="text-slate-500">
                When emailed the link, download the <strong>.zip</strong> file.
                Then, upload it to the <strong>Kintsu/Hopper/Gmail</strong> folder in your Google Drive.
              </span>
            </li>
          </ol>
        </div>
      </div>

      <div className="p-4 border-t border-slate-100 bg-slate-50 flex justify-end">
        <button onClick={onClose} className="px-6 py-2 bg-[#0F172A] text-white rounded-xl font-bold hover:bg-slate-800 transition-colors">
          Got it
        </button>
      </div>
    </div>
  </div>
);

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

  const handleClick = () => {
    if (shard.webViewLink) {
      window.open(shard.webViewLink, '_blank');
    }
  };

  return (
    <div
      onClick={handleClick}
      className={cn(
        "relative overflow-hidden rounded-xl border transition-all p-5 flex gap-5 group bg-white cursor-pointer hover:bg-slate-50",
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
          <h4 className={cn("font-bold truncate pr-4 group-hover:text-[#D4AF37] transition-colors", isRefined ? "text-slate-900" : "text-slate-500")}>
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

  const [currentFolderId, setCurrentFolderId] = useState<string | null>(null);
  const [previewFile, setPreviewFile] = useState<DriveItem | null>(null);

  // Use localhost for local testing as requested by user
  const API_BASE = import.meta.env.VITE_API_BASE;

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

  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [showTakeoutHelp, setShowTakeoutHelp] = useState(false);

  const handleScan = async () => {
    setIsScanning(true);
    setStatusMessage("Scanning Hopper...");
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const isDebug = urlParams.get('debug') === 'on';

      const files = await DriveService.listHopperFiles();
      const existingIds = new Set(shards.map(s => s.id));

      let foundNew = false;
      for (const file of files) {
        const shardId = `drive_${file.id}`;
        // Process if new OR if it's a ZIP file (we might want to re-process zips if user asks, or check if processed)
        // For now, let's just process whatever isn't tracked as a "shard" or just force process zips?
        // The shard logic keeps track of processed files.
        if (!existingIds.has(shardId) || file.name.endsWith('.zip')) {
          foundNew = true;
          setStatusMessage(`Processing: ${file.name}`);
          console.log(`Sending for refinement: ${file.name}${isDebug ? ' (DEBUG ON)' : ''}`);

          const apiUrl = new URL(`${API_BASE}/api/refine-drive-file`);

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
      if (!foundNew) setStatusMessage("No new files found.");
      else setStatusMessage("Scan complete.");

      // Refresh list
      setTimeout(() => {
        refreshRefineryStream();
        setStatusMessage(null);
      }, 2000);

    } catch (e) {
      console.error("Scan error:", e);
      setStatusMessage("Scan failed.");
    } finally {
      setIsScanning(false);
    }
  };

  const handleLogin = async () => {
    try {
      await DriveService.signIn();
      setIsSignedIn(true);

      setStatusMessage("Initializing Hopper...");
      await DriveService.ensureHopperStructure((msg) => setStatusMessage(msg));
      setStatusMessage(null);

      const kintsuId = await DriveService.findFolder('Kintsu');
      if (kintsuId) {
        const hopperId = await DriveService.findFolder('Hopper', kintsuId);
        if (hopperId) {
          setCurrentFolderId(hopperId);
        }
      }

    } catch (error) {
      console.error("Login failed:", error);
      setStatusMessage("Login failed.");
    }
  };

  const handleLogout = async () => {
    await DriveService.signOut();
    setIsSignedIn(false);
    setCurrentFolderId(null);
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
          <p className="text-xs font-mono text-slate-400 mb-6">(Version_0.02b)</p>
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
            <div className="hidden md:flex items-center gap-1">
              <PhaseBadge step={1} label="Stabilize" current={currentPhase} />
              <PhaseBadge step={2} label="Collect" current={currentPhase} />
              <PhaseBadge step={3} label="Reconstruct" current={currentPhase} />
              <PhaseBadge step={4} label="Maximize" current={currentPhase} />
            </div>

            <button onClick={() => setShowTakeoutHelp(true)} className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded-lg transition-colors text-sm font-medium mr-2">
              <HelpCircle className="w-4 h-4" />
              <span className="hidden md:inline">Takeout Help</span>
            </button>
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

        {/* Drive Browser (Hopper List) */}
        {currentFolderId && (
          <div className="mb-12">
            <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">

              {/* Status Message Area */}
              <div className="flex-1">
                {statusMessage ? (
                  <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg border border-blue-100 animate-in fade-in slide-in-from-left-4">
                    <Loader2 className="w-4 h-4 animate-spin shrink-0" />
                    <span className="text-sm font-medium">{statusMessage}</span>
                  </div>
                ) : (
                  <div className="text-sm text-slate-400 italic">
                    Ready to scan. Upload your files to Drive.
                  </div>
                )}
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => setShowTakeoutHelp(true)}
                  className="flex items-center gap-2 px-4 py-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors text-sm font-medium"
                >
                  <HelpCircle className="w-4 h-4" />
                  How to use Takeout?
                </button>

                <button
                  onClick={handleScan}
                  disabled={isScanning}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg shadow-sm text-sm font-medium transition-all hover:border-[#D4AF37] hover:text-[#D4AF37]",
                    isScanning && "text-[#D4AF37] border-[#D4AF37]"
                  )}
                >
                  <RefreshCw className={cn("w-4 h-4", isScanning && "animate-spin")} />
                  {isScanning ? "Scanning..." : "Scan Hopper"}
                </button>
              </div>
            </div>

            <HopperList
              rootFolderId={currentFolderId}
              onFileSelect={setPreviewFile}
              className="min-h-[500px]"
            />
          </div>
        )}

        <FilePreviewModal file={previewFile} onClose={() => setPreviewFile(null)} />
        {showTakeoutHelp && <TakeoutHelpModal onClose={() => setShowTakeoutHelp(false)} />}

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