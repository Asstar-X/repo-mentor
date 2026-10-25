# 02. Module Boundaries & Dependency Direction

## Objective
Map top-level repository directories into a clear responsibility matrix. Distinguish core domain modules from peripheral adapters or boilerplate glue, and establish unambiguous dependency directions.

---

## Three-Tier Module Categorization

When analyzing directories, triage every package into one of three tiers:

1. **Ingress & Dispatch Layer (Entry & Glue)**
   - Typical directories: `cmd/`, `cli/`, `api/`, `routes/`, `commands/`
   - Purpose: Accept external requests, perform initial syntactic validation, construct request contexts, and dispatch to the core engine.
   - Profile: **High line count with minimal algorithmic depth**. Skim quickly rather than reading line-by-line.

2. **Core Domain Engine (Business Core)**
   - Typical directories: `core/`, `internal/engine/`, `domain/`, `pkg/core/`
   - Purpose: Coordinate state transitions, execute domain algorithms, and enforce critical invariants.
   - Profile: **The architectural heart of the project**. Dedicate the vast majority of deep reading time here.

3. **Peripheral Adapters & Utilities (Infrastructure & Tooling)**
   - Typical directories: `storage/`, `pkg/db/`, `tools/`, `utils/`, `helpers/`, `third_party/`
   - Purpose: Encapsulate infrastructure specifics (DB drivers, HTTP client wrappers, crypto utilities).
   - Profile: Implements abstract interfaces defined by the core engine. Treat as black boxes until an edge case requires investigation.

---

## Dependency Invariant Auditing

- **Unidirectional Dependency Rule**: Upper layers call lower layers; outer infrastructure depends on inner domain rules.
- **Circular Dependency Watch**: Mutual imports between packages indicate coupling debt; avoid ping-pong reading between cyclically coupled files.
- **Interfaces over Implementations**: When the core relies on I/O, it generally programs to an Interface / Trait. Read the interface definition first before inspecting vendor-specific drivers.
