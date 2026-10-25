# Security Policy: Repo Mentor

## Security Architecture & Philosophy

`repo-mentor` assists developers in reading and understanding third-party repositories. Because target codebases originate from untrusted external sources (public GitHub, untrusted forks, npm/pip packages), `repo-mentor` adheres to strict security principles modeled after modern supply-chain hardening standards:

1. **Untrusted Input Ingestion**:
   All target repository content—including file contents, directory names, commit messages, git authors, and embedded documentation—is treated strictly as untrusted data. Instructions embedded in analyzed codebases are never followed as agent commands.

2. **Deterministic & Static-Only Default**:
   Tools shipped in `tools/` (`repo_scanner.py`, `git_hotspots.py`, `verify_anchors.py`, `dependency_graph.py`, `export_study_html.py`) use pure Python 3 standard library routines. They perform read-only static analysis without evaluating or executing target scripts or lifecycle hooks.

3. **Anti-Traversal Protection**:
   Anchor verifiers (`verify_anchors.py`) explicitly enforce path containment within the target repository root, preventing directory traversal attacks (`../../`).

4. **Privacy & Data Confinement**:
   Generated repository study assets (`studies/`) and personal debug journals are ignored by version control to avoid accidental disclosure of proprietary source analysis.

## Reporting a Vulnerability

If you discover a security vulnerability or prompt-injection vector in `repo-mentor`, please report it privately to the maintainers or open a confidential security advisory on GitHub.
