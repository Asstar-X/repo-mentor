"""repo_mentor.core: Core Static Analysis & Topology Engines.

Includes:
- scanner: Multi-language topology & entrypoint detector
- parser: Python AST and multi-language symbol & import parser
- dependency: In-repo module import DAG and Mermaid visualizer
- hotspots: Git churn and architectural gravity analyzer
- coverage: Domain mastery gating and progress calculator
"""

from repo_mentor.core.coverage import (
    calculate_domain_score,
    evaluate_mastery,
    evaluate_study_directory,
)
from repo_mentor.core.dependency import (
    DependencyAnalyzer,
    analyze_dependencies,
    generate_mermaid,
)
from repo_mentor.core.hotspots import get_git_hotspots
from repo_mentor.core.parser import (
    CallInvocation,
    GoSymbolLexer,
    PythonASTExtractor,
    RustSymbolLexer,
    SymbolIndex,
    SymbolLocation,
    TypeScriptSymbolLexer,
)
from repo_mentor.core.scanner import scan_repo

__all__ = [
    "scan_repo",
    "SymbolLocation",
    "CallInvocation",
    "SymbolIndex",
    "PythonASTExtractor",
    "GoSymbolLexer",
    "RustSymbolLexer",
    "TypeScriptSymbolLexer",
    "DependencyAnalyzer",
    "analyze_dependencies",
    "generate_mermaid",
    "get_git_hotspots",
    "calculate_domain_score",
    "evaluate_mastery",
    "evaluate_study_directory",
]
