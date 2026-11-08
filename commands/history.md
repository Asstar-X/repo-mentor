# /history (Alias: /archeology) — Git Churn & Architecture Archaeology

Identifies architectural gravity via modification frequency analysis (Git Churn) and traces the genesis commit to reconstruct the author's original architectural model.

---

## Operational Steps

### 1. Execute Churn Analysis Tools
Run against the target repository root:
```bash
repo-mentor hotspots <target_path> --commits 300 --top 15 || python tools/git_hotspots.py <target_path> --commits 300 --top 15
```

---

### 2. Generate Git Evolution Report
Adhere strictly to `methodology/06-git-history-analysis.md`:

#### I. Top Churn Hotspots Ranking
- Display the Top 10–15 files modified most frequently over recent commits.
- **Healthy Core vs. Architectural Debt Diagnosis**:
  - High Churn + High Cohesion $\rightarrow$ **Healthy Core**: Evolving domain rules.
  - High Churn + Low Cohesion $\rightarrow$ **Architectural Debt**: God Object mixing I/O and scheduling, high regression risk.
  - Test File Churn $\rightarrow$ **Fragile Test Debt**: Tests coupled to implementation details.

#### II. Genesis Commit Archaeology (The MVP Hypothesis)
Run archaeological commands:
```bash
# Locate genesis commit hash
GENESIS_HASH=$(git rev-list --max-parents=0 HEAD | tail -n 1)

# Inspect initial commit structure and diff
git show --stat $GENESIS_HASH
```
- Analyze the minimal MVP (typically under 1,000 lines) that originally validated the core golden path.
- Observe the initial data structures before enterprise configuration and legacy shims were added.
- Trace major refactoring milestones that transitioned the prototype to the current architecture.

---

### 3. Archival & Matrix Update
1. Append the Git Churn and Genesis analysis to `studies/<repo_name>/ARCHITECTURE.md`.
2. Update `study_tracker.csv` to credit the 10% macro history score to global progress.

---

### Mastery Progress & Blind-Spot Analysis
- **Global Mastery Progress**: Adds 10% macro history score to baseline if not already granted.
- **Core Domain Coverage**: $m / k$
- **Blind-Spot Warning**: [Highlight unexplored Tier-0 domains]

### Recommended Next Steps
1. **`/drill <Hotspot Domain>`** — Stress-test failure recovery and concurrency limits on fragile high-churn modules.
2. **`/overview`** — Return to macro architecture to synthesize global progress.
