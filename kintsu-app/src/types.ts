// Phase 1: Data Models

export type SourceType = 'Amazon' | 'Gmail' | 'Banking' | 'Photos' | 'Upload';

export interface Shard {
  id: string;
  sourceType: SourceType;
  filePath: string; // Path relative to Hopper root
  fileName: string;
  extractedDate?: string;
  status: 'unprocessed' | 'processing' | 'linked' | 'error';
  rawText?: string; // For preview
}

export interface RefineryItem {
  id: string;
  name: string;
  totalValue: number;
  shards: string[]; // Array of Shard IDs
  confidenceScore: number; // 0-100
  category?: string;
}

export interface FolderStats {
    source: SourceType;
    count: number;
    status: 'healthy' | 'scanning' | 'error';
}
