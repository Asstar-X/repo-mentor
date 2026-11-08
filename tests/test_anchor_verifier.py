"""tests.test_anchor_verifier: Comprehensive Test Suite for Anchor Verification Engine.

Tests:
- Anchor extraction regexes across diverse markdown formats
- Physical file existence verification
- Line bound validation and boundary edge cases (zero lines, past EOF, inverted ranges)
- Semantic AST symbol grounding and phantom symbol detection
- ±15 lines drift tolerance
- In-place anchor line auto-repair
"""

import tempfile
from pathlib import Path
import pytest

from repo_mentor.core.parser import SymbolIndex
from repo_mentor.verification.anchor_verifier import (
    AnchorItem,
    AnchorVerifier,
    audit_markdown_anchors,
    extract_anchors,
    verify_study_anchors,
)


@pytest.fixture
def sample_repo(tmp_path: Path) -> Path:
    """Creates a temporary sample code repository with Python and Go source files."""
    repo = tmp_path / "test_repo"
    repo.mkdir()

    # Python source file
    py_code = (
        '"""Sample module docstring."""\n'
        'import os\n'
        '\n'
        'class EngineManager:\n'
        '    """Manages engines."""\n'
        '    def __init__(self, name: str):\n'
        '        self.name = name\n'
        '\n'
        '    def start(self) -> bool:\n'
        '        return True\n'
        '\n'
        'def top_level_helper():\n'
        '    return 42\n'
        '\n'
        '# Extra padding lines to allow testing line drift within file bounds\n'
        'def extra_fn_1(): pass\n'
        'def extra_fn_2(): pass\n'
        'def extra_fn_3(): pass\n'
        'def extra_fn_4(): pass\n'
        'def extra_fn_5(): pass\n'
        'def extra_fn_6(): pass\n'
        'def extra_fn_7(): pass\n'
        'def extra_fn_8(): pass\n'
        'def extra_fn_9(): pass\n'
        'def extra_fn_10(): pass\n'
    )
    (repo / "manager.py").write_text(py_code, encoding="utf-8")

    # Go source file
    go_code = (
        'package sample\n'
        '\n'
        'type Worker struct {\n'
        '    ID int\n'
        '}\n'
        '\n'
        'func (w *Worker) Process() error {\n'
        '    return nil\n'
        '}\n'
    )
    (repo / "worker.go").write_text(go_code, encoding="utf-8")

    return repo


def test_extract_anchors_diverse_patterns():
    md_content = """
    # Analysis Document
    - Reference 1: [manager.py#L4-L10]
    - Reference 2: [`manager.py#L12-L13`](manager.py#L12-L13)
    - Reference 3: `manager.py#L6-L7`
    - Reference 4: `EngineManager`: [`manager.py#L4-L10`]
    - Reference 5: `EngineManager.start`: [manager.py#L9-L10]
    - Table ref: | `worker.go` | [worker.go#L3-L5] |
    - Bracket file: [manager.py]
    ```mermaid
    sequenceDiagram
        participant W as "Worker.Process (worker.go#L7-L9)"
    ```
    """
    anchors = extract_anchors(md_content)
    assert len(anchors) >= 6

    fpaths = {a.file_path for a in anchors}
    assert "manager.py" in fpaths
    assert "worker.go" in fpaths

    # Check claimed symbol extraction
    symbols = {a.claimed_symbol for a in anchors if a.claimed_symbol}
    assert "EngineManager" in symbols or "EngineManager.start" in symbols or "Worker.Process" in symbols


def test_anchor_verifier_valid_symbol_grounding(sample_repo: Path):
    verifier = AnchorVerifier(sample_repo)

    # Valid class anchor
    item = AnchorItem(
        raw_text="[manager.py#L4-L10]",
        file_path="manager.py",
        start_line=4,
        end_line=10,
        claimed_symbol="EngineManager"
    )
    res = verifier.verify_item(item)
    assert res.is_valid is True
    assert res.file_exists is True
    assert res.lines_valid is True
    assert res.symbol_grounded is True
    assert res.category == "ok"


def test_anchor_verifier_phantom_symbol_detection(sample_repo: Path):
    verifier = AnchorVerifier(sample_repo)

    # Claiming a non-existent symbol at lines 4-10
    item = AnchorItem(
        raw_text="[manager.py#L4-L10]",
        file_path="manager.py",
        start_line=4,
        end_line=10,
        claimed_symbol="NonExistentClass"
    )
    res = verifier.verify_item(item)
    assert res.is_valid is False
    assert res.file_exists is True
    assert res.symbol_grounded is False
    assert res.category == "phantom_symbol"
    assert "Claimed symbol 'NonExistentClass' does not span" in res.error_message


