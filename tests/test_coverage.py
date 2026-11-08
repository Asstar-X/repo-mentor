"""tests.test_coverage: Tests for domain mastery scoring and gating."""

import tempfile
from pathlib import Path

from repo_mentor.core.coverage import (
    calculate_domain_score,
    evaluate_mastery,
    evaluate_study_directory,
)


def test_calculate_domain_score():
    assert calculate_domain_score(False, False, False) == 0.0
    assert calculate_domain_score(True, False, False) == 35.0
    assert calculate_domain_score(True, True, False) == 70.0
    assert calculate_domain_score(True, True, True) == 100.0


def test_evaluate_mastery_macro_base():
    # Only macro completed, no domains
    res = evaluate_mastery(True, True, {})
    assert res["global_progress"] == 25.0
    assert res["macro_score"] == 25.0
    assert res["hard_cap"] == 25.0


def test_evaluate_mastery_balanced():
    # 2 domains, each 100%
    domains = {
        "Domain 1": {"trace": True, "core": True, "drill": True},
        "Domain 2": {"trace": True, "core": True, "drill": True}
    }
    res = evaluate_mastery(True, True, domains)
    assert res["global_progress"] == 100.0
    assert res["covered_domains_count"] == 2
    assert res["blind_spots"] == []
    assert res["is_gated"] is False


def test_evaluate_mastery_tier0_gating():
    # Domain 1 is Tier-0 and completely untouched (0%)
    domains = {
        "Core Router": {"trace": False, "core": False, "drill": False, "tier": "Tier-0"},
        "Helper Utils": {"trace": True, "core": True, "drill": True, "tier": "Tier-1"}
    }
    res = evaluate_mastery(True, True, domains)
    # 25 (macro) + 0 + 37.5 (Helper) = 62.5 raw, but Tier-0 is untouched
    assert res["is_gated"] is True
    assert "Core Router" in res["tier0_blind_spots"]
    assert res["global_progress"] <= 60.0


def test_evaluate_study_directory():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "ARCHITECTURE.md").write_text("# Architecture Overview\n" + "x" * 400)
        (root / "DEBUG_NOTES.md").write_text("# Debug Notes\n" + "y" * 400)
        traces = root / "traces"
        traces.mkdir()
        (traces / "domain_a.md").write_text("# Domain A\n## Trace Call Chain\n" + "z" * 300)

        res = evaluate_study_directory(root)
        assert res["macro_score"] == 25.0
        assert res["core_domains_count"] == 1
        assert "Domain A" in res["domain_scores"]
