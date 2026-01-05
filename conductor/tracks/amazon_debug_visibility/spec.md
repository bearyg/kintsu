# Specification: Amazon Filtering Debug Visibility

## Context
Currently, the Amazon Processor filters out items based on "Returned" status or if the Order ID appears in the returns file. This happens silently (with only console logs). Users need visibility into *what* was excluded to verify the logic.

## Goals
1.  **Expose Excluded Items:** When `debug_mode` is enabled, collect all items that were filtered out (due to returns, low price, or keywords).
2.  **Persist Excluded Items:** Save these excluded items to a separate Firestore collection (e.g., `debug_excluded_items`) or a log.
3.  **Enhance Shard Data:** Add `order_id` to the valid shards stored in Firestore so they can be cross-referenced.

## Requirements
-   **Processor Update:** `AmazonProcessor.process` should return `(valid_shards, excluded_items)` OR include excluded items in the return with a special flag if `debug_mode` is on.
    -   *Decision:* Let's keep `process` returning `List[Dict]` but maybe modify the structure or add a side-channel?
    -   *Better approach:* Modify `process` to accept `debug_mode` flag. If true, return a tuple `(valid_shards, debug_info)`. But `BaseProcessor` defines `process` to return `List[Dict]`.
    -   *Refined approach:* Keep `process` signature simple for now, or update `BaseProcessor`. Given `BaseProcessor` is abstract, we can update the signature or allow `process` to return extended data.
    -   *Least invasive:* Update `AmazonProcessor` to accept `debug_mode` in `__init__` or `process`.
    -   *Chosen Path:* Update `process` to accept `debug_mode` (default False). Return `result` dictionary: `{'shards': [], 'excluded': []}`? No, that breaks existing contract.
    -   *Alternative:* Just log to a global context or pass a "collector" object?
    -   *Simpler:* `process` returns `List[Dict]`. We can append "excluded" items to the list but mark them with `status: 'excluded'`. Then `main.py` decides whether to save them to `shards` or `debug_log`.
    -   *Actually:* The requirement says "produce a list of excluded items... created as firestore".
    -   *Plan:*
        1.  Update `BaseProcessor.process` to accept `**kwargs` for flexibility (like `debug=False`).
        2.  Update `AmazonProcessor.process` to collect excluded items if `debug=True`.
        3.  Return both. Since Python is dynamic, we can return a tuple or a dict if we update the call site.
        4.  Let's update `process` to return `tuple(shards, excluded_items)`. This requires updating `BaseProcessor` and `main.py`.

-   **Data Structure:**
    -   Excluded Item: `{ 'item_name': ..., 'reason': 'returned'|'low_price'|'keyword', 'order_id': ..., 'raw_data': ... }`
    -   Valid Shard: Add field `order_id`.

## Out of Scope
-   UI for viewing these logs (backend only).
