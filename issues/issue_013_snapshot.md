# Snapshots Creation, Management & Portfolio Progress Analysis

## TL;DR
Add the ability to create portfolio snapshots from current holdings, manage existing snapshots, and analyze portfolio progress over time by comparing snapshots with both quantitative results and a short executive summary.

---

## Type
Feature

## Priority
Normal

## Effort
Medium

---

# Part 1: Create Snapshot from Current Portfolio

## Current Behavior

- Snapshots are static and imported from Excel
- There is no way to create a snapshot from the current portfolio state via the UI
- Portfolio state is dynamic (based on holdings), but not persisted historically

---

## Expected Behavior

Add a button in the **Portfolio page**:

**Create Snapshot**

When clicked:

1. A new snapshot is created with:
   - timestamp (current date)
   - optional label / name (e.g. "Q1 2026")

2. The system captures the current portfolio state:
   - all holdings
   - quantity per asset
   - average price
   - current price (if available)
   - total value per asset

3. Snapshot is saved in DB:
   - Snapshot entity
   - SnapshotHolding entries (one per asset)

4. The snapshot appears in the **Snapshots page**

---

## Data Model Expectations

Snapshot:
- id
- created_at
- label / name

SnapshotHolding:
- snapshot_id
- asset_id
- quantity
- avg_price
- current_price
- total_value

---

## Acceptance Criteria (Snapshot Creation)

- [ ] Clicking "Create Snapshot" creates a new snapshot
- [ ] Snapshot includes all current holdings
- [ ] Snapshot data matches current portfolio state at creation time
- [ ] Snapshot appears in Snapshots page
- [ ] Snapshot is immutable in terms of holdings data after creation

---

# Part 2: Snapshot Management

## Current Behavior

- Snapshots cannot be renamed from the UI
- Snapshots cannot be deleted from the UI

---

## Expected Behavior

Users should be able to manage snapshots directly from the **Snapshots page**.

### Rename Snapshot
- User can edit the snapshot name / label
- The updated name is saved in DB
- The new name is reflected immediately in the UI

### Delete Snapshot
- User can delete a snapshot
- Deletion removes the snapshot and its related snapshot holdings
- Show a confirmation step before deletion

---

## Acceptance Criteria (Snapshot Management)

- [ ] User can rename a snapshot
- [ ] Renamed snapshot persists after refresh
- [ ] User can delete a snapshot
- [ ] Deleting a snapshot also removes its related snapshot holdings
- [ ] User gets a confirmation prompt before deletion
- [ ] UI updates correctly after rename or delete

---

# Part 3: Analyze Progress Between Snapshots

## Current Behavior

- Snapshots exist but are not fully used for analysis
- Analysis action is limited and not available consistently for all snapshots
- No clear summary/executive explanation is shown alongside the numeric comparison

---

## Expected Behavior

Add an **Analyze Snapshot** / **Analyze Progress** action in the **Snapshots page** that is available for every snapshot view, not only for the latest one.

The analyze action should remain accessible even when the user navigates between snapshots.

At minimum, the user should be able to analyze:
- the selected snapshot against the previous snapshot
- and/or compare two snapshots if the implementation already supports selection

---

## Analysis Output

The analysis should include:

### Portfolio Level
- Total portfolio value change
- Absolute P&L
- Percentage return

### Asset Level
For each asset:
- Change in value
- Change in quantity
- Contribution to portfolio return

### Optional Grouping / Breakdown
If data exists or can be inferred:
- Change by sector / category / theme
- Top contributing holdings
- Largest negative contributors

---

## Executive Summary Requirement

In addition to numeric analysis, include a short **executive summary paragraph** that explains the key portfolio changes in plain language.

Examples of what the summary may mention:
- overall portfolio growth or decline
- main drivers of change
- leading gainers / losers
- sector or category shifts
- major allocation changes between snapshots

This summary does not need to be AI-generated. A deterministic template-based summary is sufficient for MVP.

---

## Suggested UX (Flexible)

- Keep analysis action visible on every snapshot page / card / detail view
- Display results in a simple table for MVP
- Add a short summary block above the analysis results
- Optional later enhancements:
  - chart comparison
  - explicit snapshot picker
  - sector allocation comparison

---

## Backend Expectations

- Add service logic to:
  - fetch snapshots
  - compare a selected snapshot against another snapshot
  - compute portfolio-level and asset-level deltas
  - generate a short summary from the calculated metrics

- Calculations should be deterministic and reproducible

---

## Acceptance Criteria (Analysis)

- [ ] User can trigger analysis from every snapshot view, not only the latest one
- [ ] Analysis compares the selected snapshot to the appropriate previous snapshot (or chosen comparison snapshot)
- [ ] Portfolio total change is correctly calculated
- [ ] Asset-level changes are correctly calculated
- [ ] Analysis results are displayed in UI
- [ ] A short executive summary is displayed above or alongside the analysis
- [ ] Summary references meaningful portfolio changes such as leading assets or major shifts
- [ ] Basic table-based presentation is sufficient for MVP

---

## Relevant Files

backend/app/services/portfolio_service.py  
backend/app/services/snapshot_service.py (if exists / create if needed)  
backend/app/repositories/snapshot_repo.py  
frontend portfolio page  
frontend snapshots page  

Potential additional files:
- snapshot routes / API handlers
- snapshot detail / analysis components
- utilities for summary generation

---

## Risks / Dependencies

- Snapshot must reflect **holdings at a specific point in time**
- Holdings are derived from transactions → ensure consistency
- Need to decide whether to store current_price in snapshot or recompute later
- Need clear delete behavior for related snapshot holdings
- Sector/category analysis depends on whether such metadata already exists on assets
- Summary should be simple and deterministic for MVP

---

## Notes

- Snapshots should act as **historical checkpoints**
- Snapshot holdings should remain immutable after creation
- Rename should only affect snapshot metadata, not holdings data
- Analysis should be available consistently across the Snapshots experience
- Keep initial implementation simple and extendable