import pandas as pd
import os
from .base import BaseProcessor
from typing import List, Dict, Any

# --- Defaults ---
DEFAULT_MIN_PRICE = 15.00

DEFAULT_IGNORE_KEYWORDS = [
    # Digital / Service
    'kindle edition', 'audible', 'prime video', 'gift card', 'egift',
    'protection plan', 'warranty', 'subscription', 'membership', 'service',
    'appstore', 'download',
    
    # Grocery / Pantry / Consumables
    'fl oz', 'ounce', ' oz ', ' lb ', 'pound', 'count', 'pack of',
    'vitamin', 'supplement', 'protein', 'capsule', 'tablet',
    'coffee', 'tea', 'sugar', 'spice', 'oil', 'sauce', 'snack', 'candy',
    'paper towel', 'toilet paper', 'tissue', 'napkin', 'wipes',
    'detergent', 'soap', 'shampoo', 'conditioner', 'toothpaste', 'lotion', 'cream',
    'deodorant', 'razor', 'blade', 'diaper',
    'trash bag', 'battery', 'batteries'
]

# Exceptions to the rule (If these words exist, KEEP it even if it matches an ignore keyword)
ASSET_KEYWORDS = [
    'rechargeable', 'tool', 'device', 'appliance', 'kit'
]

class AmazonProcessor(BaseProcessor):
    def can_process(self, file_path: str, source_type: str) -> bool:
        if source_type == 'Amazon':
            return True
        if 'Retail.OrderHistory' in file_path:
            return True
        return False

    def is_likely_asset(self, description: str, price: float) -> bool:
        desc_lower = description.lower()
        
        # 1. Check Exceptions (Assets that might look like consumables)
        for asset_word in ASSET_KEYWORDS:
            if asset_word in desc_lower:
                return True

        # 2. Check Price Floor
        if price < DEFAULT_MIN_PRICE:
            return False

        # 3. Check Ignore List
        for keyword in DEFAULT_IGNORE_KEYWORDS:
            if keyword in desc_lower:
                return False
                
        return True

    def process(self, file_path: str, original_filename: str) -> List[Dict[str, Any]]:
        shards = []
        try:
            if not file_path.endswith('.csv'):
                print(f"[AmazonProcessor] Skipping non-CSV file: {file_path}")
                return []

            print(f"[AmazonProcessor] Analyzing {file_path}...")
            
            try:
                df = pd.read_csv(file_path)
            except Exception as e:
                print(f"[AmazonProcessor] Pandas read error: {e}")
                return []

            cols = df.columns.tolist()
            cols_lower = [c.lower() for c in cols]
            
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
                    
                    if 'returned' in status.lower() or 'cancelled' in status.lower():
                        continue
                        
                    try:
                        price = float(price_str)
                    except:
                        price = 0.0
                    
                    # --- ASSET TRIAGE ---
                    if not self.is_likely_asset(desc, price):
                        # Skip noise
                        continue

                    shard_data = {
                        "item_name": desc,
                        "total_amount": price,
                        "currency": "USD",
                        "date": date_str,
                        "merchant": "Amazon",
                        "confidence": "High", 
                        "category": "Uncategorized", 
                        "source_meta": {
                            "original_row": index,
                            "status": status,
                            "filter_method": "heuristic_v1"
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
