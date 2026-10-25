# [Project Name] Source Walkthrough & Debug Journal

> Local Repository: `[Local Path]`  
> Date: YYYY-MM-DD  

---

## 1. Local Debugging & Smoke Run Commands

### Build & Test Commands
```bash
# Build
[Build command]

# Run smoke unit tests
[Test command]
```

### Golden Breakpoint Call Stack
```text
1. [Entrypoint Function]: [file:line]
2. [Intermediate Dispatch]: [file:line]
3. [Core Domain Loop]: [file:line]
```

---

## 2. Core Structures & Critical Gotchas

### 1. Core Data Structures
- `[Struct 1]`: [Fields & business modeling intent]
- Core Invariants: [e.g. Immobility, lock ordering, thread-safety assumptions]

### 2. Gotchas & Subtle Edge Cases
- [Gotcha notes, unexpected corner cases, or subtle legacy compatibility logic]

---

## 3. Limit Scenario Hypothesis & Drills

### Target Scenario Drill: [e.g. Adding an adapter or injecting network jitter]
1. Required File Changes:
   - [`[File 1]`](file:///[path]): [Detailed change description]
   - [`[File 2]`](file:///[path]): [Detailed change description]
2. Boundary & Test Verification:
   - [Unit and regression tests to add or execute]
