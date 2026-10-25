# 07. Verifying Comprehension via Hypothesis Drills & Active Debugging

## Validating True Codebase Mastery
There is a massive chasm between "reading the documentation" and "truly understanding the system." Passive reading routinely creates the illusion of mastery, which shatters the moment you attempt to modify the code.

The two most effective ways to verify comprehension are: **hypothetical modification drills** and **active breakpoint debugging**.

---

## Method 1: Hypothetical Modification Drills

Formulate concrete engineering questions and identify exact code modifications:

1. **Ingesting a New Input**:
   - If adding a new CLI flag, environment variable, or API endpoint, which files require modification?
   - As the parameter travels from ingress to the core engine, which data structs encapsulate it?

2. **Swapping an Infrastructure Dependency**:
   - If replacing local disk persistence with an S3 bucket or Redis cluster, which files are impacted?
   - Does core domain logic remain untouched? If the core engine requires changes, the architecture is tightly coupled.

3. **Simulating Transient Failures**:
   - If a crash occurs midway through execution, how is partial state reclaimed?
   - Are system invariants preserved under sudden process termination?

---

## Method 2: Falsification & Constructing Counterexamples

Developers frequently succumb to confirmation bias: because a repository is well-known or heavily starred, they assume every line is flawless, often rationalizing questionable code.

**The ultimate test of architectural comprehension is attempting to logically break the system:**

1. **Constructing Interleaved Concurrency Flaws**:
   - Imagine two threads entering a critical section concurrently. Is there a Time-of-Check to Time-of-Use (TOCTOU) race condition?
2. **Constructing Network & I/O Vulnerabilities**:
   - If an RPC endpoint or database hangs for 10 seconds, does the thread pool exhaust itself? Is backpressure enforced?
3. **Acknowledging Technical Debt**:
   - When encountering crude global locks, missing cancellation propagation, or unbounded queues, label them as architectural debt rather than rationalizing them.

---

## Method 3: Active Debugging & Smoke Unit Testing

1. **Run Targeted Unit Tests First**:
   Unit tests are executable documentation left by the original maintainers. Read test fixtures in `tests/` to see exact inputs, mock boundaries, and expected return assertions.
2. **Walk the Golden Breakpoint Call Stack**:
   Set a breakpoint at the core dispatch pivot. Step in directly to observe the live call stack depth, runtime memory allocations, and state transitions.
