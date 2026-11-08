# /trace (Alias: /flow) — Call-Flow Tracing & Anchor Review

Traces the end-to-end execution flow for a specific core domain or business scenario (e.g. `/trace pkg/scheduler` or `/trace task_submission`), verifies line-number code anchors, maps sync/async boundaries, and updates the domain call chain mastery score.

---

## Operational Steps

### 1. Map to Target Functional Domain
- Confirm which domain $D_i$ in the Core Functional Domain Matrix this trace belongs to.
- If the call chain for this domain is already covered, inform the user that its trace score is saturated (35%) and recommend modeling its state machine (`/core`) or exploring an untouched blind spot.

### 2. Locate Trigger Entrypoint
Use symbol and call hierarchy extraction to identify the entry trigger in the Ingress layer:
```bash
repo-mentor ast <target_path> --calls || grep -rn "func.*Handler" <target_path>
```

### 3. Drafting Phase: Map 5-Phase Golden Path Execution Flow
Follow the execution path across all 5 canonical phases:
$$\text{Phase 1: Ingress} \longrightarrow \text{Phase 2: Dispatch} \longrightarrow \text{Phase 3: Engine} \longrightarrow \text{Phase 4: Persistence/IO} \longrightarrow \text{Phase 5: Response}$$

Adhere strictly to `methodology/03-tracing-callchains.md`:
1. **Mermaid Sequence Diagram**:
   - Flush left with margin ````mermaid`.
   - Quoted participant aliases: `participant E as "Core Engine (src/engine.go#L40)"`.
   - Explicitly annotate boundary hops (sync function call vs async channel send vs thread pool handoff).
2. **Prohibit N5 (Happy Path Bias)**:
   - Must document at least one critical error/rejection branch (validation failure, timeout, retry).
   - Trace error bubbling hierarchy and rollback mechanics.
3. **Triple-Anchor Annotation**:
   - Annotate verified line-number markdown links `[pkg/engine.go#L45-L60]`, symbol name, and 3–8 line load-bearing snippets.

### 4. Review Phase: Anchor Verification & Anti-AI Linter
Run deterministic verification tools:
```bash
# 1. Verify all code line ranges and file existence
repo-mentor verify <target_path> <trace_output.md> || python tools/verify_anchors.py <target_path> <trace_output.md>

# 2. Validate Mermaid diagram syntax
python tools/verify_mermaid.py <trace_output.md> --fix

# 3. Scan for banned buzzwords and unanchored claims
repo-mentor eval <trace_output.md> --check-fluff
```
If any file path, line number, or Mermaid diagram is invalid, reject and fix immediately.

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
