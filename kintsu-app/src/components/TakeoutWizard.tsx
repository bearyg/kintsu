import { useState } from 'react';
import { Copy, ExternalLink, UploadCloud, CheckCircle, Loader2 } from 'lucide-react';
import { db } from '../firebase';
import { doc, onSnapshot } from 'firebase/firestore';

const API_BASE = "https://kintsu-backend-351476623210.us-central1.run.app"; // Should be env var

export const TakeoutWizard = ({ userId }: { userId: string }) => {
  const [step, setStep] = useState(1);
  const [jobId, setJobId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [uploading, setUploading] = useState(false);

  const QUERY = 'in:anywhere (receipt OR order OR "sales invoice") OR label:(^cob_sm_order OR ^cob_sm_cl_jc_order OR ^cob_sm_cl_llm_order)';

  const copyQuery = () => {
    navigator.clipboard.writeText(QUERY);
    alert("Query copied to clipboard!");
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length) return;
    const file = e.target.files[0];
    setUploading(true);

    try {
      // 1. Create Job
      const res = await fetch(`${API_BASE}/api/jobs/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId, fileName: file.name })
      });
      const { jobId, uploadUrl } = await res.json();
      setJobId(jobId);

      // 2. Upload to GCS
      await fetch(uploadUrl, {
        method: 'PUT',
        body: file,
        headers: { 'Content-Type': 'application/octet-stream' }
      });

      setStep(4);
      
      // 3. Listen for Progress
      const unsub = onSnapshot(doc(db, "jobs", jobId), (doc) => {
        const data = doc.data();
        if (data) {
            setProgress(data.progress || 0);
            setStatus(data.status || 'processing');
        }
      });
      
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    } finally {
      setUploading(false);
    }
  };

  if (step === 4) {
    return (
      <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 text-center">
        <h3 className="text-xl font-bold mb-4">Processing Your Archive</h3>
        <div className="w-full bg-slate-100 rounded-full h-4 mb-4">
            <div className="bg-[#D4AF37] h-4 rounded-full transition-all duration-500" style={{ width: `${progress}%` }}></div>
        </div>
        <p className="text-slate-500">{status} ({progress}%)</p>
        
        {progress === 100 && (
            <div className="mt-6 flex flex-col items-center gap-2 text-green-600">
                <CheckCircle className="w-8 h-8" />
                <span className="font-bold">Complete! Your emails are in the Hopper.</span>
                <button onClick={() => setStep(1)} className="mt-4 text-slate-400 text-sm hover:underline">Start Over</button>
            </div>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex justify-between items-center">
        <h3 className="font-bold text-slate-700">Import from Google Takeout</h3>
        <span className="text-xs font-mono text-slate-400">Step {step} of 3</span>
      </div>

      <div className="p-8">
        {step === 1 && (
            <div className="space-y-6">
                <div>
                    <h4 className="font-bold text-lg mb-2">1. Filter your Email</h4>
                    <p className="text-slate-600 mb-4">Copy this search query and paste it into Gmail to find your receipts.</p>
                    <div className="flex gap-2">
                        <code className="flex-1 bg-slate-100 p-3 rounded-lg text-xs font-mono border border-slate-200 overflow-x-auto">
                            {QUERY}
                        </code>
                        <button onClick={copyQuery} className="p-3 bg-white border border-slate-200 rounded-lg hover:bg-slate-50">
                            <Copy className="w-4 h-4 text-slate-600" />
                        </button>
                    </div>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg text-sm text-orange-800">
                    <strong>Tip:</strong> Create a Label named <code>Kintsu_Export</code> for these emails.
                </div>
                <button onClick={() => setStep(2)} className="w-full py-3 bg-[#0F172A] text-white rounded-lg font-bold">
                    Next: Export Data
                </button>
            </div>
        )}

        {step === 2 && (
            <div className="space-y-6">
                <div>
                    <h4 className="font-bold text-lg mb-2">2. Create Export</h4>
                    <p className="text-slate-600 mb-4">Go to Google Takeout and export <strong>only</strong> the "Mail" category (and your specific Label if possible).</p>
                    <a 
                        href="https://takeout.google.com/settings/takeout" 
                        target="_blank" 
                        className="inline-flex items-center gap-2 text-[#D4AF37] hover:underline font-medium"
                    >
                        Open Google Takeout <ExternalLink className="w-4 h-4" />
                    </a>
                </div>
                <button onClick={() => setStep(3)} className="w-full py-3 bg-[#0F172A] text-white rounded-lg font-bold">
                    I have the .zip file
                </button>
            </div>
        )}

        {step === 3 && (
            <div className="text-center space-y-6">
                <div className="border-2 border-dashed border-slate-200 rounded-xl p-10 flex flex-col items-center gap-4 hover:bg-slate-50 transition-colors">
                    <UploadCloud className="w-12 h-12 text-slate-300" />
                    <div>
                        <p className="font-medium text-slate-700">Drag and drop your Takeout .zip here</p>
                        <p className="text-sm text-slate-400">or click to browse (up to 2GB)</p>
                    </div>
                    <input 
                        type="file" 
                        className="absolute inset-0 opacity-0 cursor-pointer" 
                        onChange={handleUpload}
                        disabled={uploading}
                    />
                </div>
                {uploading && <div className="text-sm text-slate-500 flex items-center justify-center gap-2"><Loader2 className="w-4 h-4 animate-spin"/> Uploading...</div>}
            </div>
        )}
      </div>
    </div>
  );
};
