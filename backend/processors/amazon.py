import pandas as pd
import os
from .base import BaseProcessor
from typing import List, Dict, Any

class AmazonProcessor(BaseProcessor):
    def can_process(self, file_path: str, source_type: str) -> bool:
        # Check if source is explicitly Amazon or if file name matches Amazon pattern
        if source_type == 'Amazon':
            return True
        if 'Retail.OrderHistory' in file_path:
            return True
        return False

    def process(self, file_path: str, original_filename: str) -> List[Dict[str, Any]]:
        shards = []
        try:
            # We expect the file_path to point to the CSV (extracted from ZIP or uploaded directly)
            # If it's the ZIP itself, the main loop handles extraction.
            # This processor handles the specific CSV file.
            
            if not file_path.endswith('.csv'):
                print(f"[AmazonProcessor] Skipping non-CSV file: {file_path}")
                return []

            print(f"[AmazonProcessor] Analyzing {file_path}...")
            
            # Load CSV with pandas
            # Amazon CSVs can be messy, sometimes need specific encoding or error handling
            try:
                df = pd.read_csv(file_path)
            except Exception as e:
                print(f"[AmazonProcessor] Pandas read error: {e}")
                return []

            # Identify Columns (Amazon changes these occasionally)
            # 2024 Common Columns: 'Order Date', 'Item Description', 'Unit Price', 'Quantity', 'Status'
            
            cols = df.columns.tolist()
            # Normalize for matching
            cols_lower = [c.lower() for c in cols]
            
            # Helper to find column index
            def get_col(candidates):
                for c in candidates:
                    for i, col in enumerate(cols_lower):
                        if c in col: return cols[i]
                return None

            col_date = get_col(['order date', 'date'])
            col_desc = get_col(['item description', 'description', 'title', 'product name'])
            col_price = get_col(['unit price', 'price', 'amount'])
            col_status = get_col(['status', 'order status'])
            
            if not col_desc or not col_price:
                print("[AmazonProcessor] Critical columns not found. Falling back.")
                return []

            # Iterate Rows
            for index, row in df.iterrows():
                try:
                    desc = str(row[col_desc])
                    price_str = str(row[col_price]).replace('$', '').replace(',', '').strip()
                    date_str = str(row[col_date]) if col_date else None
                    status = str(row[col_status]) if col_status else 'Unknown'
                    
                    # 1. Filter: Skip Returns/Cancelled
                    if 'returned' in status.lower() or 'cancelled' in status.lower():
                        continue
                        
                    # 2. Filter: Valid Price
                    try:
                        price = float(price_str)
                    except:
                        price = 0.0
                    
                    if price <= 0: continue # Skip $0 items (digital content often)

                    # 3. Create Shard Data
                    shard_data = {
                        "item_name": desc,
                        "total_amount": price,
                        "currency": "USD", # Amazon exports usually implies currency, defaults to USD for now
                        "date": date_str,
                        "merchant": "Amazon",
                        "confidence": "High", # Structured data is high confidence
                        "category": "Uncategorized", # Enrichment step will fill this later
                        "source_meta": {
                            "original_row": index,
                            "status": status
                        }
                    }
                    shards.append(shard_data)
                    
                except Exception as row_err:
                    print(f"[AmazonProcessor] Row error: {row_err}")
                    continue

            print(f"[AmazonProcessor] Extracted {len(shards)} valid items.")
            return shards

        except Exception as e:
            print(f"[AmazonProcessor] Critical Error: {e}")
            return []
