"""tests.test_benchmark: Comprehensive Test Suite for Multi-Sample Benchmark Harness.

Tests:
- Execution of run_single_benchmark on real-world sample repositories (mem0 & gin)
- Metric thresholds enforcement (CCGR >= 95%, HR == 0.0%, EPC >= 90%, FFI >= 90)
- Generation of markdown scorecard report
- Output of structured JSON summary
- Graceful handling of non-existent target paths
"""

import json
from pathlib import Path
import pytest

from benchmarks.run_benchmark import (
    BENCHMARK_TARGETS,
    BenchmarkTarget,
    generate_benchmark_markdown_report,
    main,
    run_single_benchmark,
)


def test_benchmark_mem0_sample():
    mem0_target = next(t for t in BENCHMARK_TARGETS if t.name == "mem0")
    if not mem0_target.repo_path.exists():
        pytest.skip(f"mem0 repository not present at {mem0_target.repo_path}")

    res = run_single_benchmark(mem0_target)
    assert res["status"] == "PASSED"
    assert res["language"] == "Python"

    eval_data = res["evaluation"]
    assert eval_data["grounding_rate"] >= 95.0
    assert eval_data["hallucination_rate"] == 0.0
    assert eval_data["execution_completeness"] >= 90.0
    assert eval_data["fluff_free_index"] >= 90.0
    assert eval_data["total_score"] >= 90.0
    assert eval_data["grade"] == "Grade A (High-Star)"
    assert eval_data["passed"] is True


def test_benchmark_gin_sample():
    gin_target = next(t for t in BENCHMARK_TARGETS if "gin" in t.name)
    if not gin_target.repo_path.exists():
        pytest.skip(f"gin repository not present at {gin_target.repo_path}")

    res = run_single_benchmark(gin_target)
    assert res["status"] == "PASSED"
    assert res["language"] == "Go"

    eval_data = res["evaluation"]
    assert eval_data["grounding_rate"] >= 95.0
    assert eval_data["hallucination_rate"] == 0.0
    assert eval_data["execution_completeness"] >= 90.0
    assert eval_data["fluff_free_index"] >= 90.0
    assert eval_data["total_score"] >= 90.0
    assert eval_data["grade"] == "Grade A (High-Star)"
    assert eval_data["passed"] is True


def test_benchmark_missing_repo_handling(tmp_path: Path):
    ghost_target = BenchmarkTarget(
        name="ghost-repo",
        language="Rust",
        pattern="Actor Engine",
        repo_path=tmp_path / "non_existent_repo_dir",
        study_path=tmp_path / "ARCHITECTURE.md",
        loc_estimate="~10k LOC"
    )
    res = run_single_benchmark(ghost_target)
    assert res["status"] == "SKIPPED_MISSING_REPO"


def test_benchmark_markdown_report_generation():
    mock_results = [
        {
            "name": "mem0",
            "language": "Python",
            "pattern": "Microkernel",
            "loc_estimate": "~25,000 LOC",
            "total_files": 1200,
            "internal_edges": 41,
            "evaluation": {
                "grounding_rate": 100.0,
                "hallucination_rate": 0.0,
                "execution_completeness": 100.0,
                "fluff_free_index": 100.0,
                "total_score": 100.0,
                "grade": "Grade A (High-Star)",
                "dimension_scores": {
                    "D1_Fact_Grounding": 35.0,
                    "D2_Architecture_Tradeoffs": 25.0,
                    "D3_Execution_Flow": 20.0,
                    "D4_Anti_AI_Fluff": 15.0,
                    "D5_Mermaid_Integrity": 5.0
                }
            }
        },
        {
            "name": "gin",
            "language": "Go",
            "pattern": "Radix Engine",
            "loc_estimate": "~24,500 LOC",
            "total_files": 130,
            "internal_edges": 10,
            "evaluation": {
                "grounding_rate": 100.0,
                "hallucination_rate": 0.0,
                "execution_completeness": 100.0,
                "fluff_free_index": 100.0,
                "total_score": 100.0,
                "grade": "Grade A (High-Star)",
                "dimension_scores": {
                    "D1_Fact_Grounding": 35.0,
                    "D2_Architecture_Tradeoffs": 25.0,
                    "D3_Execution_Flow": 20.0,
                    "D4_Anti_AI_Fluff": 15.0,
                    "D5_Mermaid_Integrity": 5.0
                }
            }
        }
    ]
    report_md = generate_benchmark_markdown_report(mock_results)
    assert "# repo-mentor: Multi-Sample Objective Benchmark Report" in report_md
    assert "mem0" in report_md
    assert "gin" in report_md
    assert "100.0%" in report_md
    assert "Grade A (High-Star)" in report_md


def test_benchmark_main_end_to_end():
    exit_code = main()
    assert exit_code == 0

    results_dir = Path(__file__).resolve().parent.parent / "benchmarks" / "results"
    summary_json = results_dir / "benchmark_summary.json"
    report_md = results_dir / "benchmark_report.md"

    assert summary_json.is_file()
    assert report_md.is_file()

    with open(summary_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["all_passed"] is True
    assert len(data["results"]) == 2
