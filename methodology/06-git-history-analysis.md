# 06. Git History Archaeology & Churn Hotspot Analysis

## Objective
Establish an empirical methodology for discovering architectural gravity and design intent through Git history. Utilize code churn analysis to pinpoint high-volatility hotspots, and perform commit archaeology on genesis commits to reconstruct the author's original architectural model.

---

## 1. The Power Law of Code Churn

Static inspection of a git checkout shows all files as equal citizens on disk. In reality, software modification activity follows a steep power law (Pareto distribution):
- **Long-tail static files** (60%–80% of files): Leaf utilities, configuration schemas, and static constants are created once and rarely touched.
- **Architectural Hotspots** (5%–10% of files): The core scheduling loop, connection multiplexer, or transaction coordinator is modified in almost every release.

By measuring revision frequency and churn volume, engineers bypass guesswork and immediately locate where systemic complexity congregates.

```
Modifications
     ▲
     │  █
     │  █ █
     │  █ █ █
     │  █ █ █ █ 
     │  █ █ █ █ █ █ ▂ ▂ ▂ ▂ ▂ ▂ ▂ ▂ ▂ ▂ ▂ ▂ ▂ ▂
     └────────────────────────────────────────► Files
        ◄─ Top 5% Hotspots ─► ◄─ Static Long Tail ─►
```

### Churn Calculation Command
Extract high-churn hotspots over the last 300 commits using standard git commands:
```bash
git log --format=format: --name-only --since="1 year ago" \
  | egrep -v '^$' \
  | sort \
  | uniq -c \
  | sort -nr \
  | head -n 15
```

---

## 2. Diagnosing Churn: Healthy Evolution vs. Architectural Debt

Not all high churn indicates good design. When analyzing a hotspot file, diagnose its root cause:

| Hotspot Characteristic | Diagnosis | Architectural Implication |
| :--- | :--- | :--- |
| **High Churn + High Cohesion** | **Healthy Core Gravity** | The file coordinates core domain rules (e.g., `pkg/scheduler/schedule.go`). Frequent commits reflect evolving business requirements. |
| **High Churn + Low Cohesion (God Object)**| **Architectural Debt** | The file exceeds 2,000 lines, mixes I/O with computation, and is modified by every team member. Indicates failure to decompose responsibilities. |
| **High Churn in Test Files** | **Fragile Test Debt** | Tests are tightly coupled to implementation details rather than external contracts, breaking whenever internal refactorings occur. |
| **Zero Churn + High Call Depth** | **Mature Foundational Primitive** | Rock-solid leaf algorithm or data structure (e.g., custom bitset or hash function) that rarely needs modification. |

---

## 3. Genesis Commit Archaeology

### The Initial MVP Hypothesis
Before an open-source project grew to 50,000 lines with enterprise flags, telemetry, and legacy shims, it started as a clean prototype under 1,000 lines. The **Genesis Commit** contains the purest representation of the author's core algorithm:
- No bloated configuration frameworks;
- No backwards-compatibility hacks;
- Only the core golden path and data structure needed to solve the original problem.

### Archaeological Commands
```bash
# 1. Locate the repository genesis commit hash
GENESIS_HASH=$(git rev-list --max-parents=0 HEAD | tail -n 1)

# 2. Inspect the commit message and file structure
git show --stat $GENESIS_HASH

# 3. Read the initial prototype implementation
git show $GENESIS_HASH:src/main.py  # Adjust path to genesis entrypoint
```

### Archaeological Reading Strategy
1. **Analyze the Problem Statement**: Read the genesis `README.md` or initial commit message to understand what single problem the project was created to solve.
2. **Observe the Initial Golden Path**: How did the first commit pass data from input to output without middleware?
3. **Trace Refactoring Milestones**: Use `git log --grep="refactor" --oneline` to locate when the project transitioned from a prototype to a modular architecture.

---

## 4. Git Churn Matrix Standard

When generating repository documentation in `ARCHITECTURE.md`, format the churn analysis table as follows:

| Rank | File Path | Commits (Last 300) | Net Lines Changed | Primary Responsibility | Architectural Health Assessment |
| :---: | :--- | :---: | :---: | :--- | :--- |
| 1 | `pkg/engine/dispatcher.go` | 84 | +3,420 / -1,150 | Worker pool dispatch & queue routing | **Healthy Core**: High activity aligns with scheduling optimizations. |
| 2 | `pkg/common/utils.go` | 61 | +1,890 / -920 | Grab-bag helper functions | **Architectural Debt**: High churn indicates lack of domain scoping. |
| 3 | `pkg/storage/wal.go` | 42 | +850 / -310 | Fsync synchronization & log compaction | **Critical Invariant**: Core durability engine under continuous hardening. |

---

## 5. Verification Checklist

Before accepting Git history conclusions:
- [ ] Was churn calculated over a representative window (e.g. last 200–500 commits)?
- [ ] Are top churn hotspots categorized as either healthy core or architectural debt?
- [ ] Was the genesis commit examined to extract the author's original mental model?
- [ ] Are the findings documented with concrete commit hashes and file links?
