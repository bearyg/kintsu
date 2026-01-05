import os
import tempfile
import shutil
import pandas as pd
from backend.processors.amazon import AmazonProcessor

def create_mock_data(work_dir):
    # 1. Create Mock Order History
    history_data = {
        "Order ID": ["111-0000001-0000001", "111-0000002-0000002", "111-0000003-0000003"],
        "Order Date": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "Title": ["Kept Item", "Returned Item", "Another Kept Item"],
        "Unit Price": ["$20.00", "$50.00", "$15.00"],
        "Order Status": ["Shipped", "Shipped", "Shipped"]
    }
    history_df = pd.DataFrame(history_data)
    history_file = os.path.join(work_dir, "Retail.OrderHistory.1.csv")
    history_df.to_csv(history_file, index=False)

    # 2. Create Mock Returns
    returns_data = {
        "OrderID": ["111-0000002-0000002"], # Matching the 2nd item above
        "Return Date": ["2024-01-10"]
    }
    returns_df = pd.DataFrame(returns_data)
    returns_file = os.path.join(work_dir, "Retail.OrdersReturned.1.csv")
    returns_df.to_csv(returns_file, index=False)

    return history_file, returns_file

def verify():
    work_dir = tempfile.mkdtemp()
    try:
        print(f"Creating mock data in {work_dir}...")
        history_file, returns_file = create_mock_data(work_dir)
        
        # Collect all files (simulating the unzipped directory)
        all_files = [history_file, returns_file]

        print(f"Found History: {os.path.basename(history_file)}")
        print(f"Found Returns: {os.path.basename(returns_file)}")

        # Initialize Processor
        processor = AmazonProcessor()
        
        # Process WITH context and DEBUG mode
        print("\n--- Processing WITH sibling_files (Debug Mode) ---")
        shards, excluded = processor.process(history_file, os.path.basename(history_file), sibling_files=all_files, debug=True)
        
        print(f"\nTotal shards extracted: {len(shards)}")
        print(f"Total excluded items: {len(excluded)}")
        
        # VERIFICATION LOGIC
        
        # 1. Check Shards (Valid Items)
        item_names = [s['item_name'] for s in shards]
        print(f"Extracted Items: {item_names}")
        
        if "Returned Item" in item_names:
            print("❌ FAILURE: Returned Item was NOT filtered out.")
        else:
            print("✅ SUCCESS: Returned Item was filtered out.")

        # Check Order ID in shards
        if all('order_id' in s for s in shards):
             print("✅ SUCCESS: Order ID present in all shards.")
        else:
             print("❌ FAILURE: Order ID missing in some shards.")

        # 2. Check Excluded Items
        print("\n--- Excluded Items Analysis ---")
        found_returned_reason = False
        for item in excluded:
            print(f"- {item['item_name']}: {item['reason']} (Order: {item.get('order_id')})")
            if item['item_name'] == "Returned Item" and item['reason'] == "found_in_returns_file":
                found_returned_reason = True
        
        if found_returned_reason:
            print("✅ SUCCESS: 'Returned Item' correctly logged as excluded due to returns file.")
        else:
            print("❌ FAILURE: 'Returned Item' not found in excluded list or wrong reason.")

    finally:
        shutil.rmtree(work_dir)

if __name__ == "__main__":
    verify()