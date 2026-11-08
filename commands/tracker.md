# /tracker (Alias: /stats) — Global Study Progress & Domain Coverage Dashboard

Aggregates all codebases studied through `repo-mentor`, displaying mathematical domain coverage progress, coverage matrices, and architectural pattern radar.

---

## Operational Steps

### 1. Ingest Tracking Data
Read local `study_tracker.csv` and active study indexes `studies/<repo_name>/README.md`:
```bash
repo-mentor scan --stats || cat study_tracker.csv
```
- Repository Name;
- Primary Ecosystem;
- Architecture Pattern;
- Global Mastery Progress (%);
- Study Status (`in_progress` / `completed`);
- Last Active timestamp and summary notes.

---

## 2. Output Global Dashboard & Coverage Matrix

### I. High-Level Summary
- **Total Codebases Tracked**: Number of registered projects;
- **Completed Studies**: Projects reaching 100% domain coverage and passing limit scenario verification;
- **Ecosystem Distribution**: Language breakdown across Go / Rust / Python / TS / Java / C++.

### II. Active Project: Domain Coverage Matrix
Display progress and mathematical caps across all $k$ Tier-0 domains:

| Core Functional Domain (Tier-0) | Core Module / Directory | Call Chain (`/trace`) | State Model (`/core`) | Limit Defense (`/drill`) | Domain Mastery | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **1. Task Dispatch Engine** | `pkg/scheduler/` | 35% | 35% | 30% | 100% | Mastered |
| **2. Network Protocol** | `pkg/protocol/` | 35% | 35% | 30% | 100% | Mastered |
| **3. Persistence & WAL** | `pkg/storage/` | 35% | 0% | 0% | 35% | In Progress |
| **4. Distributed Consensus** | `pkg/consensus/` | 0% | 0% | 0% | 0% | Unexplored (Blind Spot) |

- **Mathematical Progress Formula**:
  $$\text{Global Progress} = \text{Macro Base (25%)} + \sum_{i=1}^k \left( S(D_i) \times \frac{75\%}{k} \right)$$
- **Blind-Spot Hard-Cap Alert**: Total progress is mathematically capped below 100% while unexplored Tier-0 domains remain.

### III. Architecture Pattern Radar
Summary of architectural patterns conquered across studies:
| Architecture Pattern | Projects Studied | Key Competencies Mastered |
| :--- | :--- | :--- |
| **Microkernel & Plugins** | Project Name | Registry lifecycle, dynamic extension hooks, SPI contracts |
| **Pipes & Filters** | Project Name | Context propagation, backpressure buffers, stage transformations |
| **Event-Driven / Actor** | Project Name | Asynchronous channels, decoupled mailboxes, actor isolation |
| **Layered / Clean Architecture**| Project Name | Unidirectional dependencies, domain decoupling, interface inversion |
| **WAL + State Machine** | Project Name | Write-Ahead Log durability, fsync synchronization, deterministic replay |

### IV. Study History Table
Render formatted table from `study_tracker.csv`.

---

### Recommended Next Steps
1. **`/overview <path/url>`** — Onboard a new repository to analyze architecture topology and triage modules.
2. **`/trace <Unexplored Domain>`** — Trace call flows for unexplored blind spots in the active codebase.
3. **`/drill <Covered Domain>`** — Stress-test limit scenarios on analyzed domains.
