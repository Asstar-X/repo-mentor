---
name: repo-mentor
description: >
  Universal open-source codebase reading companion and deep architecture analysis toolkit.
  Transforms unfamiliar Git repositories into GitHub High-Star engineering blueprints across major
  ecosystems (Go, Rust, Python, TypeScript, Java, C++). Enforces strict anti-AI reading standards,
  filters boilerplate glue code, maps 5-phase golden execution paths, extracts state machine invariants,
  audits architectural trade-offs, and stress-tests limit scenarios.
allowed-tools: Read, Write, Edit, Glob, Grep, RunCommand, AskUserQuestion
framework_version: 1.2.0
---

# Repo Mentor — Universal Codebase Architecture & Anti-AI Reading Assistant

`repo-mentor` is an engineering-grade companion and static analysis toolkit designed to dismantle unfamiliar software repositories without the shallow, repetitive clichés common to generic AI summaries. It operates both as an ergonomic CLI executable (`repo-mentor`) and as an autonomous agent skill protocol.

---

## 0. The 5-Level Cognitive Zooming Framework

All analysis in `repo-mentor` follows the **5-Level Cognitive Zooming** framework (from macro to micro):

```
[Level 1: Why]        Problem Space & First-Principles Tension (No code lines; real-world pain & tension)
      ⬇️
[Level 2: Strategy]   Metaphor, Cast of Characters & Macro Topology (The Cast, 3~5 core human roles)
      ⬇️
[Level 3: Example]    Concrete Walkthrough: A Day in the Life of Data (Trace ONE concrete event & payload diff)
      ⬇️
[Level 4: Deep Dive]  Keystone Invariants, Core Algorithms & AST Fact Anchors (Exact code lines & limits)
      ⬇️
[Level 5: Takeaway]   Architecture Trade-offs & Transposable Patterns (Engineering lessons to take away)
```

---

## 1. Unified Command Reference

| Command | Aliases | Description & Architectural Focus | CLI Tool Equivalent |
| :--- | :--- | :--- | :--- |
| **`/overview [path/url]`** | `/recon`, `/blueprint` | Direct onboarding: Silent asset initialization, macro architecture classification, 3-tier module priority triage (Tier-0/1/2), golden path sequence diagram, and domain matrix baseline. | `repo-mentor scan <path>`<br/>`repo-mentor map <path>` |
| **`/guide`** | `/roadmap` | Actionable smoke-run roadmap: Exact local build and targeted unit test commands, progressive reading order, and golden breakpoint stack. | `repo-mentor scan <path> --entrypoints` |
| **`/trace <domain/flow>`** | `/flow` | Trace end-to-end 5-phase call flow for a core domain; verify line-number anchors and sync/async boundaries (contributes 35% to domain score). | `repo-mentor ast <path> --calls` |
| **`/core <domain>`** | `/models` | Filter boilerplate to model domain ontologies, lifecycle state machines, and system invariants (contributes 35% to domain score). | `repo-mentor ast <path> --symbols` |
| **`/history`** | `/archeology` | Analyze Git churn hotspots over recent commits and inspect genesis commit architecture archaeology (contributes 10% to macro score). | `repo-mentor hotspots <path>` |
| **`/drill <domain>`** | `/quiz`, `/interview` | Socratic architecture defense: 2 destructive limit scenarios (crash recovery, concurrency races, blast radius) (contributes 30% to domain score). | `repo-mentor eval <study_dir>` |
| **`/verify`** | `/audit` | Deterministically verify the physical existence of all file paths, symbol locations, and line-number anchors against live code. | `repo-mentor verify <path> <file>` |
| **`/export`** | `/report` | Compile accumulated study notes into a standalone, single-file offline interactive HTML study whitepaper with zoomable Mermaid diagrams. | `repo-mentor export <study_dir>` |
| **`/tracker`** | `/stats` | Display global study progress, core functional domain coverage matrix dashboard, and architecture pattern radar. | `repo-mentor scan --stats` |

---

## 2. Single Source of Truth Index (Thin-Pointer Design)

`repo-mentor` follows a modular thin-pointer design. All commands, methodology guides, and templates are indexed centrally:

