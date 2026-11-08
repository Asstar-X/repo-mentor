"""tests.test_html_compiler: Tests for dynamic single-file HTML whitepaper compiler."""

import tempfile
from pathlib import Path

from repo_mentor.export.html_compiler import (
    _extract_challenges_dynamically,
    compile_study_html,
)


def test_dynamic_challenge_extraction_from_markdown():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        debug_notes = root / "DEBUG_NOTES.md"
        debug_notes.write_text("""
# Debug Notes

## 3. Limit Scenario Hypothesis & Drills

### Limit Drill Scenario 1: Crash Recovery & Dual Persistence (Crash Recovery)
- **Failure Scenario**: Ingress process killed during async vector sync.
- **Architectural Focus**: Isolation of dirty in-memory state.
- **Reference Solution**: Rollback uncommitted transactions via RAII guard.
- **Architectural Verdict**: Dual write consistency is preserved via strict sequence boundaries.

### Limit Drill Scenario 2: High Concurrency TOCTOU Race (Concurrency Hazard)
- **Failure Scenario**: Two concurrent workers submit identical entity records.
- **Architectural Focus**: Idempotency and locking order.
- **Reference Solution**: Wrap upsert in scoped mutex.
- **Architectural Verdict**: Atomic compare-and-swap prevents split-brain state.
""")

        challenges = _extract_challenges_dynamically(root, "sample-repo")
        assert len(challenges) == 2
        assert challenges[0]["tag"] == "Crash Recovery"
        assert "Crash Recovery & Dual Persistence" in challenges[0]["title"]
        assert "Ingress process killed" in challenges[0]["scenario"]
        assert "Isolation of dirty in-memory state" in challenges[0]["focus"]

        assert challenges[1]["tag"] == "Concurrency Hazard"
        assert "High Concurrency TOCTOU Race" in challenges[1]["title"]


def test_zero_canned_boilerplate_in_compiler():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "ARCHITECTURE.md").write_text("# Gin Web Engine Architecture\n" + "Body text\n")
        (root / "DEBUG_NOTES.md").write_text("# Gin Debug Notes\n")

        out_html = root / "dist" / "index.html"
        compile_study_html(root, output_file=out_html)

        assert out_html.is_file()
        content = out_html.read_text(encoding="utf-8")

        # CRITICAL VERIFICATION: No canned DeepInfer or generic GPU/driver boilerplate
        assert "deepinfer" not in content.lower()
        assert "driver/worker adapter modules" not in content.lower()
        assert "pre-allocated pools eliminate gc/allocation pauses" not in content.lower()
        assert "deferring kv block release" not in content.lower()
        assert "npu hardware backend" not in content.lower()


def test_empty_study_fallback_card():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "ARCHITECTURE.md").write_text("# Empty Architecture\n")

        challenges = _extract_challenges_dynamically(root, "empty-repo")
        assert len(challenges) == 1
        assert challenges[0]["tag"] == "Study Status"
        assert "drills pending" in challenges[0]["title"].lower()
        assert "empty-repo" in challenges[0]["scenario"].lower()


def test_compile_study_html_end_to_end():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "ARCHITECTURE.md").write_text("""
# Sample Service

## 1. System Positioning
Service overview.

```mermaid
graph TD
    A[Ingress] --> B[Core Engine]
```
""")
        traces_dir = root / "traces"
        traces_dir.mkdir()
        (traces_dir / "trace_1.md").write_text("""
# Execution Flow Trace 1

```mermaid
sequenceDiagram
    Client->>Server: Request
    Server-->>Client: Response
```
""")

        out_file = root / "manual.html"
        res_path = compile_study_html(root, output_file=out_file)

        assert Path(res_path).is_file()
        html_code = Path(res_path).read_text(encoding="utf-8")

        assert "<!DOCTYPE html>" in html_code
        assert "REPO-MENTOR" in html_code
        assert "Architecture Diagram #1" in html_code
        assert "Architecture Diagram #2" in html_code
        assert "zoomMermaid" in html_code
        assert "btn-zoom" in html_code
