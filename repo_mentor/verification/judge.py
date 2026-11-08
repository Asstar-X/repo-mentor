"""repo_mentor.verification.judge: 100-Point Quantitative Rubric Automated Judge.

Implements the multi-dimensional anti-AI evaluation rubric across:
- D1: Fact Grounding & Authenticity (35 pts)
- D2: Architecture & Trade-offs (25 pts)
- D3: Execution Flow Continuity (20 pts)
- D4: Anti-AI Fluff & Tone Discipline (15 pts)
- D5: Mermaid Syntax Integrity (5 pts)

Produces structured EvaluationReport and enforces gating thresholds.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from repo_mentor.core.parser import SymbolIndex
from repo_mentor.verification.anchor_verifier import audit_markdown_anchors
from repo_mentor.verification.call_path_verifier import verify_sequence_hops
from repo_mentor.verification.fluff_detector import detect_fluff
from repo_mentor.verification.mermaid_verifier import extract_mermaid_blocks, lint_mermaid_code

console = Console()


@dataclass
class EvaluationReport:
    """Quantitative evaluation report produced by the 100-point rubric judge."""
    repo_name: str
    target_file: str
    grounding_rate: float
    hallucination_rate: float
    execution_completeness: float
    fluff_free_index: float
    total_score: float
    passed: bool
    grade: str
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    violations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RubricJudge:
    """100-Point quantitative evaluation judge."""

    def __init__(self, repo_dir: str | Path, symbol_index: Optional[SymbolIndex] = None):
        self.repo_dir = Path(repo_dir).resolve()
        self.symbol_index = symbol_index or SymbolIndex(self.repo_dir)
        if not self.symbol_index.symbols_by_file:
            self.symbol_index.build_index(max_depth=3)

    def evaluate(self, report_markdown_path: str | Path, strict: bool = False) -> EvaluationReport:
        doc_path = Path(report_markdown_path).resolve()
        if not doc_path.exists():
            return EvaluationReport(
                repo_name=self.repo_dir.name,
                target_file=str(doc_path),
                grounding_rate=0.0,
                hallucination_rate=100.0,
                execution_completeness=0.0,
                fluff_free_index=0.0,
                total_score=0.0,
                passed=False,
                grade="Fail (Rejected)",
                violations=[f"Report file or directory not found: {doc_path}"]
            )

        if doc_path.is_dir():
            md_files = sorted(list(doc_path.rglob("*.md")))
            contents = [p.read_text(encoding="utf-8", errors="replace") for p in md_files if not p.name.startswith(".")]
            content = "\n\n".join(contents)
        else:
            content = doc_path.read_text(encoding="utf-8", errors="replace")

        # Companion study context: if trade-offs are not in the single file, check companion DEBUG_NOTES.md in same folder
        companion_content = ""
        if doc_path.is_file() and doc_path.parent.is_dir():
            debug_notes = doc_path.parent / "DEBUG_NOTES.md"
            if debug_notes.is_file() and debug_notes != doc_path:
                try:
                    companion_content = debug_notes.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    pass

        # 1. Audit Anchors & Symbol Grounding (D1)
        if doc_path.is_dir():
            # Aggregate across all markdown files
            all_anchors_count = 0
            all_verified_count = 0
            all_hallucinations = []
            for mf in doc_path.rglob("*.md"):
                if mf.name.startswith("."):
                    continue
                res = audit_markdown_anchors(self.repo_dir, mf, symbol_index=self.symbol_index)
                all_anchors_count += res["total_anchors"]
                all_verified_count += res["verified_count"]
                all_hallucinations.extend(res["hallucinations"])
            ccgr = round((all_verified_count / all_anchors_count * 100.0), 1) if all_anchors_count > 0 else 100.0
            hr = round((len(all_hallucinations) / all_anchors_count * 100.0), 1) if all_anchors_count > 0 else 0.0
            hallucinations = all_hallucinations
            total_anchors_num = all_anchors_count
        else:
            anchor_audit = audit_markdown_anchors(
                self.repo_dir,
                doc_path,
                symbol_index=self.symbol_index
            )
            ccgr = anchor_audit["grounding_rate"]
            hr = anchor_audit["hallucination_rate"]
            hallucinations = anchor_audit["hallucinations"]
            total_anchors_num = anchor_audit["total_anchors"]

        # 2. Audit Anti-AI Fluff & Tone Discipline (D4)
        fluff_audit = detect_fluff(content)
        ffi = fluff_audit.fluff_free_index

        # 3. Audit Mermaid Diagrams & Sequence Hops (D3 & D5)
        mermaid_blocks = extract_mermaid_blocks(content)
        total_diagrams = len(mermaid_blocks)
        valid_diagrams = 0
        epc_scores: List[float] = []

        mermaid_issues = []
        for _, _, code in mermaid_blocks:
            issues = lint_mermaid_code(code)
            if not issues:
                valid_diagrams += 1
            else:
                mermaid_issues.extend(issues)

            if code.strip().lower().startswith("sequencediagram"):
                seq_res = verify_sequence_hops(code, self.symbol_index)
                epc_scores.append(seq_res["epc"])

        overall_epc = (sum(epc_scores) / len(epc_scores)) if epc_scores else 100.0

        # --- Compute Rubric Dimensions ---

        # D1: Fact Grounding & Authenticity (35 pts)
        # Line existence (15 pts), Symbol grounding (15 pts), 0% HR bonus (5 pts)
        d1_score = 0.0
        if total_anchors_num > 0:
            d1_score += (ccgr / 100.0) * 30.0
            if hr == 0.0:
                d1_score += 5.0
            else:
                d1_score = max(0.0, d1_score - (hr * 1.5))
        else:
            # No anchors present in doc
            d1_score = 0.0

        # D2: Architecture & Trade-offs (25 pts)
        # Tier triage (10 pts), Trade-offs / Debt (10 pts), State machine / Invariants (5 pts)
        d2_score = 0.0
        has_tier_triage = bool(re.search(r'Tier-0.*(?:Tier-1|Tier-2)|模块优先级|阅读分流', content, re.DOTALL))
        if has_tier_triage:
            d2_score += 10.0

        # Trade-offs check: in content or companion DEBUG_NOTES.md
        has_tradeoffs = not fluff_audit.missing_tradeoffs
        if not has_tradeoffs and companion_content:
            from repo_mentor.verification.fluff_detector import TRADEOFFS_HEADING_RE
            if TRADEOFFS_HEADING_RE.search(companion_content):
                has_tradeoffs = True
                # Remove missing_tradeoffs violation and restore penalty
                fluff_audit.violations = [v for v in fluff_audit.violations if v.category != "missing_tradeoffs"]
                fluff_audit.missing_tradeoffs = False
                fluff_audit.penalty_score = max(0.0, fluff_audit.penalty_score - 10.0)
                ffi = min(100.0, ffi + 10.0)

        if has_tradeoffs:
            d2_score += 10.0

        has_invariants = bool(re.search(r'不变式|Invariants?|State Machine|状态机|实体心智模型|生命周期', content, re.IGNORECASE))
        if has_invariants:
            d2_score += 5.0

        # D3: Execution Flow Continuity (20 pts)
        # Golden path flow (10 pts), Verified diagram hops (10 pts)
        d3_score = 0.0
        has_golden_path = bool(re.search(r'黄金路径|Golden Path|端到端全景|Call Chain|调用链路', content, re.IGNORECASE))
        if has_golden_path:
            d3_score += 10.0
        d3_score += (overall_epc / 100.0) * 10.0

        # D4: Anti-AI Fluff & Tone Discipline (15 pts)
        # Zero banned buzzwords (5 pts), Zero ungrounded paragraphs (5 pts), Peer objective tone / FFI (5 pts)
        d4_score = 0.0
        b_pts = max(0.0, 5.0 - (fluff_audit.banned_buzzword_count * 2.5))
        u_pts = max(0.0, 5.0 - (fluff_audit.ungrounded_paragraph_count * 2.5))
        f_pts = (ffi / 100.0) * 5.0
        d4_score = b_pts + u_pts + f_pts

        # D5: Mermaid Syntax Integrity (5 pts)
        d5_score = 0.0
        if total_diagrams > 0:
            d5_score = (valid_diagrams / total_diagrams) * 5.0
        else:
            d5_score = 5.0

        # Total Score
        raw_total = d1_score + d2_score + d3_score + d4_score + d5_score
        total_score = round(max(0.0, min(100.0, raw_total)), 1)

        # Grade Determination
        if total_score >= 90.0 and hr == 0.0 and ccgr >= 95.0 and ffi >= 90.0:
            grade = "Grade A (High-Star)"
        elif total_score >= 80.0 and hr == 0.0 and ccgr >= 90.0:
            grade = "Grade B (Acceptable)"
        else:
            grade = "Fail (Rejected)"

        passed = (grade == "Grade A (High-Star)") if strict else (total_score >= 80.0 and hr == 0.0 and ccgr >= 90.0)

        # Violations Aggregation
        violations: List[str] = []
        for h in hallucinations:
            violations.append(f"[Hallucination] {h['file']}:{h['lines']} - {h['error']}")
        for f in fluff_audit.violations:
            violations.append(f"[Anti-AI Fluff] L{f.line_number} {f.category}: {f.explanation}")
        for m in mermaid_issues:
            violations.append(f"[Mermaid Syntax] L{m.line_num} {m.rule}: {m.message}")

        return EvaluationReport(
            repo_name=self.repo_dir.name,
            target_file=str(doc_path),
            grounding_rate=round(ccgr, 1),
            hallucination_rate=round(hr, 1),
            execution_completeness=round(overall_epc, 1),
            fluff_free_index=round(ffi, 1),
            total_score=total_score,
            passed=passed,
            grade=grade,
            dimension_scores={
                "D1_Fact_Grounding": round(d1_score, 1),
                "D2_Architecture_Tradeoffs": round(d2_score, 1),
                "D3_Execution_Flow": round(d3_score, 1),
                "D4_Anti_AI_Fluff": round(d4_score, 1),
                "D5_Mermaid_Integrity": round(d5_score, 1)
            },
            violations=violations
        )


def evaluate_report(
    repo_path: str | Path,
    report_path: str | Path,
    strict: bool = False,
    format: str = "rich"
) -> EvaluationReport:
    """Runs the 100-point rubric judge on a report markdown file."""
    judge = RubricJudge(repo_path)
    report = judge.evaluate(report_path, strict=strict)

    if format == "json":
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        return report

    # Rich Visual Presentation
    status_style = "bold green" if report.passed else "bold red"
    status_label = "PASSED" if report.passed else "FAILED"

    panel_content = (
        f"Target Document: [bold]{report.target_file}[/bold]\n"
        f"Repository: [bold cyan]{report.repo_name}[/bold cyan]\n"
        f"Grade: [bold]{report.grade}[/bold] | Status: [{status_style}]{status_label}[/{status_style}]\n"
        f"Total Score: [bold magenta]{report.total_score} / 100.0[/bold magenta]"
    )
    console.print(Panel(
        panel_content,
        title="[bold green]Milestone 4 Evaluation Judge Report[/bold green]",
        border_style="green" if report.passed else "red"
    ))

    # Metric Scorecard Table
    m_table = Table(title="Core Metrics Scorecard", header_style="bold cyan")
    m_table.add_column("Metric", style="bold")
    m_table.add_column("Value", justify="right")
    m_table.add_column("Benchmark Target", justify="center")
    m_table.add_column("Evaluation", justify="center")

    ccgr_ok = report.grounding_rate >= 95.0
    m_table.add_row(
        "Code Citation Grounding Rate (CCGR)",
        f"{report.grounding_rate}%",
        ">= 95.0%",
        "[green]✓ PASS[/green]" if ccgr_ok else "[yellow]⚠ CHECK[/yellow]"
    )

    hr_ok = report.hallucination_rate == 0.0
    m_table.add_row(
        "Hallucination Rate (HR)",
        f"{report.hallucination_rate}%",
        "== 0.0%",
        "[green]✓ PASS[/green]" if hr_ok else "[red]✗ FAIL[/red]"
    )

    epc_ok = report.execution_completeness >= 90.0
    m_table.add_row(
        "Execution Path Completeness (EPC)",
        f"{report.execution_completeness}%",
        ">= 90.0%",
        "[green]✓ PASS[/green]" if epc_ok else "[yellow]⚠ CHECK[/yellow]"
    )

    ffi_ok = report.fluff_free_index >= 90.0
    m_table.add_row(
        "Fluff-Free Index (FFI)",
        f"{report.fluff_free_index}/100",
        ">= 90.0/100",
        "[green]✓ PASS[/green]" if ffi_ok else "[yellow]⚠ CHECK[/yellow]"
    )

    console.print(m_table)

    # Dimension Breakdown Table
    d_table = Table(title="100-Point Rubric Breakdown", header_style="bold yellow")
    d_table.add_column("Dimension", style="bold")
    d_table.add_column("Max Points", justify="right")
    d_table.add_column("Earned Score", justify="right", style="green")

    d_table.add_row("D1: Fact Grounding & Authenticity", "35.0", str(report.dimension_scores.get("D1_Fact_Grounding", 0.0)))
    d_table.add_row("D2: Architecture & Trade-offs", "25.0", str(report.dimension_scores.get("D2_Architecture_Tradeoffs", 0.0)))
    d_table.add_row("D3: Execution Flow Continuity", "20.0", str(report.dimension_scores.get("D3_Execution_Flow", 0.0)))
    d_table.add_row("D4: Anti-AI Fluff & Tone Discipline", "15.0", str(report.dimension_scores.get("D4_Anti_AI_Fluff", 0.0)))
    d_table.add_row("D5: Mermaid Syntax Integrity", "5.0", str(report.dimension_scores.get("D5_Mermaid_Integrity", 0.0)))
    d_table.add_row("Total Score", "100.0", f"[bold magenta]{report.total_score}[/bold magenta]")

    console.print(d_table)

    if report.violations:
        v_table = Table(title=f"Violations ({len(report.violations)})", header_style="bold red")
        v_table.add_column("#", justify="right")
        v_table.add_column("Violation Detail")
        for idx, v in enumerate(report.violations[:15], start=1):
            v_table.add_row(str(idx), v)
        console.print(v_table)

    return report
