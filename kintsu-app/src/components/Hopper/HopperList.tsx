import { useState, useEffect, useRef } from 'react';
import {
    Folder,
    FileText,
    Image,
    HardDrive,
    ChevronRight,
    CornerLeftUp,
    Plus,
    UploadCloud,
    Loader2,
    LayoutGrid,
    List as ListIcon,
    Trash2,
    Ban
} from 'lucide-react';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';
import { DriveService } from '../../DriveService';
import type { DriveItem, Breadcrumb, ViewMode, HopperListProps } from './types';
import { ReportGenerator } from '../Reporting/ReportGenerator';

function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

export const HopperList = ({ rootFolderId, onNavigate, onFileSelect, className }: HopperListProps) => {
    const [currentFolderId, setCurrentFolderId] = useState<string>(rootFolderId);
    const [items, setItems] = useState<DriveItem[]>([]);
    const [breadcrumbs, setBreadcrumbs] = useState<Breadcrumb[]>([{ id: rootFolderId, name: 'Hopper' }]);
    const [showReportGenerator, setShowReportGenerator] = useState(false);
    const [loading, setLoading] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [viewMode, setViewMode] = useState<ViewMode>('grid');

    const fileInputRef = useRef<HTMLInputElement>(null);

    // --- Effects ---

    useEffect(() => {
        // If rootFolderId changes from props (e.g. initial load), reset
        if (rootFolderId) {
            setCurrentFolderId(rootFolderId);
            // We might want to fetch the folder name if it's not "Hopper", but for now assume root is Hopper
            setBreadcrumbs([{ id: rootFolderId, name: 'Hopper' }]);
        }
    }, [rootFolderId]);

    useEffect(() => {
        if (!currentFolderId) return;
        loadItems(currentFolderId);
    }, [currentFolderId]);

    // --- Actions ---

    const loadItems = async (folderId: string) => {
        setLoading(true);
        if (window.location.search.includes('debug=on')) {
            console.log(`[HopperList] Loading items for folder: ${folderId}`);
        }

        try {
            const driveItems = await DriveService.listChildren(folderId);
            setItems(driveItems);
        } catch (error) {
            console.error("[HopperList] Error loading items:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleNavigate = (folderId: string, folderName: string) => {
        if (window.location.search.includes('debug=on')) {
            console.log(`[HopperList] Navigating to: ${folderName} (${folderId})`);
        }
        setCurrentFolderId(folderId);
        setBreadcrumbs(prev => [...prev, { id: folderId, name: folderName }]);
        if (onNavigate) onNavigate(folderId);
    };

    const handleBreadcrumbClick = (index: number) => {
        if (index === breadcrumbs.length - 1) return;
        const target = breadcrumbs[index];
        setBreadcrumbs(prev => prev.slice(0, index + 1));
        setCurrentFolderId(target.id);
    };

    const handleNavigateUp = () => {
        if (breadcrumbs.length <= 1) return;
        const parent = breadcrumbs[breadcrumbs.length - 2];
        setBreadcrumbs(prev => prev.slice(0, prev.length - 1));
        setCurrentFolderId(parent.id);
    };

    const handleCreateFolder = async () => {
        const name = prompt("Enter folder name:");
        if (!name) return;

        try {
            await DriveService.createFolder(name, currentFolderId);
            loadItems(currentFolderId); // Refresh
        } catch (error) {
            console.error("[HopperList] Error creating folder:", error);
        }
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files?.length) return;
        const file = e.target.files[0];

        setIsUploading(true);
        try {
            await DriveService.uploadFile(file, currentFolderId);
            loadItems(currentFolderId);
        } catch (error) {
            console.error("[HopperList] Error uploading file:", error);
            alert("Upload failed");
        } finally {
            setIsUploading(false);
            e.target.value = "";
        }
    };


    const handleExclude = async (e: React.MouseEvent, file: DriveItem) => {
        e.stopPropagation();
        if (!confirm(`Exclude "${file.name}"? This will move it to a _excluded folder.`)) return;

        try {
            // Optimistic update or loading state could go here
            await DriveService.excludeFile(file.id, currentFolderId);
            loadItems(currentFolderId);
        } catch (error) {
            console.error("Error excluding file:", error);
            alert("Failed to exclude file.");
        }
    };

    const handleDelete = async (e: React.MouseEvent, file: DriveItem) => {
        e.stopPropagation();
        if (!confirm(`Delete "${file.name}"? This will move it to a _deleted folder.`)) return;

        try {
            await DriveService.deleteFile(file.id, currentFolderId);
            loadItems(currentFolderId);
        } catch (error) {
            console.error("Error deleting file:", error);
            alert("Failed to delete file.");
        }
    };

    // --- Renders ---

    const getIcon = (mimeType: string) => {
        if (mimeType === 'application/vnd.google-apps.folder') return <Folder className="w-8 h-8 text-[#D4AF37]" />;
        if (mimeType.includes('image')) return <Image className="w-8 h-8 text-blue-400" />;
        return <FileText className="w-8 h-8 text-slate-400" />;
    };

    const renderGridItem = (item: DriveItem) => {
        const isFolder = item.mimeType === 'application/vnd.google-apps.folder';
        return (
            <div
                key={item.id}
                onClick={() => isFolder ? handleNavigate(item.id, item.name) : onFileSelect?.(item)}
                className={cn(
                    "group relative p-4 rounded-xl border transition-all cursor-pointer flex flex-col items-center gap-3 text-center",
                    isFolder
                        ? "bg-white border-slate-200 hover:border-[#D4AF37] hover:shadow-md hover:shadow-orange-50/50"
                        : "bg-slate-50 border-slate-100 hover:bg-white hover:border-blue-200 hover:shadow-sm"
                )}
            >
                {getIcon(item.mimeType)}
                <span className="text-sm font-medium text-slate-700 truncate w-full px-1 group-hover:text-slate-900">
                    {item.name}
                </span>

                {/* Quick Actions Overlay (Desktop) */}
                {!isFolder && (
                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                        <button
                            onClick={(e) => handleExclude(e, item)}
                            title="Exclude"
                            className="p-1 hover:bg-slate-100 rounded text-slate-400 hover:text-orange-400 bg-white/80 backdrop-blur-sm border border-slate-200 shadow-sm"
                        >
                            <Ban className="w-3 h-3" />
                        </button>
                        <button
                            onClick={(e) => handleDelete(e, item)}
                            title="Delete"
                            className="p-1 hover:bg-slate-100 rounded text-slate-400 hover:text-red-400 bg-white/80 backdrop-blur-sm border border-slate-200 shadow-sm"
                        >
                            <Trash2 className="w-3 h-3" />
                        </button>
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className={cn("flex flex-col h-full bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden", className)}>
            {/* Header / Toolbar */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/50">

                {/* Breadcrumbs */}
                <div className="flex items-center gap-2 text-sm text-slate-600 overflow-hidden">
                    <HardDrive className="w-4 h-4 text-slate-400 shrink-0" />
                    {breadcrumbs.map((crumb, i) => (
                        <div key={crumb.id} className="flex items-center gap-1 shrink-0">
                            {i > 0 && <ChevronRight className="w-3 h-3 text-slate-300" />}
                            <span
                                onClick={() => handleBreadcrumbClick(i)}
                                className={cn(
                                    "transition-colors truncate max-w-[150px]",
                                    i === breadcrumbs.length - 1
                                        ? "font-bold text-slate-900 cursor-default"
                                        : "cursor-pointer hover:text-[#D4AF37] hover:underline"
                                )}
                            >
                                {crumb.name}
                            </span>
                        </div>
                    ))}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                    <div className="flex bg-slate-100 rounded-lg p-1 hidden sm:flex">
                        <button
                            onClick={() => setViewMode('grid')}
                            className={cn("p-1.5 rounded-md transition-all", viewMode === 'grid' ? "bg-white shadow text-slate-900" : "text-slate-400 hover:text-slate-600")}
                        >
                            <LayoutGrid className="w-4 h-4" />
                        </button>
                        <button
                            onClick={() => setViewMode('list')}
                            className={cn("p-1.5 rounded-md transition-all", viewMode === 'list' ? "bg-white shadow text-slate-900" : "text-slate-400 hover:text-slate-600")}
                        >
                            <ListIcon className="w-4 h-4" />
                        </button>
                    </div>

                    <div className="w-px h-6 bg-slate-200 mx-1 hidden sm:block" />

                    <button
                        onClick={handleCreateFolder}
                        className="p-2 text-slate-500 hover:bg-white hover:text-[#D4AF37] rounded-lg transition-colors"
                        title="New Folder"
                    >
                        <Plus className="w-5 h-5" />
                    </button>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex gap-2 w-full md:w-auto">
                <button
                    onClick={() => setShowReportGenerator(true)}
                    className="flex items-center justify-center gap-2 px-4 py-2 bg-[#0F172A] text-white rounded-lg hover:bg-slate-800 transition-colors shadow-sm text-sm font-bold"
                >
                    <FileText className="w-4 h-4" />
                    <span className="hidden md:inline">Generate Report</span>
                </button>

                <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isUploading}
                    className="flex items-center justify-center gap-2 px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors shadow-sm text-sm font-medium"
                >
                    {isUploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <UploadCloud className="w-4 h-4" />}
                    <span className="hidden md:inline">Upload Files</span>
                </button>
                <input
                    type="file"
                    ref={fileInputRef}
                    className="hidden"
                    onChange={handleFileUpload}
                    disabled={isUploading}
                />
            </div>
            <div className="flex-1 p-6 overflow-y-auto min-h-[300px]">
                {loading ? (
                    <div className="h-full flex flex-col items-center justify-center text-slate-400 gap-3">
                        <Loader2 className="w-8 h-8 animate-spin text-[#D4AF37]" />
                        <span className="text-sm">Loading Hopper contents...</span>
                    </div>
                ) : items.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-slate-400 border-2 border-dashed border-slate-100 rounded-xl bg-slate-50/50">
                        <p>This folder is empty</p>
                    </div>
                ) : (
                    <div className={cn(
                        viewMode === 'grid'
                            ? "grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4"
                            : "flex flex-col gap-2"
                    )}>
                        {/* Back Button (In-Grid) */}
                        {breadcrumbs.length > 1 && viewMode === 'grid' && (
                            <div
                                onClick={handleNavigateUp}
                                className="group p-4 rounded-xl border border-dashed border-slate-200 hover:border-slate-300 hover:bg-slate-50 cursor-pointer flex flex-col items-center justify-center gap-2 text-slate-400"
                            >
                                <CornerLeftUp className="w-6 h-6 group-hover:-translate-y-1 transition-transform" />
                                <span className="text-xs font-medium">Back</span>
                            </div>
                        )}

                        {items.map(item => renderGridItem(item))}
                    </div>
                )}
            </div>

            {/* Footer / Upload Area */}
            <div className="p-4 border-t border-slate-100 bg-slate-50/30">
                {/* Only show upload if not at root (Hopper) level, to encourage organization */}
                {breadcrumbs.length > 1 ? (
                    <label className={cn(
                        "flex items-center justify-center gap-2 w-full py-3 rounded-xl border border-dashed transition-all cursor-pointer font-medium text-sm",
                        isUploading
                            ? "bg-slate-50 border-slate-200 text-slate-400 cursor-wait"
                            : "border-[#D4AF37]/50 bg-orange-50/50 text-[#D4AF37] hover:bg-orange-50 hover:border-[#D4AF37] hover:shadow-sm"
                    )}>
                        {isUploading ? (
                            <>
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Uploading...
                            </>
                        ) : (
                            <>
                                <UploadCloud className="w-4 h-4" />
                                Upload File to "{breadcrumbs[breadcrumbs.length - 1].name}"
                            </>
                        )}
                        <input
                            type="file"
                            className="hidden"
                            onChange={handleFileUpload}
                            disabled={isUploading}
                        />
                    </label>
                ) : (
                    <p className="text-center text-xs text-slate-400 py-2">
                        Navigate to a subfolder to upload files
                    </p>
                )}
            </div>
            {/* Report Generator Modal */}
            {showReportGenerator && (
                <ReportGenerator
                    folderId={rootFolderId}
                    onClose={() => setShowReportGenerator(false)}
                />
            )}
        </div>
    );
};
