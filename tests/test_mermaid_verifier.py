"""tests.test_mermaid_verifier: Comprehensive Test Suite for Mermaid Verifier.

Tests:
- Header detection (graph, sequenceDiagram, stateDiagram, invalid headers)
- Unclosed quotes and unbalanced delimiters
- Flowchart unquoted parentheses
- Sequence diagram unquoted participant aliases
- State diagram :: scope operator collisions
- Reserved keyword collisions (--> end)
- repair_mermaid_code automated transformations
- verify_study_mermaid end-to-end directory verification and repair
"""

from pathlib import Path

from repo_mentor.verification.mermaid_verifier import (
    lint_mermaid_code,
    repair_mermaid_code,
    verify_study_mermaid,
)


def test_lint_valid_mermaid_diagrams():
    # Valid flowchart
    fc = """
    graph TD
        A["Node A"] --> B["Node B (Detailed)"]
        B --> C["Done"]
    """
    assert len(lint_mermaid_code(fc)) == 0

    # Valid sequence diagram
    seq = """
    sequenceDiagram
        participant A as "Client Ingress"
        participant B as "Worker Engine"
        A->>B: executeTask()
        B-->>A: taskResult
    """
    assert len(lint_mermaid_code(seq)) == 0


def test_lint_invalid_headers():
    bad_header = """
    randomDiagram
        A --> B
    """
    issues = lint_mermaid_code(bad_header)
    assert any(i.rule == "invalid_header" for i in issues)

    empty = ""
    issues_empty = lint_mermaid_code(empty)
    assert any(i.rule == "empty_diagram" for i in issues_empty)


def test_lint_unclosed_quotes():
    code = """
    graph TD
        A["Unclosed quote] --> B["Valid"]
    """
    issues = lint_mermaid_code(code)
    assert any(i.rule == "unclosed_quotes" for i in issues)


def test_lint_unquoted_flowchart_parens():
    code = """
    graph TD
        A[Unquoted (with parens)] --> B
    """
    issues = lint_mermaid_code(code)
    assert any(i.rule == "unquoted_flowchart_label" for i in issues)


def test_lint_unquoted_sequence_alias():
    code = """
    sequenceDiagram
        participant A as Unquoted Alias With Spaces
        A->>B: ping
    """
    issues = lint_mermaid_code(code)
    assert any(i.rule == "unquoted_participant_alias" for i in issues)


def test_lint_state_diagram_colons():
    code = """
    stateDiagram-v2
        StateA --> StateB: ns::event_transition
    """
    issues = lint_mermaid_code(code)
    assert any(i.rule == "state_transition_colons" for i in issues)


def test_lint_reserved_keyword_end():
    code = """
    graph TD
        Start --> end
    """
    issues = lint_mermaid_code(code)
    assert any(i.rule == "reserved_node_id" for i in issues)


def test_repair_mermaid_code():
    broken = """
    graph TD
        A[Unquoted (label)] --> B
        B --> end
    """
    repaired = repair_mermaid_code(broken)
    assert 'A["Unquoted (label)"]' in repaired
    assert '_end_node["End"]' in repaired

    # Sequence alias repair
    seq_broken = """
    sequenceDiagram
        participant A as Raw Alias Label
    """
    seq_repaired = repair_mermaid_code(seq_broken)
    assert 'participant A as "Raw Alias Label"' in seq_repaired

    # State diagram :: repair
    state_broken = """
    stateDiagram-v2
        Init --> Active: core::start
    """
    state_repaired = repair_mermaid_code(state_broken)
    assert "core.start" in state_repaired


def test_verify_study_mermaid_and_auto_fix(tmp_path: Path):
    doc = tmp_path / "doc.md"
    content = """# Title
```mermaid
graph TD
    NodeA[Label (with parens)] --> NodeB
```
"""
    doc.write_text(content, encoding="utf-8")

    # Audit without fix
    res1 = verify_study_mermaid(doc, fix=False)
    assert res1["success"] is False
    assert res1["issues_count"] >= 1

    # Audit with fix
    res2 = verify_study_mermaid(doc, fix=True)
    assert res2["fixed_files"] == 1

    # Check file content updated
    updated = doc.read_text(encoding="utf-8")
    assert 'NodeA["Label (with parens)"]' in updated

    # Re-verify should now pass
    res3 = verify_study_mermaid(doc, fix=False)
    assert res3["success"] is True
    assert res3["issues_count"] == 0
