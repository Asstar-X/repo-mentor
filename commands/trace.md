# /trace (Alias: /flow) — Concrete Data Journey & Golden Path Tracing

> **Backing Skill**: [`skills/repo-trace/SKILL.md`](../skills/repo-trace/SKILL.md)

Executes cognitive **Level 3 (Example)**: tracks a single, living concrete input payload as it traverses component boundaries, records station-by-station payload diffs, delineates sync/async transitions, and documents error recovery branches.

---

## Operational Workflow

### 1. Identify Target Domain & Extract Call Hierarchy
```bash
# Extract symbol signatures and call hierarchy for the domain
repo-mentor ast <target_path> --symbols --calls
```

### 2. Generate Trace Slice (`studies/<repo_name>/traces/<domain>_trace.md`)

#### Part I: Concrete Walkthrough — A Day in the Life (具象案例与输入样本)
- **Concrete Input Event**: Provide an exact, living payload (e.g. a specific JSON request, CLI invocation, or AST node).
- **Station-by-Station Data Journey & Payload Diff**:
  1. **Ingress (接入层)**: Protocol decode, validation, trace ID injection (Payload Diff: Raw Bytes ➔ Command Context).
  2. **Buffer / Spool (缓冲层)**: Channel or RingBuffer enqueue (Payload Diff: In-flight sequence assigned).
  3. **Processing (处理层)**: Business logic, FSM mutation, or compute kernel execution.
  4. **Persistence / Egress (出站层)**: Storage write, fsync, or response dispatch.

#### Part II: 5-Phase Golden Path Sequence Diagram (Mermaid)
- Draw `sequenceDiagram` with quotes around participant names.
- Distinguish synchronous (`->>`) vs asynchronous (`-->>`) hops (channels, thread pools, worker queues).
- Include `alt / else` blocks for error recovery, retries, and fallback handling.

---

## 3. Automated Verification
Verify that all referenced paths and diagrams are valid:
```bash
repo-mentor verify <target_path> studies/<repo_name>/traces/<domain>_trace.md --fix
```

---

## 4. Update Tracker
In `studies/<repo_name>/README.md`, update the core domain checklist to mark call path tracing complete.
