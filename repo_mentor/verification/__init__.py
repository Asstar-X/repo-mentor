"""repo_mentor.verification: Quality Gating & Anti-AI Verification Engine.

Provides AST-grounded code anchor verification, Mermaid diagram syntax validation & repair,
anti-AI fluff detection, call path continuity verification, and the 100-point rubric judge.
"""

from repo_mentor.verification.anchor_verifier import (
    AnchorItem,
    AnchorVerificationResult,
    audit_markdown_anchors,
    extract_anchors,
    verify_study_anchors,
)
from repo_mentor.verification.mermaid_verifier import (
    MermaidIssue,
    MermaidVerificationResult,
    lint_mermaid_code,
    repair_mermaid_code,
    verify_study_mermaid,
)
from repo_mentor.verification.fluff_detector import (
    FluffAuditResult,
    FluffViolation,
    detect_fluff,
)
from repo_mentor.verification.call_path_verifier import (
    CallHop,
    HopVerificationResult,
    verify_sequence_hops,
)
from repo_mentor.verification.judge import (
    EvaluationReport,
    evaluate_report,
)

__all__ = [
    "AnchorItem",
    "AnchorVerificationResult",
    "extract_anchors",
    "audit_markdown_anchors",
    "verify_study_anchors",
    "MermaidIssue",
    "MermaidVerificationResult",
    "lint_mermaid_code",
    "repair_mermaid_code",
    "verify_study_mermaid",
    "FluffViolation",
    "FluffAuditResult",
    "detect_fluff",
    "CallHop",
    "HopVerificationResult",
    "verify_sequence_hops",
    "EvaluationReport",
    "evaluate_report",
]
