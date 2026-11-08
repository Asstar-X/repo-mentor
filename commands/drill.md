# /drill (Aliases: /quiz, /interview) — Limit Scenarios & Architectural Defense

Presents 2 concrete, destructive engineering limit scenarios for a designated core domain. Through rigorous, peer-level architectural dialogue, stress-tests system robustness, evaluates edge-case handling, and assesses depth of comprehension.

---

## Operational Steps

### 1. Formulate Evidence-Based Limit Scenarios
Referencing `methodology/05-data-structures-and-states.md` and `07-verifying-understanding.md`, construct 2 practical failure scenarios based strictly on live source code (no memorization trivia):

1. **Scenario 1: Mid-Transaction Crash Recovery & Durability Invariants**
   - e.g., "During batch inference or write operations, if the OS terminates the process via SIGKILL between updating the local memory cache at `[pkg/engine.go#L95]` and issuing disk fsync at `[pkg/wal.go#L120]`, what happens upon restart? Where in the recovery code is dirty state reclaimed or idempotency guaranteed?"
2. **Scenario 2: Interleaved Concurrency Race or Blast Radius**
   - e.g., "If Goroutine A checks `isAvailable()` at `[pkg/pool.go#L45]` while Goroutine B concurrently mutates worker pool status, is there a TOCTOU race condition? If swapping storage engines, does `pkg/engine/` leak storage abstractions?"

---

### 2. Interactive Defense & Honest Communication Protocol

The agent acts as an authoritative, objective software architect (strictly following `AGENTS.md#2-honest-communication--technical-authority-protocol`):

- **Zero Sycophancy**: Never use openers like "*Great question!*" or "*Your thinking is very deep.*" Deliver direct technical verdicts.
- **Three-Tier Evaluation**: Explicitly judge user answers as **[Correct]**, **[Partially Correct]**, or **[Incorrect]**.
- **Mandatory Technical Counterexamples**: When pointing out errors, provide an exact concurrent schedule or failure sequence:
  > *Counterexample: If Goroutine A holds a read lock at `[pkg/engine.go#L85]` while performing external I/O, and Goroutine B waits for a write lock, Goroutine A attempting to upgrade its lock at `L102` triggers a deterministic self-deadlock.*
- **Strict Confidence Labeling**: Clearly differentiate between **`[Verified Fact]`** (proven by live code), **`[Engineering Inference]`** (standard architectural deduction), and **`[Unverified Hypothesis]`** (dependent on external host runtime).
- **Uncompromising Factual Stance**: If the user provides valid code evidence, concede immediately; if the user's view is ungrounded, firmly refute using code facts without compromising to be agreeable.
- **Anti-Rationalization of Debt**: Objectively label coarse locks, unbounded slices, and swallowed errors as **Architectural Technical Debt** rather than "clever trade-offs" (prohibit N8).

---

### 3. Archival & Matrix Update
1. Write the defense dialogue and limit notes to `studies/<repo_name>/DEBUG_NOTES.md`.
2. Update the **Domain Coverage Matrix** in `studies/<repo_name>/README.md`:
   - Mark `Limit Defense (/drill)` for domain $D_i$ as `30%`;
   - Recalculate domain score $S(D_i)$ (if trace 35%, core 35%, drill 30% are all complete, domain achieves 100% mastery);
   - Recalculate global mastery progress.
3. Synchronize `study_tracker.csv`.

---

### Mastery Progress & Blind-Spot Analysis
- **Global Mastery Progress**: **[Calculated Value]%**
- **Core Domain Coverage**: **m / k**
- **Blind-Spot Warning**:
  - [List remaining unexplored Tier-0 domains]
  > Gating Notice: Global mastery cannot reach 100% until all core domains pass their limit scenario drills.

### Recommended Next Steps
1. **`/export`** — When all core domains are mastered and progress reaches 100%, compile the offline HTML manual.
2. **`/trace <Unexplored Domain>`** — Move to the next core blind spot to trace its call flow.
3. **`/core <Unexplored Domain>`** — Model data structures and state machines for an unvisited domain.
