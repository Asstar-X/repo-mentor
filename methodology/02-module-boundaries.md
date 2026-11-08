# 02. Module Boundaries & Dependency Direction

## Objective
Establish rigorous boundaries between software layers, enforcing a 3-tier module priority matrix (Tier-0, Tier-1, Tier-2). Eliminate the cognitive drag of flat enumeration, detect dependency inversions and circular coupling, and prioritize deep reading time on load-bearing domain logic.

---

## 1. The 3-Tier Module Priority Triage

A production repository contains thousands of lines of code, but cognitive bandwidth is finite. Treating every directory equally guarantees exhaustion before reaching the architectural core. Every package and module must be triaged into one of three distinct tiers:

```
┌────────────────────────────────────────────────────────────────────────┐
│  Tier-0: Core Domain Engine (60%–70% of Deep Reading Time)             │
│  - State machines, invariant guards, scheduling loops, consensus       │
│  - Highest algorithmic density, lowest churn tolerance                 │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │ Inward Dependency
┌───────────────────────────────────┴────────────────────────────────────┐
│  Tier-1: Dispatch & Protocol Adapters (20%–25% of Deep Reading Time)   │
│  - Route dispatchers, serialization codecs, RPC/REST controllers       │
│  - Moderate complexity; orchestrates request lifecycles                │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │ Inward Dependency
┌───────────────────────────────────┴────────────────────────────────────┐
│  Tier-2: Peripheral Glue & Boilerplate (5%–10% of Deep Reading Time)   │
│  - CLI flags, config parsing, logger wiring, DTO mappers, bash scripts │
│  - High line count, zero domain signal; skim or skip completely        │
└────────────────────────────────────────────────────────────────────────┘
```

### Detailed Triage Criteria

| Tier | Layer Classification | Typical Directories | Architectural Role | Reading Strategy |
| :---: | :--- | :--- | :--- | :--- |
| **Tier-0** | **Core Domain Engine** | `core/`, `engine/`, `domain/`, `consensus/`, `fsm/` | Enforces fundamental invariants, executes domain algorithms, manages state transitions. | **Full-depth inspection**. Examine every branch, lock boundary, and error rollback. |
| **Tier-1** | **Dispatch & Adapters** | `api/`, `controllers/`, `handlers/`, `storage/`, `transport/` | Converts wire protocols to domain structs; coordinates persistence interfaces. | **Interface inspection**. Review method signatures and boundary handoffs; treat internals as black boxes until tracing. |
| **Tier-2** | **Peripheral Glue** | `cmd/`, `cli/`, `config/`, `utils/`, `helpers/`, `scripts/` | Parses flags, reads environment variables, formats logs, wraps third-party SDKs. | **Aggressive filtering**. Skim signatures; never spend reading time on flag declarations or config defaults. |

---

## 2. Dependency Flow Directions & Invariant Rules

### 1. The Inward Dependency Rule
- Dependencies must strictly point **inward** toward higher-level policies.
- **Valid**: `Ingress (Tier-1)` imports `Core Engine (Tier-0)`. `Storage Adapter (Tier-1)` implements `Repository Interface (Tier-0)`.
- **Violation (Leaky Abstraction)**: `Core Engine (Tier-0)` importing HTTP context, SQL driver types, or CLI flag sets directly. When domain logic is coupled to external transports, portability and testability collapse.

### 2. Interface Inversion at Boundaries
- Load-bearing systems decouple state calculation from I/O through interfaces or traits:
  - In Go: `type StorageEngine interface { WriteBatch(...) error }` defined inside `core/`.
  - In Rust: `pub trait ConsensusTransport { fn send(&self, msg: Message); }` in domain crate.
  - In Python: Abstract Base Classes (`abc.ABC`) or `typing.Protocol` isolating engine from database drivers.
- Always read the **abstract interface definition** first before delving into vendor-specific adapters (`pg_storage.go`, `s3_adapter.py`).

### 3. Circular Dependency Hazards
- Mutual package imports (Package A imports Package B, and Package B imports Package A) signify architectural erosion.
- In languages that allow circular imports (e.g. Python via deferred imports inside functions), circular references create hidden initialization deadlocks, memory leaks, and tightly coupled God Packages.
- Pinpoint and document circular dependencies as architectural technical debt.

---

## 3. Negative Anti-Pattern to Eliminate

### ❌ N3: Flat Enumeration without Priority (扁平无优先级)
- **Symptom**: Presenting a uniform list of all modules in alphabetical or directory tree order, assigning equal weight to an 80-line `argparse` wrapper and a 6,000-line distributed Raft engine.
- **Engineering Verdict**: Fails to guide the developer to the heart of the system. Reading 10 trivial utility files before discovering the core dispatcher wastes hours of cognitive energy.
- **Gate Rule**: Any architecture report or module breakdown lacking an explicit **Tier-0 / Tier-1 / Tier-2 priority matrix** with stated reading depth rationale is rejected immediately.

---

## 4. Module Boundary Triage Matrix Standard

When generating repository documentation in `ARCHITECTURE.md`, format the module responsibilities matrix strictly as follows:

| Module / Directory Path | Priority Tier | Domain Role & Responsibility | Core Logic? | Dependency Direction & Constraints |
| :--- | :---: | :--- | :---: | :--- |
| `pkg/engine/` | **Tier-0** | Task scheduling, DAG topological sorting, worker lease allocation | **Yes** | Inward only; zero dependency on transport or storage drivers. |
| `pkg/storage/wal/` | **Tier-0** | Disk append-only logging, fsync synchronization, segment rotation | **Yes** | Called by `pkg/engine/`; implements `core.DurabilityEngine`. |
| `pkg/api/rest/` | **Tier-1** | HTTP route dispatch, JSON deserialization, auth token validation | No | Depends on `pkg/engine/`; translates HTTP DTO to domain commands. |
| `pkg/storage/sqlite/` | **Tier-1** | SQLite driver adapter for offline state snapshots | No | Depends on `pkg/storage/`; implements persistence interfaces. |
| `cmd/server/` | **Tier-2** | Flag parsing, config loading, signal trapping, graceful shutdown glue | No | Ingress runner; instantiates dependencies and launches engine. |
| `pkg/utils/` | **Tier-2** | String formatting, slice helpers, timestamp formatters | No | Leaf utility; must never import any other internal package. |

---

## 5. Verification Checklist

Before finalizing module boundary analysis, verify:
- [ ] Has every top-level package been categorized into Tier-0, Tier-1, or Tier-2?
- [ ] Does the Tier-0 classification capture all state machines, scheduling loops, and critical invariants?
- [ ] Are Tier-2 glue packages explicitly marked for filtering?
- [ ] Have all boundary interfaces and dependency inversions been validated against import declarations?
- [ ] Is flat enumeration (N3) completely avoided?
