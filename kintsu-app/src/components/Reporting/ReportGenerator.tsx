import { useState } from 'react';
import { FileText, Download, Loader2, CheckCircle, FileCheck } from 'lucide-react';
import { DriveService } from '../../DriveService';

interface ReportGeneratorProps {
    folderId: string;
    onClose: () => void;
}

export const ReportGenerator = ({ folderId, onClose }: ReportGeneratorProps) => {
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [formats, setFormats] = useState({
        pdf: true,
        csv: true,
        zip: false
    });

    const handleGenerate = async () => {
        setLoading(true);
        try {
            const selectedFormats = Object.entries(formats)
                .filter(([_, enabled]) => enabled)
                .map(([fmt]) => fmt);

            const API_BASE = import.meta.env.VITE_API_BASE;

            const response = await fetch(`${API_BASE}/api/reports/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    folderId,
                    reportName: 'Kintsu_Claim_Report',
                    formats: selectedFormats,
                    accessToken: DriveService.accessToken
                })
            });

            if (!response.ok) throw new Error('Generation failed');

            setSuccess(true);
        } catch (error) {
            console.error("Report generation failed:", error);
            alert("Failed to generate report. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    if (success) {
        return (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
                <div className="bg-white rounded-2xl p-8 max-w-md w-full text-center shadow-2xl">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4 text-green-600">
                        <CheckCircle className="w-8 h-8" />
                    </div>
                    <h3 className="text-2xl font-bold text-slate-900 mb-2">Report Generated!</h3>
                    <p className="text-slate-500 mb-6">
                        Your reports have been saved to the <strong>Reports</strong> folder in your Google Drive.
                    </p>
                    <button
                        onClick={onClose}
                        className="w-full py-3 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 transition-colors"
                    >
                        Close
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 animate-in fade-in">
            <div className="bg-white rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden">
                <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between">
                    <h3 className="font-bold text-lg text-slate-900 flex items-center gap-2">
                        <FileCheck className="w-5 h-5 text-[#D4AF37]" />
                        Generate Claim Report
                    </h3>
                    <button onClick={onClose} className="text-slate-400 hover:text-slate-600">✕</button>
                </div>

                <div className="p-6">
                    <p className="text-slate-500 mb-6 text-sm">
                        Select the formats you'd like to generate. Kintsu will compile your data and save these files to your Google Drive.
                    </p>

                    <div className="space-y-3 mb-8">
                        <label className="flex items-center p-4 border border-slate-200 rounded-xl cursor-pointer hover:bg-slate-50 transition-colors">
                            <input
                                type="checkbox"
                                checked={formats.pdf}
                                onChange={e => setFormats({ ...formats, pdf: e.target.checked })}
                                className="w-5 h-5 rounded border-slate-300 text-[#D4AF37] focus:ring-[#D4AF37]"
                            />
                            <div className="ml-4">
                                <span className="block font-bold text-slate-900">PDF Summary</span>
                                <span className="text-xs text-slate-400">Professional document for adjusters</span>
                            </div>
                            <FileText className="ml-auto w-5 h-5 text-slate-300" />
                        </label>

                        <label className="flex items-center p-4 border border-slate-200 rounded-xl cursor-pointer hover:bg-slate-50 transition-colors">
                            <input
                                type="checkbox"
                                checked={formats.csv}
                                onChange={e => setFormats({ ...formats, csv: e.target.checked })}
                                className="w-5 h-5 rounded border-slate-300 text-[#D4AF37] focus:ring-[#D4AF37]"
                            />
                            <div className="ml-4">
                                <span className="block font-bold text-slate-900">CSV Inventory</span>
                                <span className="text-xs text-slate-400">Spreadsheet compatible format</span>
                            </div>
                            <FileText className="ml-auto w-5 h-5 text-slate-300" />
                        </label>

                        <label className="flex items-center p-4 border border-slate-200 rounded-xl cursor-pointer hover:bg-slate-50 transition-colors">
                            <input
                                type="checkbox"
                                checked={formats.zip}
                                onChange={e => setFormats({ ...formats, zip: e.target.checked })}
                                className="w-5 h-5 rounded border-slate-300 text-[#D4AF37] focus:ring-[#D4AF37]"
                            />
                            <div className="ml-4">
                                <span className="block font-bold text-slate-900">Evidence Archive (ZIP)</span>
                                <span className="text-xs text-slate-400">Bundle of all source files</span>
                            </div>
                            <Download className="ml-auto w-5 h-5 text-slate-300" />
                        </label>
                    </div>

                    <button
                        onClick={handleGenerate}
                        disabled={loading || (!formats.pdf && !formats.csv && !formats.zip)}
                        className="w-full py-3 bg-[#0F172A] text-white rounded-xl font-bold hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
                    >
                        {loading ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                Generating...
                            </>
                        ) : (
                            <>
                                Generate Reports
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};
