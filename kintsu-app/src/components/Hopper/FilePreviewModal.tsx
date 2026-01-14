import { X, ExternalLink, Download, FileText, Code } from 'lucide-react';
import type { DriveItem } from './types';
import { HtmlPreview } from './Previewers/HtmlPreview';
import { JsonPreview } from './Previewers/JsonPreview';

interface FilePreviewModalProps {
    file: DriveItem | null;
    onClose: () => void;
}

export const FilePreviewModal = ({ file, onClose }: FilePreviewModalProps) => {
    if (!file) return null;

    const isHtml = file.mimeType === 'text/html' || file.name.endsWith('.html');
    const isJson = file.mimeType === 'application/json' || file.name.endsWith('.json');

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 md:p-8 animate-in fade-in duration-200">
            <div className="bg-white w-full max-w-5xl h-full max-h-[90vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden">

                {/* Header */}
                <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                    <div className="flex items-center gap-3 overflow-hidden">
                        <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center text-slate-400 shrink-0">
                            {isJson && <Code className="w-6 h-6 text-purple-500" />}
                            {isHtml && <FileText className="w-6 h-6 text-orange-500" />}
                            {!isJson && !isHtml && <FileText className="w-6 h-6" />}
                        </div>
                        <div className="min-w-0">
                            <h3 className="font-bold text-slate-900 truncate">{file.name}</h3>
                            <p className="text-xs text-slate-500 font-mono">ID: {file.id}</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        {file.webViewLink && (
                            <a
                                href={file.webViewLink}
                                target="_blank"
                                rel="noreferrer"
                                className="p-2 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-blue-500 transition-colors"
                                title="Open in Drive"
                            >
                                <ExternalLink className="w-5 h-5" />
                            </a>
                        )}
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-red-50 hover:text-red-500 rounded-lg text-slate-400 transition-colors"
                        >
                            <X className="w-6 h-6" />
                        </button>
                    </div>
                </div>

                {/* Content Body */}
                <div className="flex-1 overflow-hidden bg-slate-50 p-4 relative">
                    {isHtml && <HtmlPreview fileId={file.id} />}
                    {isJson && <JsonPreview fileId={file.id} />}

                    {!isHtml && !isJson && (
                        <div className="flex flex-col items-center justify-center h-full text-slate-400">
                            <p className="mb-4">Preview not available for this file type.</p>
                            {file.webViewLink && (
                                <a
                                    href={file.webViewLink}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2"
                                >
                                    <ExternalLink className="w-4 h-4" />
                                    Open in Google Drive
                                </a>
                            )}
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
};
