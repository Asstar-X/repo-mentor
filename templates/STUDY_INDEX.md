# [Project Name] — Architecture Study Index & Coverage Checklist

> **Study Status**: `[in_progress / completed]`  
> **Target Ecosystem**: `[Go / Rust / Python / TypeScript / Java / C++]`  
> **Cognitive Framework**: 5-Level Cognitive Zooming (Why ➔ Strategy ➔ Example ➔ Deep-Dive ➔ Takeaway)  
> **Quality Standard**: Zero-Fluff Engineering Standard & AST Fact Grounded

---

## 1. Study Asset Catalog

- **[Architecture Specification (ARCHITECTURE.md)](ARCHITECTURE.md)**: Level 1 (Why & Tension) + Level 2 (Metaphor & Characters) + Level 4 (Keystone FSM & Algorithms) + Level 5 (Trade-offs).
- **[Source Walkthrough & Debug Journal (DEBUG_NOTES.md)](DEBUG_NOTES.md)**: Local build & targeted smoke test commands, golden breakpoint stack, and What-If challenge logs.
- **Domain Deep-Dive Slices (`traces/`)**:
  - [Domain 1 Deep-Dive (traces/domain_1.md)](traces/domain_1.md): Level 3 Concrete Walkthrough + Level 4 Implementation.
  - [Domain 2 Deep-Dive (traces/domain_2.md)](traces/domain_2.md)

---

## 2. Core Functional Domain Checklist (Explored vs. Blind Spots)

A project cannot be certified as understood if critical core domains remain unexamined. 

| Core Functional Domain | Primary Directory / Module | Exploration Status | Core Finding / Key Invariant |
| :--- | :--- | :---: | :--- |
| **1. [Domain Name 1]** | `[src/domain_1/]` | `[Explored / Blind Spot]` | [One-sentence invariant, e.g. Single-flight drain queue] |
| **2. [Domain Name 2]** | `[src/domain_2/]` | `[Explored / Blind Spot]` | [One-sentence invariant] |
| **3. [Domain Name 3]** | `[src/domain_3/]` | `[Explored / Blind Spot]` | [One-sentence invariant] |
| **4. [Domain Name 4]** | `[src/domain_4/]` | `[Explored / Blind Spot]` | [One-sentence invariant] |

> ⚠️ **Blind-Spot Warning**:  
> If any core domain is marked as `Blind Spot`, the codebase has not been mastered. Run `/deep-dive <domain>` to eliminate the blind spot.

---

## 3. Key Technical Indicators & Architectural Radar

| Dimension | Assessment & Metric | Grounded Evidence / Anchor |
| :--- | :--- | :--- |
| **Codebase Scale** | [e.g. 24,500 LOC (Go 82%, C 18%)] | Static scan report via `repo-mentor scan` |
| **Test Coverage & Harness** | [e.g. Comprehensive unit & fuzz tests] | Test fixtures located in `tests/` or `*_test.go` |
| **Top 1 Git Hotspot** | `[src/core/dispatcher.ext#L1]` | Most frequently modified file over last 300 commits |
| **Concurrency Model** | [e.g. Worker pool + sync.RWMutex] | Threading & lock patterns in core modules |
| **Durability Guarantee** | [e.g. Sequential WAL with synchronous fsync] | Invariant verified in `src/storage/wal.ext` |
| **External Dependencies** | [e.g. Embedded SQLite, Zero network RPC] | Package manifest inspection (`go.mod` / `pyproject.toml`) |

---

## 4. Quality Gate Verification

Before publishing this study:
- [ ] **Gate 1 (Anchor Verification)**: 100% of line-number anchors exist on physical disk (`repo-mentor verify`).
- [ ] **Gate 2 (Mermaid Syntax)**: All diagrams render cleanly with quoted participant aliases.
- [ ] **Gate 3 (Anti-AI Fluff Linter)**: Zero banned buzzwords or ungrounded fluff paragraphs detected (`repo-mentor eval`).
- [ ] **Gate 4 (Zero Blind Spots)**: All core functional domains in Section 2 are marked as `Explored`.
