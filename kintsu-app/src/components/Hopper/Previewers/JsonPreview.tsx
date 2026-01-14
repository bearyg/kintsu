import { useState, useEffect } from 'react';
import { Loader2, ChevronRight, ChevronDown } from 'lucide-react';
import { DriveService } from '../../../DriveService';

interface JsonPreviewProps {
    fileId: string;
}

const JsonNode = ({ name, value, depth = 0 }: { name?: string, value: any, depth?: number }) => {
    const [expanded, setExpanded] = useState(depth < 2); // Auto-expand top levels
    const isObject = value !== null && typeof value === 'object';
    const isArray = Array.isArray(value);
    const isEmpty = isObject && Object.keys(value).length === 0;

    if (!isObject) {
        return (
            <div className="font-mono text-sm leading-6 hover:bg-slate-50 px-2 rounded flex">
                {name && <span className="text-purple-600 mr-2 min-w-[100px] shrink-0">{name}:</span>}
                <span className={
                    typeof value === 'string' ? "text-green-600 break-all" :
                        typeof value === 'number' ? "text-blue-600" :
                            "text-slate-600"
                }>
                    {JSON.stringify(value)}
                </span>
            </div>
        );
    }

    return (
        <div className="font-mono text-sm">
            <div
                onClick={() => !isEmpty && setExpanded(!expanded)}
                className={`flex items-center px-2 py-1 rounded cursor-pointer hover:bg-slate-100 ${isEmpty ? 'cursor-default' : ''}`}
            >
                <span className="w-4 h-4 mr-1 flex items-center justify-center text-slate-400">
                    {!isEmpty && (expanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />)}
                </span>
                {name && <span className="text-purple-700 font-semibold mr-2">{name}:</span>}
                <span className="text-slate-500">
                    {isArray ? `Array(${value.length})` : `Object {${Object.keys(value).length}}`}
                </span>
            </div>

            {expanded && !isEmpty && (
                <div className="ml-6 border-l border-slate-200 pl-2">
                    {Object.entries(value).map(([k, v]) => (
                        <JsonNode key={k} name={isArray ? undefined : k} value={v} depth={depth + 1} />
                    ))}
                </div>
            )}
        </div>
    );
};

export const JsonPreview = ({ fileId }: JsonPreviewProps) => {
    const [data, setData] = useState<any | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchContent = async () => {
            setLoading(true);
            setError(null);
            try {
                const text = await DriveService.getFileContent(fileId);
                setData(JSON.parse(text));
            } catch (error) {
                console.error("Failed to load JSON content:", error);
                setError("Invalid JSON or failed to load.");
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
                <span>Parsing JSON...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-10 text-center text-red-500 bg-red-50 rounded-lg border border-red-100">
                {error}
            </div>
        )
    }

    return (
        <div className="w-full h-full bg-white rounded-lg border border-slate-200 overflow-auto p-4">
            <JsonNode value={data} />
        </div>
    );
};
