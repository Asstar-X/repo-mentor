# /history (Alias: /archeology) — Git Churn & Architecture Archaeology

Identifies high-churn files via modification frequency analysis (Git Churn) and traces the initial commit to uncover the original architectural intent.

---

## Operational Steps

### 1. Execute Churn Analysis Script
Run against the target repository root:
```bash
python tools/git_hotspots.py <target_path> --commits 300 --top 15
```

### 2. Generate Git Evolution Report
Adhere to `methodology/06-git-history-analysis.md`:

#### I. Top Churn Hotspots Ranking
- Display the Top 10 files modified most frequently over recent commits;
- Inspect source code to determine why: are these files naturally volatile due to evolving business rules, or structurally flawed due to low cohesion and excessive responsibilities?

#### II. Initial Commit Archaeology
- Retrieve the repository's earliest commit records and prototype snapshot;
- Analyze the minimal MVP (often only a few hundred lines) that originally proved out the core golden path;
- Trace the major refactoring milestones that evolved the initial prototype into the current production architecture.

---

### Mastery Progress & Blind-Spot Analysis
- **Global Mastery Progress**: Adds 10% macro history score to baseline if not already granted.
- **Core Domain Coverage**: $m / k$
- **Blind-Spot Warning**: [Highlight unexplored Tier-0 domains]

### Recommended Next Steps
1. **`/drill <Hotspot Domain>`** — Stress-test failure recovery and concurrency limits on fragile high-churn modules.
2. **`/overview`** — Return to macro architecture to synthesize global progress.
