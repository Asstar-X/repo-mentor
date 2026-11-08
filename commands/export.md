# /export (Alias: /report) — Offline HTML Architecture Manual Export

> **Backing Skill**: [`skills/repo-export/SKILL.md`](../skills/repo-export/SKILL.md)

Compiles accumulated study assets in `studies/<repo_name>/` (system positioning, architecture topologies, call chains, Q&A records, and limit scenario drills) into a standalone, single-file offline HTML technical whitepaper without external CDN dependencies.

---

## Operational Workflow

### 1. Pre-Export Quality Gate Audit
Before exporting, confirm that all study assets satisfy quality gates:
```bash
repo-mentor verify <target_path> studies/<repo_name>/ --fix
repo-mentor eval <target_path> studies/<repo_name>/
```
Ensure zero broken code anchors, valid Mermaid diagrams, and zero banned buzzwords.

---

### 2. Run Compilation Tool
```bash
# Compile and export standalone offline HTML whitepaper
repo-mentor export studies/<repo_name>/
```

The export engine automatically synthesizes and semantically structures:
- `studies/<repo_name>/README.md`
- `studies/<repo_name>/ARCHITECTURE.md`
- `studies/<repo_name>/DEBUG_NOTES.md`
- `studies/<repo_name>/traces/*.md`

---

### 3. Verify Output Asset
- Verify that `studies/<repo_name>/<repo_name>_architecture_manual.html` exists;
- Confirm the generated file is completely standalone and functional without network connectivity.
