# /export (Alias: /report) — Offline HTML Architecture Manual Export

Compiles accumulated study assets in `studies/<repo_name>/` (system positioning, architecture topologies, call chains, Q&A records, and limit scenario drills) into a standalone, single-file offline HTML technical whitepaper.

---

## Operational Steps

### 1. Pre-Export Quality Gate Audit
Before exporting, confirm that all study assets satisfy the High-Star quality gates:
```bash
repo-mentor verify <target_path> studies/<repo_name>/ARCHITECTURE.md
repo-mentor eval studies/<repo_name>/ --check-fluff
```
Ensure zero broken code anchors and zero banned buzzwords.

---

### 2. Run Compilation Tool
```bash
repo-mentor export studies/<repo_name>/
```
The export engine automatically synthesizes and semantically structures:
- `studies/<repo_name>/README.md`
- `studies/<repo_name>/ARCHITECTURE.md`
- `studies/<repo_name>/DEBUG_NOTES.md`
- `studies/<repo_name>/traces/*.md`

---

## Output Structure & Design Highlights

- **Output File**: `studies/<repo_name>/dist/index.html`.
- **Three Progressive Engineering Sections**:
  - **I. System Positioning & Macro Architecture**:
    - 1.1 Core Engineering Problem & Value Proposition;
    - 1.2 Macro Architecture Topology (Mermaid with protocol/process boundaries);
    - 1.3 3-Tier Module Priority Triage Matrix (Tier-0 / Tier-1 / Tier-2);
    - 1.4 Golden Path Sequence Diagram with verified code anchors;
    - 1.5 Study Mastery & Blind-Spot Coverage Matrix.
  - **II. Core Code Walkthrough & State Machine Invariants**:
    - Keystone entity mental models, lifecycle state machines, forbidden transition guards, and system invariant code anchors;
    - Direct Q&A walkthrough cards with verified line bounds `[path#Lstart-Lend]` and 3-tier confidence labeling (`[Verified Fact]`, `[Engineering Inference]`, `[Unverified Hypothesis]`).
  - **III. Limit Scenarios, Trade-offs & Technical Debt**:
    - 3.1 Architectural Design Trade-offs (what was sacrificed and why);
    - 3.2 Objective Technical Debt Audit (God Objects, lock contention, missing backpressure);
    - 3.3 Crash Recovery & Persistence Boundaries;
    - 3.4 Concurrency Contention & TOCTOU Race Counterexamples;
    - 3.5 Extensibility & Blast Radius.
- **Two-Column Responsive Layout**: Left sticky sidebar navigation synchronizes seamlessly with right content via Scrollspy.
- **Paper Monochrome Aesthetic**: Minimalist, compact, high-density black-and-white engineering layout with print and PDF export support (`@media print`).
- **Mermaid Proportional Zoom Engine**: Interactive diagram viewer with `[ Zoom In + ]`, `[ Zoom Out - ]`, `[ 150% HD ]`, and `[ 100% Reset ]` controls, supporting smooth horizontal scrolling.

---

## Progress Tracking & Study States
- **Real-Time Progress Synchronization**: Automatically syncs mastery progress from `study_tracker.csv`, supporting both in-progress review (e.g. 15%–90%) and final completion export (100%).
- **Current Global Mastery**: Displays current score (e.g. `35.5%` or `100%`) with mathematical score breakdown.
- **Status Badges**:
  - **In Progress (`in_progress`)**: Highlights current domain coverage, hard caps, and blind spots.
  - **Completed (`completed` / 100%)**: Confirms 100% domain coverage and full limit scenario defense.

### Recommended Next Steps
- **If Study is In Progress (< 100%)**: Run `/trace <Unexplored Domain>` to conquer call-flow blind spots, or `/drill <Core Domain>` to test invariants.
- **If Study is Completed (100%)**: Run `/tracker` to inspect global radar, or `/overview <New Repo>` to begin studying another repository.
