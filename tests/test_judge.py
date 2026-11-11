"""tests.test_judge: Comprehensive Test Suite for 100-Point Rubric Automated Judge.

Tests:
- Dimensional score calculations across D1, D2, D3, D4, D5
- Grade A (High-Star Quality) qualification
- Automatic failure / gating on hallucinations (non-existent files or phantom symbols)
- Strict mode vs non-strict mode enforcement
- JSON format vs Rich console output format
- Sequence diagram call-hop verification integration
"""

from pathlib import Path

import pytest

from repo_mentor.verification.judge import RubricJudge, evaluate_report


@pytest.fixture
def mock_codebase(tmp_path: Path) -> Path:
    """Creates a small mock codebase for judge tests."""
    repo = tmp_path / "judge_repo"
    repo.mkdir()

    # Core source file
    code = (
        "package core\n"
        "\n"
        "type Router struct {\n"
        "    Routes []string\n"
        "}\n"
        "\n"
        "func (r *Router) Dispatch(path string) bool {\n"
        "    return true\n"
        "}\n"
    )
    (repo / "router.go").write_text(code, encoding="utf-8")
    return repo


def test_judge_grade_a_high_star(mock_codebase: Path, tmp_path: Path):
    doc = tmp_path / "high_star_report.md"
    content = """# System Architecture Blueprint

## 1. System Overview & Topology
[Verified Fact] High performance routing architecture.

```mermaid
graph TD
    Client --> Ingress["Router Dispatch (router.go#L7)"]
```

## 2. Module Responsibilities & Triage
| Module | Layer | Role | Core Engine? |
| :--- | :--- | :--- | :---: |
| `router.go` | Core | `Router.Dispatch` | **Yes (Tier-0)** |
| `config.go` | Config | Configuration | Tier-1 |

## 3. Golden Path Execution
```mermaid
sequenceDiagram
    participant C as "Client"
    participant R as "Router.Dispatch (router.go#L7)"
    C->>R: Dispatch("/api")
    R-->>C: ok
```
- [`router.go#L3-L9`](router.go#L3-L9)

## 4. Invariants & State Machine
- [Verified Fact] Route table immutability is guaranteed by mutex lock.

## 5. Architecture Trade-offs & Failure Modes
- [Verified Fact] Static slice routing trades dynamic mutation for O(1) lookup.
- [Verified Fact] Memory bounds prevent allocation exhaustion.
"""
    doc.write_text(content, encoding="utf-8")

    judge = RubricJudge(mock_codebase)
    report = judge.evaluate(doc, strict=True)

    assert report.total_score >= 90.0
    assert report.hallucination_rate == 0.0
    assert report.grounding_rate == 100.0
    assert report.fluff_free_index >= 90.0
    assert report.grade == "Grade A (High-Star)"
    assert report.passed is True
    assert len(report.violations) == 0


def test_judge_fails_on_hallucinated_file(mock_codebase: Path, tmp_path: Path):
    doc = tmp_path / "hallucinated_report.md"
    content = """# Architecture
Reference to imaginary code: [non_existent/fake.py#L10-L20]
### Trade-offs
Discussion.
"""
    doc.write_text(content, encoding="utf-8")

    judge = RubricJudge(mock_codebase)
    report = judge.evaluate(doc, strict=False)

    assert report.hallucination_rate > 0.0
    assert report.passed is False
    assert any("[Hallucination]" in v for v in report.violations)


def test_judge_strict_mode_gating(mock_codebase: Path, tmp_path: Path):
    # A report with acceptable score but missing strict Grade A criteria
    doc = tmp_path / "mediocre_report.md"
    content = """# Architecture
Reference: [`router.go#L3-L9`]
Some generic description.
### Trade-offs
Basic trade-offs.
"""
    doc.write_text(content, encoding="utf-8")

    judge = RubricJudge(mock_codebase)
    strict_report = judge.evaluate(doc, strict=True)
    assert strict_report.passed is False


def test_evaluate_report_json_format(mock_codebase: Path, tmp_path: Path, capsys):
    doc = tmp_path / "simple_doc.md"
    doc.write_text("# Title\n[`router.go#L3-L9`]\n### Trade-offs\nNone\n", encoding="utf-8")

    report = evaluate_report(mock_codebase, doc, strict=False, format="json")
    captured = capsys.readouterr()
    assert '"repo_name": "judge_repo"' in captured.out
    assert '"total_score":' in captured.out
    assert isinstance(report.total_score, float)
