# /export (Alias: /report) — Offline HTML Architecture Manual Export

Compiles accumulated study assets in `studies/<repo_name>/` (system positioning, architecture topologies, call chains, Q&A records, and limit scenario drills) into a standalone, single-file offline HTML technical whitepaper.

---

## Operational Steps

### 1. Run Compilation Tool
```bash
python tools/export_study_html.py studies/<repo_name>/
```
The tool automatically synthesizes and semantically structures:
- `studies/<repo_name>/README.md`
- `studies/<repo_name>/ARCHITECTURE.md`
- `studies/<repo_name>/DEBUG_NOTES.md`
- `studies/<repo_name>/traces/*.md`

---

## Output Structure & Design Highlights

- **Output File**: `studies/<repo_name>/dist/index.html`.
- **Three Progressive Engineering Sections**:
  - **I. System Positioning & Architecture**:
    - 1.1 Development Background & Problems Solved;
    - 1.2 Core Business Flow & Architecture Diagram (Mermaid proportional zoom);
    - 1.3 Core Directory Structure & Module Division;
    - 1.4 Module Reading Priority Order (Tier-0 Must Read / Tier-1 On-Demand / Tier-2 Skip);
    - 1.5 Study Mastery & Uncovered Domain Backlog.
  - **II. Core Code Walkthrough & Q&A Records**:
    - Direct Q&A cards (N records, lossless compilation), indexed in the left sidebar from Q01 to QN, presenting upfront technical conclusions, verified code anchors `[path#Lxx-Lyy]`, and objective confidence levels.
  - **III. Limit Scenarios & Architectural Defense**:
    - 3.1 Challenge Guide;
    - 3.2 Crash Recovery & Data Consistency;
    - 3.3 High Concurrency & Lock Contention;
    - 3.4 Extensibility & Blast Radius;
    - 3.5 Performance Bottlenecks & Design Trade-offs;
    - Testing deep structural comprehension with destructive failure scenarios, architectural focus, source-backed answers, and counterexamples.
- **Two-Column Layout**: Left sticky sidebar navigation synchronizes seamlessly with right content via Scrollspy.
- **Paper Monochrome Aesthetic**: Minimalist, compact, high-density black-and-white engineering layout with full print and PDF export support (`@media print`).
- **Mermaid Proportional Zoom Engine**: Uncompressed diagram viewer with `[ Zoom In + ]`, `[ Zoom Out - ]`, `[ 150% HD ]`, and `[ 100% Reset ]` controls, supporting smooth horizontal scrolling.

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
