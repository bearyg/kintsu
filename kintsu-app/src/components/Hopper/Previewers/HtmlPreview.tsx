import { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import { DriveService } from '../../../DriveService';

interface HtmlPreviewProps {
    fileId: string;
}

export const HtmlPreview = ({ fileId }: HtmlPreviewProps) => {
    const [content, setContent] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchContent = async () => {
            setLoading(true);
            try {
                const text = await DriveService.getFileContent(fileId);
                setContent(text);
            } catch (error) {
                console.error("Failed to load HTML content:", error);
                setContent("<div style='color:red; padding: 20px;'>Failed to load content.</div>");
            } finally {
                setLoading(false);
            }
        };

        if (fileId) {
            fetchContent();
        }
    }, [fileId]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-full p-10 text-slate-400 gap-3">
                <Loader2 className="w-8 h-8 animate-spin text-[#D4AF37]" />
                <span>Loading HTML preview...</span>
            </div>
        );
    }

    return (
        <div className="w-full h-full bg-white rounded-lg border border-slate-200 overflow-hidden">
            <iframe
                srcDoc={content || ''}
                title="HTML Preview"
                className="w-full h-full border-none"
                sandbox="allow-same-origin"
            />
        </div>
    );
};
