"""repo_mentor.core.coverage: Domain Mastery Gating & Macro Progress Calculator.

Implements the Domain Coverage Gating model:
    Global Progress = Macro Base (25%) + sum(S(Di) * 75% / k)
where:
    Macro Base = 15% (Architecture Overview) + 10% (Git Churn & Archaeology)
    S(Di) = 35% (Trace) + 35% (Core Invariants) + 30% (Limit Drill)

Enforces strict blind-spot progress caps when Tier-0 domains are untouched (0%),
preventing hallucinated claims of comprehensive mastery.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


def calculate_domain_score(trace_done: bool, core_done: bool, drill_done: bool) -> float:
    """Calculates mastery score for a single domain (0.0 to 100.0)."""
    score = 0.0
    if trace_done:
        score += 35.0
    if core_done:
        score += 35.0
    if drill_done:
        score += 30.0
    return min(100.0, round(score, 1))


def evaluate_mastery(
    macro_overview: bool,
    macro_history: bool,
    domains: Dict[str, Dict[str, Any]],
    tier0_domains: Optional[Set[str]] = None
) -> Dict[str, Any]:
    """
    Evaluates global repository mastery and enforces blind-spot caps.

    :param macro_overview: True if architecture overview and topology are mapped (15%)
    :param macro_history: True if Git Churn / history evolution are mapped (10%)
    :param domains: Dict of {domain_name: {"trace": bool, "core": bool, "drill": bool, "tier": Optional[str]}}
    :param tier0_domains: Explicit set of domain names classified as Tier-0 (critical path)
    :return: Dict containing global progress, hard cap, blind spots, and domain breakdown.
    """
    base_score = 0.0
    if macro_overview:
        base_score += 15.0
    if macro_history:
        base_score += 10.0

    k = len(domains)
    if k == 0:
        return {
            "global_progress": round(base_score, 1),
            "macro_score": round(base_score, 1),
            "core_domains_count": 0,
            "covered_domains_count": 0,
            "hard_cap": round(base_score, 1),
            "tier0_blind_spots": [],
            "blind_spots": [],
            "domain_scores": {},
            "is_gated": False
        }

    weight_per_domain = 75.0 / k
    domain_scores: Dict[str, float] = {}
    blind_spots: List[str] = []
    tier0_blind_spots: List[str] = []
    covered_count = 0
    domains_contribution = 0.0

    # Auto-detect Tier-0 if specified in domain dict or tier0_domains param
    effective_tier0 = set(tier0_domains) if tier0_domains else set()
    for name, status in domains.items():
        if status.get("tier") == "Tier-0" or status.get("tier0", False):
            effective_tier0.add(name)

    for name, status in domains.items():
        t = bool(status.get("trace", False))
        c = bool(status.get("core", False))
        d = bool(status.get("drill", False))
        s = calculate_domain_score(t, c, d)
        domain_scores[name] = s

        if s == 100.0:
            covered_count += 1
        elif s == 0.0:
            blind_spots.append(name)
            if name in effective_tier0:
                tier0_blind_spots.append(name)

        domains_contribution += s * (weight_per_domain / 100.0)

    raw_progress = base_score + domains_contribution

    # Calculate hard cap:
    # If any Tier-0 domain is completely unvisited (0%), progress is capped at active domain maximum
    untouched_k = len(blind_spots)
    active_k = k - untouched_k
    hard_cap = round(25.0 + (active_k * weight_per_domain), 1)

    is_gated = False
    gating_reason = ""
    if tier0_blind_spots:
        is_gated = True
        gating_reason = f"Tier-0 core domains untouched: {', '.join(tier0_blind_spots)}"
        # Cap cannot exceed hard_cap or 60.0 when Tier-0 domains are untouched
        tier0_cap = min(hard_cap, 60.0)
        global_progress = min(raw_progress, tier0_cap)
    else:
        global_progress = min(raw_progress, hard_cap)

    return {
        "global_progress": round(global_progress, 1),
        "raw_progress": round(raw_progress, 1),
        "macro_score": round(base_score, 1),
        "core_domains_count": k,
        "covered_domains_count": covered_count,
        "hard_cap": hard_cap,
        "is_gated": is_gated,
        "gating_reason": gating_reason,
        "tier0_blind_spots": tier0_blind_spots,
        "blind_spots": blind_spots,
        "domain_scores": domain_scores
    }


def evaluate_study_directory(study_dir: str | Path) -> Dict[str, Any]:
    """Inspects a study workspace directory and computes live mastery score."""
    study_path = Path(study_dir).resolve()
    if not study_path.is_dir():
        return {"error": f"Study directory does not exist: {study_dir}"}

    # 1. Macro Overview check
    arch_md = study_path / "ARCHITECTURE.md"
    macro_overview = False
    if arch_md.is_file():
        text = arch_md.read_text(encoding="utf-8", errors="replace")
        if len(text.strip()) > 100:
            macro_overview = True

    # 2. Macro History check
    debug_md = study_path / "DEBUG_NOTES.md"
    macro_history = False
    if debug_md.is_file():
        text = debug_md.read_text(encoding="utf-8", errors="replace")
        if len(text.strip()) > 100:
            macro_history = True

    # 3. Domains check from traces directory
    traces_dir = study_path / "traces"
    domains: Dict[str, Dict[str, Any]] = {}
    if traces_dir.is_dir():
        for f in traces_dir.glob("*.md"):
            content = f.read_text(encoding="utf-8", errors="replace")
            # Extract domain name
            d_name = f.stem.replace("_", " ").title()
            title_m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if title_m:
                d_name = title_m.group(1).strip()

            has_trace = bool(re.search(r"##.*(?:Trace|Walkthrough|调用链|执行流)", content, re.I))
            has_core = bool(re.search(r"##.*(?:Core|Invariant|Gotcha|核心结构|不变式)", content, re.I))
            has_drill = bool(re.search(r"##.*(?:Drill|Limit|Failure|极限|攻防)", content, re.I))

            # If the trace file has solid content
            if len(content.strip()) > 200:
                has_trace = True

            domains[d_name] = {
                "trace": has_trace,
                "core": has_core,
                "drill": has_drill
            }

    # Also check if debug_notes has limit drills
    if debug_md.is_file():
        debug_content = debug_md.read_text(encoding="utf-8", errors="replace")
        if re.search(r"##.*(?:Limit Drill|Failure|Scenario|极限场景)", debug_content, re.I):
            for d in domains.values():
                d["drill"] = True

    return evaluate_mastery(macro_overview, macro_history, domains)