| Category | File Path | Scope & Engineering Standard |
| :--- | :--- | :--- |
| **Command** | [`commands/overview.md`](commands/overview.md) | Macro pattern classification, 3-tier triage matrix, topology diagram, domain baseline |
| **Command** | [`commands/guide.md`](commands/guide.md) | Local build/smoke test commands, 4-step progressive reading order, golden breakpoints |
| **Command** | [`commands/trace.md`](commands/trace.md) | 5-phase Golden Path call chain walkthrough, sync/async hops, sequence diagrams |
| **Command** | [`commands/core.md`](commands/core.md) | Domain entity modeling, state machine transitions, illegal guard checks, invariants |
| **Command** | [`commands/history.md`](commands/history.md) | Git churn hotspots (power law distribution) and genesis commit MVP archaeology |
| **Command** | [`commands/drill.md`](commands/drill.md) | Destructive limit scenarios, concurrency race counterexamples, technical debt audit |
| **Command** | [`commands/verify.md`](commands/verify.md) | Deterministic code anchor audit, physical line range bounds, and symbol existence |
| **Command** | [`commands/export.md`](commands/export.md) | Offline single-file HTML whitepaper compiler with responsive monochrome layout |
| **Command** | [`commands/tracker.md`](commands/tracker.md) | Global repository learning progress, domain coverage dashboard, and pattern radar |
| **Methodology** | [`methodology/01-architecture-patterns.md`](methodology/01-architecture-patterns.md) | Pattern topologies, structural signatures vs directory names, Anti-patterns N1 & N4 |
| **Methodology** | [`methodology/02-module-boundaries.md`](methodology/02-module-boundaries.md) | Tier-0/1/2 triage, inward dependency rules, interface inversion, Anti-pattern N3 |
| **Methodology** | [`methodology/03-tracing-callchains.md`](methodology/03-tracing-callchains.md) | 5-phase Golden Path tracing, sync/async boundary hops, Anti-pattern N5 |
| **Methodology** | [`methodology/04-skipping-boilerplate.md`](methodology/04-skipping-boilerplate.md) | 80% boilerplate filtering, 20% load-bearing invariants, Anti-pattern N7 |
| **Methodology** | [`methodology/05-data-structures-and-states.md`](methodology/05-data-structures-and-states.md) | Keystone entities, state machine transitions, forbidden guards, invariant code anchors |
| **Methodology** | [`methodology/06-git-history-analysis.md`](methodology/06-git-history-analysis.md) | Code churn gravity, healthy vs debt diagnosis, genesis commit archaeology |
| **Methodology** | [`methodology/07-verifying-understanding.md`](methodology/07-verifying-understanding.md) | Triple-Anchor Rule, 3-tier confidence labeling, counter-factual challenge drills |
| **Methodology** | [`methodology/08-untrusted-repo-security.md`](methodology/08-untrusted-repo-security.md) | Prompt injection defense, static-first rule, path containment, data privacy |
| **Template** | [`templates/ARCHITECTURE.md`](templates/ARCHITECTURE.md) | Production architecture specification blueprint with trade-offs and failure modes |
| **Template** | [`templates/DEBUG_NOTES.md`](templates/DEBUG_NOTES.md) | Source walkthrough journal, golden breakpoints, and limit scenario challenge logs |
| **Template** | [`templates/STUDY_INDEX.md`](templates/STUDY_INDEX.md) | Study index, $k$-domain coverage matrix, mathematical progress gating, and radar |

---

## 3. The 9 Negative Anti-Patterns (The Negative Taxonomy N1–N9)

Generic AI code explanations routinely suffer from eight characteristic pathologies. In `repo-mentor`, violating any of these patterns incurs immediate penalty or disqualification:

