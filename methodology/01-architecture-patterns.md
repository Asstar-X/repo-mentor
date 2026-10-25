# 01. Architectural Pattern Recognition & Macro Layering

## Why Identify the Pattern First?
When onboarding to an unfamiliar codebase, the biggest mistake is diving straight into implementation details. Different types of systems adhere to fundamentally different organizational models:
- Compilers and build systems inherently use **Pipes & Filters** stage-by-stage pipelines;
- Web backends isolate persistence via **Layered / Clean Architecture**;
- Extensible developer tools rely on an ultra-minimal **Microkernel** exposing lifecycle hooks.

Pinpointing the macro pattern before opening individual files explains why top-level directories exist and how data flows through the system.

---

## Architectural Pattern Cheat Sheet

| Architecture Pattern | Canonical Examples | Directory Signatures | Data & Control Flow Characteristics |
| :--- | :--- | :--- | :--- |
| **Plugin / Microkernel** | VSCode, Webpack, Babel | `core/`, `plugins/`, `extensions/`, `hooks/` | Minimal core manages lifecycle and events; core capabilities inject via plugin registries. |
| **Pipes & Filters** | Compilers, Transcoders, ETL | `parser/`, `lexer/`, `stages/`, `pipeline/` | Data moves unidirectionally across discrete, immutable transformation stages. |
| **Event-Driven / Actor** | Game servers, Message brokers, NATS | `events/`, `handlers/`, `bus/`, `mailbox/` | Modules avoid direct synchronous calls, decoupling via message dispatching and consumption. |
| **Clean / Layered** | Enterprise backends, DDD services | `api/`, `service/`, `domain/`, `repository/` | Inward dependency rule. Core domain rules are isolated from databases or network transports. |
| **Workflow / Orchestration** | Automation scripts, Agent workflows | `commands/`, `skills/`, `tools/`, `prompts/` | Declarative specifications direct execution strategies, coordinated with deterministic scripts. |
| **WAL + State Machine** | Redis, etcd, SQLite | `wal/`, `storage/`, `raft/`, `engine/` | Write-Ahead Logs enforce durability before in-memory state machines update read/write states. |

---

## Systematic Recon Steps

1. **Establish System Boundaries**:
   - What are the inputs (CLI arguments, HTTP requests, message queues, file descriptors)?
   - What are the terminal outputs (stdout, local files, DB records, network payloads)?
   - What external infrastructure is required (OS system calls, external APIs, persistent volumes)?

2. **Graph the Architectural Topology (Mermaid)**:
   Clearly delineate:
   `External Input -> Ingress Dispatch -> Core Domain Engine -> Persistence / Outbound Network`.
