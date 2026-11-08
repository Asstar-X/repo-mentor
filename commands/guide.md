# /guide (Alias: /roadmap) — Hands-On Guide & Reading Path

> **Backing Skill**: [`skills/repo-recon/SKILL.md`](../skills/repo-recon/SKILL.md)

Generates an actionable, copy-pasteable local study roadmap for the target codebase: **local build & targeted smoke unit test commands**, **progressive reading order**, **golden breakpoints**, and a **first hands-on hack experiment**.

---

## Operational Workflow

### 1. Extract Ground Truth
From the repository root, run deterministic tools:
```bash
repo-mentor scan <target_path>
repo-mentor hotspots <target_path> --top 10
```
Identify test directories, build systems, entrypoints, and modification hotspots.

---

### 2. Generate Hands-On Study Guide

#### I. Minimal Runnable Verification (Smoke Run Commands)
Based on detected ecosystem and project manifests, provide exact commands that require zero guesswork:
- **Build / Compilation Command**:
  ```bash
  # Project-specific build command (e.g. go build -o bin/server ./cmd/server)
  ```
- **Targeted Smoke Unit Test Command**:
  - Select 1–2 representative tests from Tier-0 domains with filter flags, avoiding long-running full test suites.
  ```bash
  # Project-specific targeted test command (e.g. pytest tests/core/test_engine.py -k "test_dispatch" -vv)
  ```

#### II. Progressive Reading Order (With Verified Code Anchors)
Provide a 4-step sequence specifying exactly what to focus on and what boilerplate to skip:
1. **Stop 1: Ingress & Entrypoint** `[path/entry.ext#L30-L60]` — Trace how external inputs are unmarshalled into domain Context; skip flag descriptions.
2. **Stop 2: Core Dispatcher** `[path/scheduler.ext#L80-L120]` — Observe the main scheduling loop, worker pool, and task routing.
3. **Stop 3: Keystone State & Entity Definitions** `[path/state.ext#L15-L50]` — Inspect core data structures, memory ownership, and state enums.
4. **Stop 4: High-Churn Core Invariant** `[path/hotspot.ext#L100-L150]` — Study the business logic most frequently modified in recent commits.

#### III. Recommended Golden Breakpoints
Identify four high-value breakpoint locations across the execution lifecycle:
- **Breakpoint 1 (Ingress Pivot)**: Set at `[path/entry.ext#Lxx]` to inspect raw request unmarshalling and auth context.
- **Breakpoint 2 (Dispatch Pivot)**: Set at `[path/scheduler.ext#Lyy]` to step into queue routing, lease allocation, and timeout propagation.
- **Breakpoint 3 (Guard Pivot)**: Set at `[path/engine.ext#Lzz]` to inspect state machine invariants and mutex acquisitions.
- **Breakpoint 4 (Durability Pivot)**: Set at `[path/wal.ext#Lww]` to step into disk fsync or network commit acknowledgements.

#### IV. First Hands-On Experiment (First Hack)
Suggest a low-risk, easily verifiable hands-on task:
- e.g., "Add a unit test in `tests/` feeding an out-of-bounds parameter to confirm defensive rejection";
- or "Add a configuration flag in the config module and verify clean local compilation and startup."