| # | Anti-Pattern | Description & Typical Symptoms | Engineering Root Cause | Disqualification Rule |
| :---: | :--- | :--- | :--- | :--- |
| **N1** | **Directory Parroting**<br/>(目录机械复述) | Translating folder names into literal descriptions (e.g. "*`utils/` stores utilities, `models/` stores data models*"). | Zero information gain; conceals actual runtime execution. | More than 3 generic directory descriptions without role or dependency direction fails audit. |
| **N2** | **Buzzword Stacking**<br/>(空洞术语堆砌) | Unanchored praise: "*highly decoupled, robust, flexible, enterprise-grade architecture*". | Masking ignorance of code-level mechanisms with buzzwords. | Any buzzword lacking code-level line anchor within 50 words is flagged and penalized. |
| **N3** | **Flat Enumeration**<br/>(扁平无优先级) | Listing all directories or files alphabetically without distinguishing core from glue. | Wasting 80% of reading bandwidth on peripheral plumbing. | Missing Tier-0 / Tier-1 / Tier-2 triage matrix is an immediate one-strike rejection. |
| **N4** | **Phony Static Boxes**<br/>(静态假架构图) | Mermaid boxes containing names without call sequences, protocols, or network/process boundaries. | Superficial diagramming that cannot guide debugging. | Architecture diagram must label protocol and process boundaries with data flow direction. |
| **N5** | **Happy Path Bias**<br/>(快乐路径偏见) | Tracing only successful execution; ignoring error bubbling, retries, timeouts, and rollbacks. | Real-world software spends 70% of complexity on failure defense. | Call chain trace with zero error handling or boundary defense fails review. |
| **N6** | **Floating Anchors**<br/>(浮动无根引用) | Citing bare file names (`engine.py`) or nonexistent symbols without exact start/end line bounds. | Hallucination or laziness; cannot be verified by automated tools. | Unanchored assertions or broken line bounds fail verification gate. |
| **N7** | **Boilerplate Domination**<br/>(胶水代码反客为主) | Spending pages analyzing CLI flags (`argparse`/`cobra`), config loading, or logger setups. | Avoiding difficult algorithmic cores by focusing on easy glue code. | Explaining CLI flags or configuration beyond 3 summary lines is prohibited. |
| **N8** | **Debt Rationalization**<br/>(缺陷美化与盲目崇拜) | Praising God Objects, global mutable locks, or swallowed errors as "*clever lightweight design*". | Sycophancy and lack of technical critical discernment. | Study assets must feature an objective `Trade-offs & Technical Debt` audit. |
| **N9** | **Premature Grounding Overload**<br/>(认知早熟/行号过度前置) | Dumping microscopic code lines, function calls, and system calls before establishing the real-world pain point (Why), metaphor, cast of characters, and concrete walkthrough data journey. | Inverting cognitive learning hierarchy; induces reader cognitive overload and disorientation. | Level 1 and Level 2 must not contain internal code line numbers. Concrete data scenario must precede detailed code traces. |

---

## 4. The Banned Phrasing Blacklist (50+ Fluff Terms)

The following phrases are **strictly prohibited** in all generated reports and agent dialogues unless citing historical documentation verbatim:

### Prohibited Chinese Phrases (严禁中文违禁词)
1. `非常优雅` / `设计极其优雅`
2. `架构清晰` / `结构十分严谨`
3. `高度解耦` (后无具体接口解耦代码依据)
4. `高内聚低耦合` (后无代码佐证)
5. `极高的可用性` / `极强的高可用性`
6. `极高的灵活性` / `极具扩展性`
7. `健壮的异常处理` (后无重试/熔断机制)
8. `巧妙的权衡` / `巧妙的设计` (美化缺陷)
9. `工业级设计` / `企业级架构`
10. `行业标杆` / `业界典范`
11. `开箱即用`
12. `一目了然` / `不言而喻`
13. `显而易见` / `不难发现`
14. `众所周知` / `毋庸置疑`
15. `值得注意的是` (无依据口头禅)
16. `顾名思义`
17. `首先...其次...总的来说` (八股文套路)
18. `今天我们来一起学习` / `让我们深入探索`
19. `可以说是一个非常优秀的开源项目`
20. `作者的代码功底非常深厚`
21. `体现了极高的编程素养`
22. `完美契合` / `无可挑剔`
23. `综上所述` / `由此可见` (无事实推演)
24. `毋庸赘述`
25. `非常好的一点是`

### Prohibited English Phrases (Banned Fluff Terms)
26. `elegant` / `elegantly designed`
27. `beautifully crafted` / `masterclass in`
28. `highly decoupled` (without citing interface code)
29. `high cohesion and low coupling`
30. `highly scalable` / `infinitely extensible`
31. `enterprise-grade` / `production-ready`
32. `robust error handling` (without retry/backoff code)
33. `clever trade-off` (used to rationalize debt)
34. `state-of-the-art`
35. `industry-standard`
36. `out of the box`
37. `crystal clear` / `self-explanatory`
38. `as we all know` / `it goes without saying`
39. `needless to say`
40. `firstly... secondly... in summary`
41. `let's dive in` / `let's explore`
42. `great question!` (sycophantic opener)
43. `that's a very deep insight!`
44. `testament to the author's skill`
45. `impeccably structured`
46. `seamless integration`
47. `blazing fast`
48. `intuitive and powerful`
49. `game changer`
50. `sophisticated architecture`
51. `clean and neat`
52. `flawless execution`

---

## 5. The 100-Point Quantitative Rubric

Reports are evaluated by `repo-mentor eval` across five core dimensions (Total: 100 points). Any one-strike condition results in immediate disqualification:

