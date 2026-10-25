# 05. Core Data Structures & State Machine Invariants

## Data Structures Define Architectural Ceilings
As Linus Torvalds famously observed: *"Bad programmers worry about the code. Good programmers worry about data structures and their relationships."*

Truly mastering an unfamiliar codebase does not mean memorizing transient call stacks; it means mastering its **core data structures** and understanding **how lifecycle states transition**.

---

## Three Focal Points for Core Modeling

### 1. The Central Entities
Identify the primary objects that the entire architecture revolves around:
- Git revolves around `Blob`, `Tree`, `Commit`, and `Index`;
- Kubernetes revolves around `Pod`, `Node`, and `ReplicaSet`;
- Workflow engines revolve around `Task`, `Job`, and `DAGNode`;
- Analysis tools revolve around `AnalysisReport`, `AstNode`, and `MetricsMatrix`.

Understanding the central entity's field definitions reveals the author's internal mental model of the domain.

### 2. State Enums & Lifecycle State Machines
State fields (`Status`, `State`, `Phase`) are almost always defined as enums. Pinpoint them and identify:
- What are the valid states?
- What events trigger transitions between preceding and succeeding states?
- What transitions are strictly forbidden (and where does the code intercept illegal transitions)?

### 3. System Invariants
What fundamental truths must remain unbroken at all times during runtime?
- e.g., "Once an order enters `Paid`, its monetary balance is immutable";
- e.g., "A Raft leader only appends to its log, never overwriting its own entries";
- e.g., "A task execution lease can only be owned by a single worker at any instant."

Find where the codebase guards these invariants (typically in lock acquisition zones, transaction boundaries, or precondition assertions). That is where the architectural gravity lies.