def test_anchor_verifier_missing_file_hallucination(sample_repo: Path):
    verifier = AnchorVerifier(sample_repo)

    item = AnchorItem(
        raw_text="[phantom/missing.py#L1-L10]",
        file_path="phantom/missing.py",
        start_line=1,
        end_line=10,
        claimed_symbol="Ghost"
    )
    res = verifier.verify_item(item)
    assert res.is_valid is False
    assert res.file_exists is False
    assert res.category == "missing_file"


def test_anchor_verifier_out_of_bounds_lines(sample_repo: Path):
    verifier = AnchorVerifier(sample_repo)

    # Line 999 is past EOF (manager.py has ~15 lines)
    item = AnchorItem(
        raw_text="[manager.py#L900-L999]",
        file_path="manager.py",
        start_line=900,
        end_line=999
    )
    res = verifier.verify_item(item)
    assert res.is_valid is False
    assert res.lines_valid is False
    assert res.category == "out_of_bounds"

    # Inverted lines: L10-L4
    inverted = AnchorItem(
        raw_text="[manager.py#L10-L4]",
        file_path="manager.py",
        start_line=10,
        end_line=4
    )
    res_inv = verifier.verify_item(inverted)
    assert res_inv.is_valid is False
    assert res_inv.lines_valid is False
    assert res_inv.category == "out_of_bounds"


def test_anchor_verifier_drift_tolerance(sample_repo: Path):
    verifier = AnchorVerifier(sample_repo)

    # Helper function is at line 12. Cited at L14 (within ±15 lines drift)
    drifted_item = AnchorItem(
        raw_text="[manager.py#L14-L15]",
        file_path="manager.py",
        start_line=14,
        end_line=15,
        claimed_symbol="top_level_helper"
    )
    res = verifier.verify_item(drifted_item, drift_tolerance=15)
    assert res.is_valid is True
    assert res.symbol_grounded is True

    # Cited way beyond drift tolerance (line 80)
    beyond_item = AnchorItem(
        raw_text="[manager.py#L80-L85]",
        file_path="manager.py",
        start_line=80,
        end_line=85,
        claimed_symbol="top_level_helper"
    )
    res_beyond = verifier.verify_item(beyond_item, drift_tolerance=5)
    assert res_beyond.is_valid is False


def test_audit_markdown_anchors_end_to_end(sample_repo: Path, tmp_path: Path):
    doc_path = tmp_path / "study_doc.md"
    doc_path.write_text(
        "# Study\n\n"
        "- Grounded class: [`manager.py#L4-L10`]\n"
        "- `top_level_helper`: [manager.py#L12-L13]\n"
        "- Hallucination: [imaginary.py#L1-L5]\n",
        encoding="utf-8"
    )

    audit = audit_markdown_anchors(sample_repo, doc_path)
    assert audit["total_anchors"] == 3
    assert audit["verified_count"] == 2
    assert audit["grounding_rate"] == 66.7
    assert audit["hallucination_rate"] == 33.3
    assert len(audit["hallucinations"]) == 1
    assert audit["hallucinations"][0]["file"] == "imaginary.py"


def test_verify_study_anchors_directory(sample_repo: Path, tmp_path: Path):
    study_dir = tmp_path / "my_study"
    study_dir.mkdir()
    (study_dir / "valid.md").write_text("- Valid: [worker.go#L3-L5]\n", encoding="utf-8")

    summary = verify_study_anchors(sample_repo, study_dir)
    assert summary["success"] is True
    assert summary["grounding_rate"] == 100.0
    assert summary["hallucination_rate"] == 0.0


def test_single_line_anchor_auto_repair(sample_repo: Path, tmp_path: Path):
    doc_path = tmp_path / "study_single_line.md"
    doc_path.write_text(
        "# Study\n\n"
        "- Helper symbol: `top_level_helper`: [manager.py#L12]\n",
        encoding="utf-8"
    )

    audit = audit_markdown_anchors(sample_repo, doc_path, fix=True)
    assert audit["valid"] is True
    assert audit["total_anchors"] == 1

    # Verify that #L12 was successfully repaired in-place to #L12-L13
    repaired_content = doc_path.read_text(encoding="utf-8")
    assert "[manager.py#L12-L13]" in repaired_content
    assert "[manager.py#L12]" not in repaired_content
