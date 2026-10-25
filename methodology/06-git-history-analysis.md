# 06. Git History Archaeology & Churn Hotspot Analysis

## Why Codebase History Outweighs Static Snapshots
Production codebases evolve continuously under real-world pressures. After years of iteration, a codebase accumulates peripheral fixes, legacy shims, and backwards-compatibility patches. Looking solely at current HEAD makes it difficult to distinguish core architectural bones from defensive patches.

Auditing Git history unlocks two high-leverage insights:

---

## 1. Locating Architectural Gravity via Git Churn
In any software repository, the distribution of maintenance activity across files follows a power law:
- Static utilities (`utils.py`, `strings.go`) are committed once and left untouched for years;
- Files orchestrating state machines, resource allocations, and dispatch loops are modified in almost every release.

By measuring commit frequency and churn volume (`git log --numstat`):
- **High-churn files with substantial volume** invariably represent the architectural center of gravity.
- Focusing on the Top 5 to 10 hotspots provides the highest return on investment for understanding systemic risk.

---

## 2. Examining the Genesis Commit (Architecture Archaeology)

```bash
git rev-list --max-parents=0 HEAD
git show <genesis_commit_hash>
```

Most prominent open-source projects started as clean, focused prototypes under 1,000 lines of code:
- No bloated configuration frameworks;
- No sprawling legacy compatibility layers;
- Just the purest, simplest minimal implementation that proved out the author's initial hypothesis.

Spending ten minutes reading the initial commit reveals the author's original vision and how the golden path was originally designed before complexity set in.
