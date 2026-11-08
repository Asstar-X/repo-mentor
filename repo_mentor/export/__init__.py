"""repo_mentor.export: Export & Whitepaper Synthesis Engines.

Includes:
- html_compiler: Dynamic single-file HTML whitepaper compiler
- markdown_synth: Structured Markdown scaffolder and deliverable synthesizer
"""

from repo_mentor.export.html_compiler import compile_study_html
from repo_mentor.export.markdown_synth import (
    scaffold_study_workspace,
    synthesize_architecture,
    synthesize_debug_notes,
)

__all__ = [
    "compile_study_html",
    "scaffold_study_workspace",
    "synthesize_architecture",
    "synthesize_debug_notes",
]
