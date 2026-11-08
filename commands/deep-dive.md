# /deep-dive (Aliases: /trace, /core, /drill) — Unified Domain Deep-Dive

Analyzes a specific core functional domain end-to-end, traversing from a concrete data scenario (Level 3) down to micro-level algorithms, state machine invariants, code anchors, and limit defenses (Level 4), concluding with architectural trade-offs (Level 5).

---

## Operational Steps

### 1. Identify Target Domain & Context
1. Identify the target domain $D_i$ (e.g., `/deep-dive storage` or `/deep-dive hook-spool`).
2. Verify target domain files using AST extraction:
   ```bash
   repo-mentor ast <target_path> --symbol <domain_symbol>
   ```

---

## 2. Generate 3-Part Deep-Dive Slice (`studies/<repo_name>/traces/<domain>.md`)

### Part I: Level 3 — Concrete Walkthrough: A Day in the Life (具象案例与数据变形)
> 💡 **Cognitive Rule**: 读者在看代码前，必须看到一份**真实具体的数据**在各组件间流转变形的全过程。
1. **Specific Input Event**:
   - Provide an exact, concrete input payload (e.g. a specific CLI command, JSON payload, or test failure).
2. **Step-by-Step Data Journey**:
   - Trace how the payload transforms across stations (Ingress ➔ Spool/Buffer ➔ Processing ➔ Persistence).
   - Document the **Payload Diff** at each station (what gets sanitized, what gets extracted, what hash or timestamp is attached).

### Part II: Level 4 — Keystone Algorithms, State Invariants & Code Anchors (硬核代码与微观实现)
> 💡 **Cognitive Rule**: 带着好奇心深入微观实现，所有结论必须强绑定真实源码。
1. **Keystone Structures & State Transitions**:
   - Define core entities with physical line anchors `[path/to/file.ext#Lstart-Lend]`.
   - Graph state transition diagram (`stateDiagram-v2`).
2. **5-Phase Golden Path Sequence Diagram**:
   - Mermaid `sequenceDiagram` with quoted participant aliases.
   - Delineate sync vs async hops and error recovery branches.
3. **Core Algorithm & Invariant Enforcement**:
   - Detailed walkthrough of how the system solves its core dilemma.
   - Code snippet (3–8 load-bearing lines) with verified line numbers.
4. **Limit Scenario & What-If Drill**:
   - 💥 **What-If Hypothesis**: What disaster occurs if a critical line or lock is removed?
   - Verified code defense (fsync, single-flight, timeout, or circuit breaker).

### Part III: Level 5 — Takeaways & Trade-offs (权衡与可迁移模式)
- **Trade-offs**: What was sacrificed to achieve this design?
- **Borrowable Patterns**: What design pattern can an engineer steal for their own work?

---

## 3. Automated Verification & Archival
Run deterministic checks on the generated slice:
```bash
# 1. Verify code anchors and Mermaid syntax with auto-fix
repo-mentor verify <target_path> studies/<repo_name>/traces/<domain>.md --fix

# 2. Audit against fluff and unanchored assertions
repo-mentor eval <target_path> studies/<repo_name>/traces/<domain>.md
```

### 4. Update Checklist
In `studies/<repo_name>/README.md`, mark the domain as explored in the Domain Checklist:
```markdown
- [x] **Domain: [Domain Name]** (`[path/to/module/]`) — Explored (Trace, Core & Drill)
```
