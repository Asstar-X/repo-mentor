# /verify (Alias: /audit) — Code Anchor & Quality Gate Verification

> **Backing Skill**: [`skills/repo-verify/SKILL.md`](../skills/repo-verify/SKILL.md)

Executes deterministic static analysis to verify that all code paths, line ranges, symbols, and Mermaid diagrams referenced in study documentation physically exist and render cleanly on disk, eliminating hallucinations and AI marketing fluff.

---

## Operational Workflow

### 1. Execute Verification Tools
```bash
# 1. Physical line number, symbol existence, and Mermaid diagram audit (with auto-fix)
repo-mentor verify <target_path> studies/<repo_name>/ARCHITECTURE.md --fix
repo-mentor verify <target_path> studies/<repo_name>/DEBUG_NOTES.md --fix
repo-mentor verify <target_path> studies/<repo_name>/traces/ --fix

# 2. Anti-AI fluff linting and 100-point rubric evaluation
repo-mentor eval <target_path> studies/<repo_name>/
```

---

### 2. Output Verification Audit Report
- **Total Anchors Scanned**: Count of file and line-number anchors detected;
- **Verified Valid (100% Target)**: Anchors where file exists, line bounds are within EOF, and symbol is grounded;
- **Mermaid Health**: Verified diagrams render with zero syntax errors;
- **Anti-Fluff Score**: Count of banned buzzwords detected (target: 0) and ungrounded long paragraphs flagged.