| Dimension | Weight | Scoring Criteria (85–100: High-Star, 60–84: Passing, <60: Fail) | One-Strike Disqualification |
| :--- | :---: | :--- | :--- |
| **D1: Fact Grounding & Verification** | **25%** | 100% of claims cite verified `[path#Lstart-Lend]` line bounds, precise symbols, and load-bearing snippets (3–8 lines). Full 3-tier confidence labeling (`[Verified Fact]`, `[Engineering Inference]`, `[Unverified Hypothesis]`). | Nonexistent file or symbol; unanchored factual claims; line bounds out of range. |
| **D2: Core Abstraction & Invariants** | **20%** | Extracts 2–4 keystone entities with field-level intent; maps lifecycle state machine; identifies forbidden transitions and code guard intercepts; locates unbroken system invariants with lock/CAS code anchors. | Flat entity listing; zero state machine modeling; failure to identify invariants. |
| **D3: Execution Flow & Dynamics** | **20%** | Golden path covers all 5 phases (Ingress -> Dispatch -> Engine -> Persistence -> Response); Mermaid sequence diagram with quoted participant aliases; explicitly marks sync/async boundaries and thread/network hops. | Static box diagram only; zero dynamic sequence; tracing trivial utility or CLI flag parsing. |
| **D4: Failure Modes & Edge Cases** | **20%** | Comprehensive failure analysis: error bubbling hierarchy (fatal/transient/swallowed), retry with exponential backoff & jitter, partial failure rollback, resource leak defenses. | Happy-path-only analysis; ignoring network timeouts, concurrency races, or crashes. |
| **D5: Trade-offs & Anti-AI Purity** | **15%** | Zero sycophancy or banned buzzwords; explains why authors chose Pattern A over Pattern B; conducts objective technical debt audit (God Object, lock contention, missing backpressure). | Empty praise (e.g. "*very elegant*"); unanchored buzzwords; rationalizing code debt. |

---

## 6. The 5 Positive Engineering Standards

1. **Fact Grounding (The Triple-Anchor Rule)**: Every claim must cite relative file path, line bounds `[path#Lstart-Lend]`, symbol identifier, and a load-bearing snippet.
2. **Invariants & Forbidden Transitions**: Extract the fundamental truths the system defends under concurrency and failure. Point to the physical lock, CAS, or assertion code enforcing each invariant.
3. **The Golden Path (End-to-End Execution)**: Trace the single high-value workflow that justifies the system's existence across the 5 canonical phases.
4. **Architectural Trade-offs & Debt Audit**: Software engineering is the art of compromise. Quantify what was sacrificed (latency vs durability, memory vs locality, simplicity vs flexibility). Objectively expose technical debt.
5. **Defense-in-Depth & Failure Modes**: Document how the system survives when inputs are corrupted, connections hang, threads race, or the process receives `SIGKILL`.

---

## 7. Mermaid Diagram Standards

All diagrams must follow strict formatting rules to prevent rendering crashes:
- **Standalone Flush Code Blocks**: Mermaid blocks must start flush left ````mermaid` with blank lines before and after. Never indent under bullet lists.
- **Quoted Participant Aliases**: In sequence diagrams, always use quoted aliases:
  `participant E as "Core Engine (src/core/engine.go#L40)"`
- **Quoted Node Labels**: In flowcharts, always double-quote node labels:
  `Node["Scheduler (src/scheduler.py#L30-L60)"]`
- **No Scope Operators in State Diagrams**: Use `.` instead of C++ `::` in `stateDiagram-v2` (e.g. `AllocStatus.NEVER`).
- **No Reserved Keywords**: Never name a node `end`, `subgraph`, `graph`, `class`, or `style`.
- **Pre-Commit Linting**: Run `repo-mentor verify --mermaid` to detect syntax errors.

---

## 8. Response Footer Protocol

Every command response generated by `repo-mentor` **MUST** conclude with:

```markdown
---

### Mastery Progress & Blind-Spot Analysis
- **Global Mastery Progress**: [Calculated]% (Macro Base 25% + Core Domain Coverage 75%)
- **Core Domain Coverage**: m / k (Covered Core Domains / Total Identified Tier-0 Domains)
- **Blind-Spot Warning**: [List all Tier-0 core domains not yet walked through or modeled]
  > Gating Notice: While blind spots persist, mastery progress is mathematically hard-capped below 100%.

### Recommended Next Steps
1. **`/command_1`** — [One-line actionable technical rationale for current context]
2. **`/command_2`** — [One-line actionable technical rationale for current context]
```
