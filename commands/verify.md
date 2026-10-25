# /verify (Alias: /audit) — Code Anchor & Line Number Verification

Executes `tools/verify_anchors.py` to deterministically verify that all code paths and line numbers referenced in study notes (e.g. `[src/engine.go#L45-L60]`) physically exist on disk, eliminating hallucinations.

---

## Operational Steps

### 1. Execute Verification Tool
Run against target study assets:
```bash
python tools/verify_anchors.py <target_path> studies/<repo_name>/ARCHITECTURE.md
python tools/verify_anchors.py <target_path> studies/<repo_name>/DEBUG_NOTES.md
```

### 2. Output Verification Audit Report
- **Total Anchors Scanned**: Number of file and line-number anchors detected;
- **Verified Valid**: Anchors where file exists and line range is within bounds;
- **Violations & Anomalies**:
  - Target file does not exist in target repository;
  - Line numbers exceed the actual line count of the file;
  - Inverted or illegal line ranges (e.g. `L50-L30`);
  - Path traversal attempts outside repository root.

### 3. In-Place Correction
If invalid anchors are flagged, re-read the live source file, correct the line numbers or paths in the notes, and re-run until 100% anchor validity is confirmed.

---

### Recommended Next Steps
1. **`/export`** — Once anchor validation passes, compile the standalone offline HTML study whitepaper.
2. **`/trace <Scenario>`** — Trace additional execution flows and anchor new line references.
