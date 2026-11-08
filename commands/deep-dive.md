# /deep-dive (Aliases: /core, /drill) — Keystone Entities, State Machines & Limit Drills

> **Backing Skill**: [`skills/repo-deepdive/SKILL.md`](../skills/repo-deepdive/SKILL.md)

Executes cognitive **Level 4 (Deep Dive)** & **Level 5 (Takeaway)**: inspects keystone entity structures, models lifecycle state machines (FSM), extracts 3~8 load-bearing code lines with verified AST anchors, runs destructive What-If disaster drills, and audits architectural trade-offs.

---

## Operational Workflow

### 1. Inspect Keystone Entities & Symbols
```bash
# Locate keystone structs, classes, or state machines in target domain
repo-mentor ast <target_path> --symbol <KeystoneStruct>
```

### 2. Generate Deep-Dive Slice (`studies/<repo_name>/traces/<domain>_core.md`)

#### Part I: Keystone Entities & Lifecycle State Machine
- **Keystone Structures**: Physical line anchors `[path/to/struct.ext#Lstart-Lend]` with memory layouts and lock protection notes.
- **State Transition Model (`stateDiagram-v2`)**: Initial state to terminal state, including explicit **forbidden transition guards**.

#### Part II: Load-Bearing Algorithms & Code Anchors
- **3~8 Load-Bearing Lines**: Essential concurrency control, pointer swapping, or core mathematical calculations.
- **Triple-Anchor Compliance**: Every code snippet MUST link to `[path/to/file.ext#Lstart-Lend]`.

#### Part III: Destructive Limit Scenario & What-If Drill
- 💥 **What-If Disaster Hypothesis**: "If line X or lock Y is omitted, how does the system fail?"
- **Interleaved Concurrent Schedule**: Step-by-step timeline proof of race condition, crash, or data corruption.
- **Verified Source Defense**: Concrete defense deployed in the live codebase (single-flight, CAS, timeout, WAL replay).

#### Part IV: Level 5 Trade-offs & Borrowable Patterns
- **Trade-offs**: What was sacrificed to achieve this design?
- **Borrowable Patterns**: 1~2 design patterns the reader can directly adopt in their own projects.

---

## 3. Automated Verification & Archival
```bash
# Verify code anchors and lint Mermaid state diagrams with auto-fix
repo-mentor verify <target_path> studies/<repo_name>/traces/<domain>_core.md --fix

# Evaluate against anti-AI fluff linting
repo-mentor eval <target_path> studies/<repo_name>/traces/<domain>_core.md
```

---

## 4. Update Checklist
In `studies/<repo_name>/README.md`, mark the domain's state model and limit drill as completed:
```markdown
- [x] **Domain: [Domain Name]** (`[path/to/module/]`) — Explored (Trace, Core FSM & What-If Defense)
```
