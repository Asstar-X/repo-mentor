# 03. Systematic Call-Chain Tracing (Following the Golden Path)

## Objective
Establish an execution-first methodology for tracing critical end-to-end paths through an unfamiliar codebase. Follow the Golden Path across synchronous, asynchronous, and network boundaries, anchor physical caller-callee line references, and eliminate superficial happy-path bias.

---

## 1. The 5-Phase Golden Path Architecture

Reading code statically without following runtime execution produces fragmented, illusory mental models. To understand how data structures mutate and where system policies are enforced, trace a single high-value end-to-end scenario across the five canonical phases:

$$\text{Phase 1: Ingress} \longrightarrow \text{Phase 2: Dispatch} \longrightarrow \text{Phase 3: Engine} \longrightarrow \text{Phase 4: Persistence/IO} \longrightarrow \text{Phase 5: Response}$$

```
[External Trigger]
       │
       ▼
┌──────────────┐   Decode / Validate DTO
│ 1. Ingress   │ ────────────────────────────────────────┐
└──────────────┘                                         ▼
                                                  ┌──────────────┐
                                                  │ 2. Dispatch  │ Route & Build Request Context
                                                  └──────────────┘
                                                         │
                                                         ▼
                                                  ┌──────────────┐
                                                  │  3. Engine   │ Invariant Guards & State Transition
                                                  └──────────────┘
                                                         │
                                                         ▼
┌──────────────┐   Format Output & Ack            ┌──────────────┐
│ 5. Response  │ ◄─────────────────────────────── │ 4. Persist/IO│ Sync Fsync / Network Send
└──────────────┘                                  └──────────────┘
```

### Detailed Phase Responsibilities

1. **Phase 1: Ingress (Transport & Protocol Parsing)**
   - Entrypoints: CLI command handler, HTTP route handler, gRPC service method, or message queue consumer.
   - Operations: Raw byte stream decoding, header parsing, syntactic schema validation.
2. **Phase 2: Dispatch (Routing & Context Construction)**
   - Operations: Authentication/authorization verification, timeout deadline injection (`context.WithTimeout`), rate limiting, dispatch to worker pool or actor queue.
3. **Phase 3: Engine (Core Domain Computation)**
   - Operations: Invariant assertions, state machine transition checks, algorithmic scheduling, memory updates. **This is where business value resides.**
4. **Phase 4: Persistence / Outbound I/O (Durability & Side Effects)**
   - Operations: WAL disk append with `fsync`, database transactional commit, remote RPC emission, cache invalidation.
5. **Phase 5: Response / Receipt (Receipt Generation & Emission)**
   - Operations: Result status serialization, telemetry counter increment, error envelope wrapping, client ack.

---

## 2. Crossing Boundary Hops: Sync vs. Async Execution

Complex systems rarely execute linearly on a single thread. When tracing call chains, explicitly identify and label boundary crossings:

| Boundary Type | Manifestation in Code | Trace Strategy & Critical Gotchas |
| :--- | :--- | :--- |
| **Sync Function Call** | `res = engine.Process(ctx, req)` | Follow direct stack frame. Note caller lock acquisitions before entry. |
| **Async Task Spawn** | `go worker.Run()`, `asyncio.create_task()`, `tokio::spawn` | The current thread/goroutine relinquishes execution. Trace where the future/channel is awaited. |
| **Channel / Queue Hop** | `ch <- task`, `queue.push(item)` | Identify buffer size. Is it bounded (backpressure) or unbounded (OOM hazard)? Identify consumer loop. |
| **Thread Pool Handoff**| `pool.submit(callable)`, `asyncio.to_thread` | Trace context propagation (tracing spans, user credentials, cancellation tokens). |
| **Network / RPC Hop** | `client.Do(req)`, `grpc.Invoke()` | Note timeout deadline, circuit breaker wrapping, and idempotent retry policies. |

---

## 3. Negative Anti-Pattern to Eliminate

### ❌ N5: Happy Path Bias (快乐路径偏见)
- **Symptom**: Describing an execution trace as if every network call succeeds instantly, every lock is acquired without contention, inputs are always valid, and crashes never occur.
- **Engineering Verdict**: In production software, over 70% of the engineering complexity resides in error handling, backpressure, retries, timeout cancellations, and partial failure rollbacks. A trace that ignores failure paths fails to convey how the system survives in production.
- **Gate Rule**: Every call chain trace **MUST** document:
  - At least one critical failure/rejection branch (e.g., validation failure, lock timeout, network retry);
  - How errors bubble up through the stack (error wrapper, panic recovery, or silent drop);
  - State cleanup or rollback mechanisms triggered upon failure.

---

## 4. Mermaid Sequence Diagram Standard

All call-chain diagrams in `traces/<scenario>.md` and `ARCHITECTURE.md` must follow these syntax and annotation rules:
1. **Flush Margins**: Code block starts flush left with ````mermaid` without list indentation.
2. **Quoted Participant Aliases**: Always declare participants with quoted names and file anchors:
   ```mermaid
   sequenceDiagram
       autonumber
       participant C as "Client / Caller"
       participant I as "Ingress (cmd/server.go#L45)"
       participant E as "Engine (pkg/engine.go#L110)"
       participant S as "Storage (pkg/wal.go#L60)"

       C->>I: SubmitTask(payload)
       activate I
       I->>I: ValidateSchema() [L52]
       alt Invalid Payload
           I-->>C: 400 Bad Request
       end
       I->>E: Dispatch(ctx, task) [L70]
       activate E
       Note over E: Check state invariant & acquire lock [L118]
       E->>S: AppendWAL(entry) [L142]
       activate S
       S-->>E: Fsync ACK [L85]
       deactivate S
       E-->>I: ExecutionResult [L165]
       deactivate E
       I-->>C: 200 OK (Receipt)
       deactivate I
   ```
3. **Anchor Every Major Arrow**: Every inter-module transition must specify the exact source file and line range where the invocation occurs.

---

## 5. Verification Checklist

Before publishing a call-chain trace:
- [ ] Does the trace cover all 5 phases (Ingress -> Dispatch -> Engine -> Persistence -> Response)?
- [ ] Are async spawns, thread handoffs, and channel boundaries explicitly marked?
- [ ] Does the trace explicitly document error handling, retries, and rollback (avoiding N5)?
- [ ] Are all participants declared with double-quoted aliases and verified file anchors?
- [ ] Have all code links been verified against disk?
