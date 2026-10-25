# 04. Identifying & Filtering Boilerplate Glue Code

## Cognitive Bandwidth Management
In production repositories, 80% to 90% of all lines are boilerplate and infrastructure glue. While indispensable for operational robustness, these lines convey almost zero design signal about the core system.

Reading line-by-line leads directly to cognitive exhaustion. You must actively filter them.

---

## Code Patterns to Skim or Skip

| Code Category | Manifestation | Recommended Handling |
| :--- | :--- | :--- |
| **CLI Argument & Flag Parsing** | Long definitions using `argparse`, `cobra.Command`, `clap`, `commander` | Note the flags supported; skip the repetitive descriptions. |
| **Config & Env Variable Loading** | YAML/JSON reading, env binding, default fallback assignment | Focus solely on the final `Config` struct definition. |
| **Logging & Distributed Tracing** | Embedded `log.Infof(...)`, `logger.Debug(...)`, span injections | Ignore completely; avoid letting log strings obscure control flow. |
| **Defensive Null Checks & Error Wraps**| Repetitive `if err != nil`, re-thrown `try...catch` blocks | Unless explicit retry or circuit-breaker policies exist, skip standard wraps. |
| **DTO to Domain Object Mapping** | Manual field-by-field assignment between requests and entities | Mechanical plumbing; observe the source and destination types and move on. |

---

## High-Leverage Code Deserving Deep Focus

1. **Core Data Structure Definitions** (Field names directly reflect domain models and memory trade-offs);
2. **State Machine Transition Guards** (Conditions that gate moving from State A to State B);
3. **Concurrency Synchronization Points** (Lock acquisition order, channel capacities, lifecycle ownership);
4. **Primary Computational Loops & Scheduling Algorithms**.
