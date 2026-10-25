# /guide (Alias: /roadmap) — Hands-On Guide & Reading Path

Generates an actionable, copy-pasteable local study roadmap for the target codebase: **local build & smoke unit test commands**, **progressive reading order**, **golden breakpoints**, and a **first hands-on hack experiment**.

---

## Operational Steps

### 1. Extract Ground Truth
From the repository root, run:
```bash
python tools/repo_scanner.py <target_path>
python tools/git_hotspots.py <target_path>
```
Identify test directories, build systems, entrypoints, and modification hotspots.

---

### 2. Generate Hands-On Study Guide

#### I. Minimal Runnable Verification (Smoke Run Commands)
Based on detected ecosystem and project manifests, provide exact commands that require no guesswork:
- **Build / Compilation Command**:
  ```bash
  # Project-specific build command (e.g. go build -o bin/server ./cmd/server)
  ```
- **Core Unit Test Command**:
  - Select 1–2 representative tests from Tier-0 domains with filter flags, avoiding long-running full test suites.
  ```bash
  # Project-specific targeted test command (e.g. cargo test core::engine -- --nocapture)
  ```

#### II. Progressive Reading Order (With Verified Code Anchors)
Provide a 4–5 step sequence specifying exactly what to focus on and what boilerplate to skip:
1. **Stop 1: Ingress & Entrypoint** `[path/entry.go#L30-L60]` — Trace how external inputs are converted into internal Context;
2. **Stop 2: Core Dispatcher** `[path/scheduler.go#L80-L120]` — Observe the main loop and task dispatch logic;
3. **Stop 3: State & Entity Definitions** `[path/state.go#L15-L50]` — Inspect core data structures and state enums;
4. **Stop 4: High-Churn Core Logic** `[path/hotspot.go#L100-L150]` — Study the business logic most frequently modified in recent commits.

#### III. Recommended Golden Breakpoints
Identify the two most information-dense breakpoint locations:
- **Breakpoint 1 (Dispatch Pivot)**: Set at `[path/file.go#Lxx]` to step into task decomposition and dispatch stacks;
- **Breakpoint 2 (Defensive Guard)**: Set at `[path/file.go#Lyy]` to inspect rejection of invalid inputs or illegal state transitions.

#### IV. First Hands-On Experiment (First Hack)
Suggest a low-risk, easily verifiable hands-on task:
- e.g., "Add a unit test in `tests/` feeding an out-of-bounds parameter to confirm defensive rejection";
- or "Add a configuration flag in the config module and verify clean local compilation and startup."

---

### Mastery Progress & Blind-Spot Analysis
- **Global Mastery Progress**: Current score (Macro base 15%–25% + Domain coverage score)
- **Core Domain Coverage**: $m / k$
- **Blind-Spot Warning**: List Tier-0 domains not yet covered by `/trace`, `/core`, or `/drill`.
  > Gating Notice: The hands-on guide assists local onboarding but does not replace domain mastery. All blind spots must be conquered to complete the study.

### Recommended Next Steps
1. **`/trace <Unexplored Domain>`** — Follow Stop 1–2 to walk through the end-to-end call chain.
2. **`/core <Unexplored Domain>`** — Jump to Stop 3 to model data structures and state invariants.
