# Amazon Filtering Specification

## Context
When users request their data from Amazon, they receive a zip file containing multiple CSVs. The primary file `Retail.OrderHistory` contains all purchases. However, items that were returned are listed in a separate file: `Retail.OrdersReturned`.

## Problem
Currently, the `AmazonProcessor` only looks at `Retail.OrderHistory`. This leads to "false positives" where the system suggests items that the user no longer possesses because they were returned.

## Goal
Enhance the `AmazonProcessor` to be "zip-aware" or "context-aware". When processing an Amazon data dump, it should:
1.  Look for the `Retail.OrdersReturned` file in the same batch/archive.
2.  Parse it to build a blacklist of `OrderID`s that have been returned.
3.  Filter out any items from `Retail.OrderHistory` that match these returned `OrderID`s.

## Data Sources
- **Order History:** `Retail.OrderHistory.1.csv` (Key: `Order ID`)
- **Returns:** `Retail.OrdersReturned.1.csv` (Key: `OrderID`)

## Acceptance Criteria
- [ ] The system detects if `Retail.OrdersReturned` exists in the uploaded zip.
- [ ] If found, it parses the returned orders into a set of `returned_order_ids`.
- [ ] When processing `Retail.OrderHistory`, any row with an `Order ID` present in `returned_order_ids` is skipped.
- [ ] A log message indicates how many items were filtered due to returns.
