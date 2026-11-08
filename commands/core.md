# /core (Alias: /models) — Core Entities, State Machines & Invariants

Focuses on a designated core functional domain (e.g. `/core pkg/storage` or `/core scheduler_entities`), filtering boilerplate glue code to model critical domain ontologies, lifecycle state machines, forbidden transition guards, and system invariants.

---

## Operational Steps

### 1. Map to Target Functional Domain
- Confirm which domain $D_i$ in the Core Functional Domain Matrix this command corresponds to.
- If the domain's state model is already analyzed, notify the user that its score is saturated (35%) and recommend limit drills (`/drill`) or switching to an unexplored blind spot.

### 2. Filter Boilerplate Noise
Adhere strictly to `methodology/04-skipping-boilerplate.md` (prohibit N7 Boilerplate Domination):
- Omit CLI argument flags and environment variable loading;
- Omit repetitive error handling wrappers and tracing spans;
- Omit boilerplate struct copying and DTO field mappings.

### 3. Extract Symbols & Generate Core Modeling Report
Invoke AST analysis tools:
```bash
repo-mentor ast <target_path> --symbols || grep -rn "type.*struct" <target_path>
```

Adhere to `methodology/05-data-structures-and-states.md`:

#### I. Keystone Entity Definitions
Display 2–3 key struct/class definitions carrying primary domain rules (with verified line-number links):
- Explain the business modeling intent of each core field;
- Note memory representation (contiguous array, heap pointer, pooled buffer);
- Note concurrency protection: guarded by mutex, atomic CAS, or immutable Value Object.

#### II. State Machine Transitions & Forbidden Guards
If tasks or requests follow a lifecycle state machine, diagram with Mermaid `stateDiagram-v2`:
- Flush left margin ````mermaid`.
- Never use C++ `::` scope operators in transition labels (use `.` instead, e.g. `AllocStatus.NEVER`).
- **Forbidden Transitions**: Enumerate illegal transitions (e.g. `COMPLETED -> RUNNING`) and quote the physical code guard enforcing rejection:
  ```go
  // [pkg/engine/task.go#L112-L120]
  if !allowedTransitions[t.state][nextState] {
      return ErrIllegalStateTransition
  }
  ```

#### III. System Invariants
List 2–3 fundamental invariant rules that must never break at runtime:
- Point to the physical code anchor (lock acquisition order, atomic CAS loop, or transactional commit) enforcing each invariant.

#### IV. Architectural Trade-offs & Technical Debt Audit
Objectively analyze the engineering trade-offs chosen by the authors (e.g. resident memory vs. zero allocation, strict consistency vs. throughput), and flag technical debt without rationalizing flaws (prohibit N8).

---

### 4. Archival & Matrix Update
1. Save analysis into `studies/<repo_name>/DEBUG_NOTES.md`.
2. Update the **Domain Coverage Matrix** in `studies/<repo_name>/README.md`:
   - Mark `State Model (/core)` for domain $D_i$ as `35%`;
   - Recalculate domain score $S(D_i)$ and global mastery progress.
3. Synchronize `study_tracker.csv`.

---

### Mastery Progress & Blind-Spot Analysis
- **Global Mastery Progress**: **[Calculated Value]%**
- **Core Domain Coverage**: **m / k**
- **Blind-Spot Warning**:
  - [List remaining unexplored Tier-0 domains]
  > Gating Notice: Mastery progress remains capped until all core domains are walked through and modeled.

### Recommended Next Steps
1. **`/drill <Current Domain>`** — Stress-test edge cases, concurrency races, and invalid state transitions.
2. **`/trace <Unexplored Domain>`** — Switch to an untouched core domain.
3. **`/history`** — Investigate the evolution and refactoring history of these core data models.
