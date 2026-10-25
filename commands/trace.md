# /trace (Alias: /flow) — Call-Flow Tracing & Anchor Review

Traces the end-to-end execution flow for a specific core domain or business scenario (e.g. `/trace pkg/scheduler` or `/trace task_submission`), verifies line-number code anchors, and updates the domain call chain mastery score.

---

## Operational Steps

### 1. Map to Target Functional Domain
- Confirm which domain $D_i$ in the Core Functional Domain Matrix this trace belongs to.
- If the call chain for this domain is already covered, inform the user that its trace score is saturated (35%) and recommend modeling its state machine or exploring an untouched blind spot.

### 2. Locate Trigger Entrypoint
Use symbol search to identify the entry trigger in the Ingress layer (CLI command binding, HTTP route handler, or event listener).

### 3. Drafting Phase: Map Critical Execution Flow
Follow the execution path across key transitions:
`Ingress -> Dispatch -> Core Engine -> Persistence / Outbound Network`.

Adhere to `methodology/03-tracing-callchains.md`:
- Draw a Mermaid sequence diagram (`sequenceDiagram`, using `participant ID as "Display Name (path#Lxx)"` with quoted aliases and flush-left margins);
- Annotate verified line-number markdown links (e.g. `[pkg/engine.go#L45-L60]`);
- Trace how core data entities mutate along the path.

### 4. Review Phase: Anchor Verification & Mermaid Syntax
1. **Deterministic Line Number & File Verification**:
   ```bash
   python tools/verify_anchors.py <target_path> <trace_output.md>
   ```
   If any file path or line number is invalid, reject and fix immediately.
2. **Mermaid Diagram Syntax Verification**:
   ```bash
   python tools/verify_mermaid.py <trace_output.md> --fix
   ```
   Validate participants, labels, and formatting to prevent rendering fallbacks.
3. **Filter Boilerplate Noise**:
   Ensure CLI argument flags, logging lines, and generic error wrappers do not clutter the diagram.
4. **Inspect State Invariants**:
   Verify lock acquisitions/releases, transaction boundaries, and channel closures.

### 5. Archival & Matrix Update
1. Save the call chain slice to: `studies/<repo_name>/traces/<scenario>.md`.
2. Update the **Domain Coverage Matrix** in `studies/<repo_name>/README.md`:
   - Mark `Call Chain (/trace)` for domain $D_i$ as `35%`;
   - Recalculate domain score $S(D_i)$ and global mastery progress.
3. Update `study_tracker.csv` with latest progress and activity timestamp.

---

### Mastery Progress & Blind-Spot Analysis
- **Global Mastery Progress**: **[Calculated Value]%**
- **Core Domain Coverage**: **m / k**
- **Blind-Spot Warning**:
  - [List remaining unexplored Tier-0 domains]
  > Gating Notice: Progress is mathematically hard-capped until the above blind spots are explored.

### Recommended Next Steps
1. **`/core <Current Domain>`** — Model data structures, entities, and state invariants for this domain.
2. **`/drill <Current Domain>`** — Challenge limit scenarios (concurrency races, crash recovery).
3. **`/trace <Unexplored Domain>`** — Switch to the next core blind spot.
