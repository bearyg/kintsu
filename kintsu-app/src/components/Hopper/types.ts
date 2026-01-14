export interface DriveItem {
    id: string;
    name: string;
    mimeType: string;
    webViewLink?: string;
    iconLink?: string;
    thumbnailLink?: string;
    parents?: string[];
    sourceType?: string; // e.g., 'Amazon', 'Gmail' - derived from parent folder name
}

export interface Breadcrumb {
    id: string;
    name: string;
}

export type ViewMode = 'list' | 'grid';

export interface HopperListProps {
    rootFolderId: string;
    onNavigate?: (folderId: string) => void;
    onFileSelect?: (file: DriveItem) => void;
    className?: string;
}
