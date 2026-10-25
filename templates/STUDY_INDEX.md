# [Project Name] — Architecture Study Index

> **Study Status**: `[in_progress / completed]`  
> **Primary Language**: `[Go / Rust / Python / TS / Java / ...]`  
> **Architecture Pattern**: `[Microkernel / Pipes & Filters / Event-Driven / Layered / Workflow]`  
> **Global Mastery Progress**: `[0% ~ 100%]` (Macro Base 25% + Core Domain Coverage 75%)

---

## 1. Study Asset Catalog

- **[Architecture Specification](ARCHITECTURE.md)**: System positioning, architectural topology, module priority triage (Tier-0/1/2), and golden sequence flows.
- **[Source Walkthrough & Debug Journal](DEBUG_NOTES.md)**: Local build/smoke test commands, golden breakpoints, state machine invariants, and limit scenario drills.
- **Domain Call Chain Traces (`traces/`)**:
  - [Golden Path Call Chain Walkthrough](traces/scenario_1.md)

---

## 2. Core Functional Domains (Domain Coverage Matrix)

| Core Functional Domain (Tier-0) | Core Module / Directory | Call Chain (`/trace` 35%) | State Model (`/core` 35%) | Limit Defense (`/drill` 30%) | Domain Mastery | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **1. [Domain Name]** | `[path/to/module/]` | 0% | 0% | 0% | 0% | Unexplored (Blind Spot) |
| **2. [Domain Name]** | `[path/to/module/]` | 0% | 0% | 0% | 0% | Unexplored (Blind Spot) |
| **3. [Domain Name]** | `[path/to/module/]` | 0% | 0% | 0% | 0% | Unexplored (Blind Spot) |

> **Coverage Gating Rules**:
> - Global Progress = Macro Pattern Triage (15%) + Git Churn Evolution (10%) + $\sum_{i=1}^k (S(D_i) \times \frac{75\%}{k})$;
> - If any Tier-0 domain remains uninspected, its score is 0%, mathematically hard-capping total mastery below 100%.

---

## 3. Key Technical Indicators

| Dimension | Assessment | Notes |
| :--- | :--- | :--- |
| **Codebase Scale** | [xxx LOC] | Core language lines of code |
| **Test Coverage** | [None / Basic / Comprehensive] | Unit test directories and integration fixtures |
| **Top 1 Hotspot File** | `[path/to/file#Lxx]` | Most frequently modified core file via Git Churn |
| **External Dependencies**| [Dependency list] | Storage engines, message brokers, or key third-party libraries |
