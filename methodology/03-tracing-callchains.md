# 03. Systematic Call-Chain Tracing (Following the Golden Path)

## Why Trace Execution Flows?
Reading code horizontally (e.g. reading all models first, then reading all utils) is notoriously inefficient: you cannot observe how data structures mutate in real-world execution.

The fastest way to understand any unfamiliar system is: **pick a single canonical operation and follow its execution flow from ingress to terminal state.**

---

## The Four-Step Tracing Technique

### 1. Select the Golden Path Scenario
Never trace trivial utility commands like `--version` or `--help`. Choose the operation that defines the software's reason for being:
- Version control system: Trace a `commit` transaction;
- Web service: Trace an authenticated `POST` request committing state to storage;
- Workflow engine: Trace a task from parsing and scheduling to output emission.

### 2. Pinpoint the Trigger Entrypoint
Locate the entry point in CLI flag declarations (`main.go`, `cli.py`, `index.ts`) or HTTP router tables, identifying the root dispatcher (Handler / Controller).

### 3. Follow the Data (Data Flow Mutation)
Observe how the external request DTO is unmarshalled, validated, converted into a Domain Entity, and passed into the core engine.
Record key milestone transitions:
- Where are inputs validated and rejected?
- Where do state machine transitions or batch algorithms execute?
- Where are mutations committed to disk or dispatched across the network?

### 4. Graph the Sequence & Anchor Code Lines
Render a Mermaid `sequenceDiagram` and annotate each transition with **verified line-number markdown links** (e.g. `[src/engine.go#L45-L60]`), enabling one-click navigation for future reviews.
