# 04. Identifying & Filtering Boilerplate Glue Code

## Objective
Establish an active filtering methodology to bypass the 80% of low-signal plumbing code present in modern repositories. Focus developer cognitive bandwidth squarely on the 20% load-bearing structures that define system correctness, throughput, and reliability.

---

## 1. The 80/20 Reality of Production Codebases

In professional open-source projects, line counts are overwhelmingly dominated by operational glue, defensive wrapping, and configuration bindings:
- A 20,000-line repository often contains fewer than 3,000 lines of genuine domain logic.
- The remaining 17,000 lines consist of command-line flag declarations, configuration unmarshalling, structured logging, distributed tracing span injections, and boilerplate type conversions.

When reading code, novice readers and generic LLMs make the mistake of reading sequentially from `main()`. They spend 80% of their time reading argument parsers and logging setups, arriving exhausted at the core engine. **Mastering a codebase requires knowing what NOT to read.**

---

## 2. The 5 Major Categories of Boilerplate Glue

| Boilerplate Category | Common Libraries & Manifestations | Code Signatures to Spot | Handling Protocol |
| :--- | :--- | :--- | :--- |
| **CLI & Flag Parsing** | `argparse`, `click`, `typer`, `cobra`, `clap`, `flag` | Dozens of `parser.add_argument()`, `.Flags().StringVar()` | Note supported subcommands and flags in 30 seconds; **skip all description strings and flag wiring**. |
| **Config & Env Binding** | `viper`, `pydantic-settings`, `godotenv`, `serde` | `os.Getenv()`, default assignment fallbacks, validation hooks | Look only at the final compiled `Config` struct; **skip reading file load and env precedence logic**. |
| **Logging & Telemetry** | `zap`, `logrus`, `structlog`, `opentelemetry`, `tracing` | `logger.Info()`, `span.SetAttribute()`, `tracer.Start()` | **Mentally filter out entirely**. Never allow logging statements to obscure algorithmic control flow. |
| **Trivial Error Wraps** | `fmt.Errorf("failed to...: %w", err)`, re-raise blocks | Repetitive 3-line error propagation checks without recovery | Skip standard bubbling; **inspect error blocks only if they trigger retry, rollback, or circuit-breaking**. |
| **DTO / Entity Mappers** | `userDTO.ToDomain()`, `ModelFromProto()`, manual assignments| Long lists of `dest.Field = src.Field` field-by-field copying | Verify source and target types; **skip inspecting the line-by-line assignment plumbing**. |

---

## 3. The 20% Load-Bearing Core: Where Gravity Resides

Always redirect cognitive attention to the high-signal constructs that dictate how the system behaves under stress:

### 1. Invariant Preconditions & Guards
Conditions that gate state mutation or reject invalid states:
```python
# HIGH SIGNAL: State guard enforcing idempotency and transition validity
if self._state not in (TaskState.PENDING, TaskState.RETRYING):
    raise IllegalStateTransitionError(f"Cannot run task from {self._state}")
```

### 2. Physical Concurrency Locks & Critical Sections
Where data races and memory corruption are prevented:
```go
// HIGH SIGNAL: Lock acquisition order and atomic CAS state update
m.mu.Lock()
defer m.mu.Unlock()
if !atomic.CompareAndSwapUint32(&m.activeWorkers, old, old+1) {
    return ErrWorkerPoolExhausted
}
```

### 3. Core Algorithmic Loops & Scheduling Logic
The mathematical or logical heart of the system:
- Dependency graph topological sorting (`pkg/dag/sort.go`);
- Cache eviction algorithms (LRU/LFU/TinyLFU ring buffers);
- Consensus state machine replication (`raft/raft.go`).

---

## 4. Negative Anti-Pattern to Eliminate

### ❌ N7: Boilerplate Domination (胶水代码反客为主)
- **Symptom**: Dedicating paragraphs or multiple pages of analysis to explaining how `main()` initializes CLI flags, how Viper reads `config.yaml`, or how logger levels are configured via environment variables.
- **Engineering Verdict**: This represents severe cognitive laziness. CLI and configuration loading follow industry-standard boilerplate patterns across all ecosystems; they reveal nothing about the core architectural design or algorithm design of the specific repository.
- **Gate Rule**:
  - In `ARCHITECTURE.md` and call chain traces, CLI and configuration initialization **must not exceed 3 lines** of high-level summary.
  - Any report that spends more than 10% of its content on Tier-2 boilerplate glue is rejected.

---

## 5. Active Filtering Heuristic (The 5-Second Test)

Before reading any block of code, ask:
1. *If this block was replaced by a dummy mock, would the domain algorithm or state machine behave differently?*
   - If **NO** (e.g. logging, flag parsing, metrics export) $\rightarrow$ **SKIP IMMEDIATELY**.
   - If **YES** (e.g. data validation, lock acquisition, state mutation, network I/O) $\rightarrow$ **INSPECT DEEPLY**.
2. *Does this line mutate durable state or acquire an operating system resource?*
   - If **NO** $\rightarrow$ Skim rapidly.
   - If **YES** $\rightarrow$ Trace the lifecycle ownership and failure recovery path.

---

## 6. Verification Checklist

Before accepting an architectural or code walkthrough:
- [ ] Is CLI flag parsing and configuration loading condensed into a concise reference?
- [ ] Are all logging calls and telemetry instrumentation filtered out of control flow diagrams?
- [ ] Are state guards, concurrency primitives, and domain invariants highlighted?
- [ ] Does the analysis avoid boilerplate domination (N7)?
