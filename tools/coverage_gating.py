#!/usr/bin/env python3
"""
coverage_gating.py - Domain Coverage Gating & Macro Progress Calculator
Part of repo-mentor skill.

Calculates code mastery progress based on the Domain Coverage Gating model:
Global Progress = Base Score (25%) + sum( S(D_i) * (75% / k) )

Prevents false 100% mastery scores when core functional domains are untouched.
Pure Python 3 standard library.
"""

from typing import Dict, List, Any


def calculate_domain_score(trace_done: bool, core_done: bool, drill_done: bool) -> float:
    """Calculates the mastery score for a single domain (0.0 to 100.0)."""
    score = 0.0
    if trace_done:
        score += 35.0
    if core_done:
        score += 35.0
    if drill_done:
        score += 30.0
    return min(100.0, score)


def evaluate_mastery(
    macro_overview: bool,
    macro_history: bool,
    domains: Dict[str, Dict[str, bool]]
) -> Dict[str, Any]:
    """
    Evaluates global repository mastery.

    :param macro_overview: True if architecture overview and pattern are mapped (15%)
    :param macro_history: True if Git Churn / history evolution are mapped (10%)
    :param domains: Dict of {domain_name: {"trace": bool, "core": bool, "drill": bool}}
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
            "macro_score": base_score,
            "core_domains_count": 0,
            "covered_domains_count": 0,
            "hard_cap": round(base_score, 1),
            "blind_spots": [],
            "domain_scores": {}
        }

    weight_per_domain = 75.0 / k
    domain_scores = {}
    blind_spots = []
    covered_count = 0
    domains_contribution = 0.0

    for name, status in domains.items():
        t = status.get("trace", False)
        c = status.get("core", False)
        d = status.get("drill", False)
        s = calculate_domain_score(t, c, d)
        domain_scores[name] = s

        if s == 100.0:
            covered_count += 1
        elif s == 0.0:
            blind_spots.append(name)

        domains_contribution += s * (weight_per_domain / 100.0)

    global_progress = round(base_score + domains_contribution, 1)

    # Calculate hard cap: if blind spots remain 0%, max possible score is:
    # base_score + (active_domains * 100.0 * weight_per_domain / 100.0)
    untouched_k = len(blind_spots)
    active_k = k - untouched_k
    hard_cap = round(25.0 + (active_k * weight_per_domain), 1)

    return {
        "global_progress": global_progress,
        "macro_score": base_score,
        "core_domains_count": k,
        "covered_domains_count": covered_count,
        "hard_cap": hard_cap,
        "blind_spots": blind_spots,
        "domain_scores": domain_scores
    }
