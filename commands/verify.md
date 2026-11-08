# /verify (Alias: /audit) — Code Anchor & Line Number Verification

Executes `repo-mentor verify` (or `tools/verify_anchors.py`) and the Anti-AI quality engine to deterministically verify that all code paths, line numbers, and symbols referenced in study notes (e.g. `[src/engine.go#L45-L60]`) physically exist on disk, eliminating hallucinations.

---

## Operational Steps

### 1. Execute Verification Tools
Run against target study assets:
```bash
# 1. Physical line number and symbol existence audit
repo-mentor verify <target_path> studies/<repo_name>/ARCHITECTURE.md || python tools/verify_anchors.py <target_path> studies/<repo_name>/ARCHITECTURE.md
repo-mentor verify <target_path> studies/<repo_name>/DEBUG_NOTES.md || python tools/verify_anchors.py <target_path> studies/<repo_name>/DEBUG_NOTES.md

# 2. Mermaid syntax and diagram formatting audit
python tools/verify_mermaid.py studies/<repo_name>/ARCHITECTURE.md --fix

# 3. Anti-AI fluff linting and rubric scoring (Gate 3)
repo-mentor eval studies/<repo_name>/ --check-fluff
```

---

### 2. Output Verification Audit Report
- **Total Anchors Scanned**: Number of file and line-number anchors detected;
- **Verified Valid**: Anchors where the file exists, symbol is present, and line range is within bounds;
- **Violations & Anomalies**:
  - Target file does not exist in the repository;
  - Line numbers exceed the actual line count of the file;
  - Inverted or illegal line ranges (e.g. `L50-L30`);
  - Path traversal attempts outside repository root (`../../`);
  - Banned buzzwords from the Blacklist (e.g. "*非常优雅*", "*highly decoupled* without code anchor").

---

### 3. In-Place Correction
If invalid anchors or fluff violations are flagged:
1. Re-read the live source file on disk;
2. Correct the line bounds, symbol identifiers, or phrasing in the notes;
3. Re-run `/verify` until 100% anchor validity and zero fluff violations are confirmed.

---

### Recommended Next Steps
1. **`/export`** — Once anchor validation and anti-fluff checks pass, compile the standalone offline HTML whitepaper.
2. **`/trace <Scenario>`** — Trace additional execution flows and anchor new line references.
