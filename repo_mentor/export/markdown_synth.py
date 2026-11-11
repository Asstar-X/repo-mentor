"""repo_mentor.export.markdown_synth: Structured Markdown Scaffolder & Synthesizer.

Synthesizes standardized study documentation deliverables:
- ARCHITECTURE.md: Topology, module triage matrix, invariants, and sequence diagrams.
- DEBUG_NOTES.md: Local build commands, breakpoint call stacks, core entity models, gotchas, and limit drills.
- STUDY_INDEX.md / README.md: Executive summary, domain breakdown, and progress tracking.
Powers the `repo-mentor init <study_dir> --repo <repo_path>` workflow.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from repo_mentor.core.dependency import analyze_dependencies, generate_mermaid
from repo_mentor.core.hotspots import get_git_hotspots
from repo_mentor.core.scanner import scan_repo


def synthesize_architecture(
    repo_name: str,
    scan_info: dict[str, Any],
    dep_info: dict[str, Any],
    hotspot_info: dict[str, Any],
) -> str:
    """Synthesizes a standardized ARCHITECTURE.md grounded in real scan data."""
    lang = scan_info.get("primary_language", "Unknown")
    total_files = scan_info.get("total_files_scanned", 0)
    mermaid_dag = dep_info.get("mermaid_dag", '```mermaid\ngraph TD\n    Root["Core Module"]\n```')

    entrypoints_str = ""
    for e in scan_info.get("entrypoints", [])[:5]:
        entrypoints_str += f"- `{e['path']}`: {e.get('reason', 'Primary entrypoint')}\n"
    if not entrypoints_str:
        entrypoints_str = "- No dedicated root entrypoints detected; check core library modules.\n"

    hotspots_str = ""
    for h in hotspot_info.get("hotspots", [])[:8]:
        hotspots_str += f"| `{h['path']}` | {h['loc']} | {h['churn']} | {h['revisions']} | {h['hotspot_score']} |\n"
    if not hotspots_str:
        hotspots_str = "| `main` | 0 | 0 | 0 | 0.0 |\n"

    internal_mods = dep_info.get("internal_modules", [])
    triage_str = ""
    for idx, mod in enumerate(internal_mods[:6], 1):
        tier = "Tier-0" if idx <= 2 else "Tier-1"
        triage_str += (
            f"| **Domain {idx}: {mod}** | `{mod}` | {tier} | Core functional subdomain |\n"
        )
    if not triage_str:
        triage_str = (
            "| **Domain 1: Core Engine** | `.` | Tier-0 | Primary business orchestration |\n"
        )

    return f"""# {repo_name} Architecture & System Design Whitepaper

> **Target Repository**: `{repo_name}`
> **Primary Language**: {lang} ({total_files} active files scanned)
> **Architecture Pattern**: Layered Modular Decoupled Architecture
> **Status**: Comprehensive Engineering Documentation

---

## 1. System Positioning & Core Ingress

### 1.1 Architectural Purpose & Boundaries
`{repo_name}` is engineered for high reliability and structured execution.
All core business logic is grounded in physical code abstractions rather than ephemeral wrappers.

### 1.2 Primary System Entrypoints
{entrypoints_str}

---

## 2. Module Boundaries & Dependency Topology

### 2.1 Intra-Repository Dependency DAG
{mermaid_dag}

### 2.2 Module Triage & Domain Allocation
| Domain Name | Root Path | Tier | Architectural Role |
| :--- | :--- | :---: | :--- |
{triage_str}

---

## 3. High-Churn Architectural Hotspots (Code As A Crime Scene)

The following files represent the highest architectural complexity and modification frequency:

| File Path | LOC | Churn (Ins+Del) | Revisions | Hotspot Score |
| :--- | :---: | :---: | :---: | :---: |
{hotspots_str}

---

## 4. System Invariants & Trade-Offs

1. **State Isolation Invariant**: All internal mutations are encapsulated within designated domain boundaries.
2. **Defensive Boundary**: External I/O and protocol deserialization must validate inputs before delegating to the core engine.
"""


def synthesize_debug_notes(repo_name: str, scan_info: dict[str, Any]) -> str:
    """Synthesizes standardized DEBUG_NOTES.md template for walkthroughs and limit drills."""
    lang = scan_info.get("primary_language", "Unknown")
    test_suites = scan_info.get("test_suites", {})
    frameworks = ", ".join(test_suites.get("frameworks", ["standard test runner"]))

    build_cmd = "make test"
    if lang == "Python":
        build_cmd = "pytest tests/ -v"
    elif lang == "Go":
        build_cmd = "go test -v ./..."
    elif lang == "Rust":
        build_cmd = "cargo test"

    return f"""# {repo_name} Source Walkthrough & Debug Journal

> **Repository**: `{repo_name}`
> **Ecosystem**: {lang} ({frameworks})

---

## 1. Local Debugging & Smoke Run Commands

### Build & Test Commands
```bash
# Execute unit and regression test suite
{build_cmd}
```

### Golden Breakpoint Call Stack
```text
1. [Ingress Entrypoint]: Entrypoint parameter validation
2. [Coordinator Dispatch]: State progression and routing
3. [Domain Core Execution]: Load-bearing state machine
4. [Terminal Boundary]: Persistence and response formatting
```

---

## 2. Core Structures & Critical Gotchas

### 1. Core Data Structures
- `CoreContext`: Encapsulates request scope and lifecycle boundaries.
- `StateRecord`: Persisted immutable record tracking domain mutations.

### 2. System Invariants & Subtle Gotchas
1. **Thread Safety / Concurrency Invariant**: Concurrent read/write access must coordinate via designated synchronization primitives.
2. **Error Propagation Invariant**: Errors must bubble with contextual diagnostics rather than being silently caught and suppressed.

---

## 3. Limit Scenario Hypothesis & Drills

### Limit Drill Scenario 1: Crash Recovery & State Consistency (Crash Recovery)
- **Failure Scenario**: Process termination or unhandled panic during state transition.
- **Architectural Focus**: Memory reclamation, persistence boundaries, and transaction recovery.
- **Reference Solution**: Clean resource release via RAII/defer and idempotent transaction recovery.
- **Architectural Verdict**: Core state progress relies on bounded transactions to eliminate residual dirty states.

### Limit Drill Scenario 2: High Concurrency & Resource Exhaustion (Concurrency Limit)
- **Failure Scenario**: Extreme burst concurrency exceeding worker thread/connection limits.
- **Architectural Focus**: Queue saturation, backpressure signaling, and pool pre-allocation.
- **Reference Solution**: Upstream rate limiting and non-blocking admission rejection.
- **Architectural Verdict**: Bounded resource pools protect system availability under peak loads.
"""


def scaffold_study_workspace(
    study_dir: str | Path, repo_dir: str | Path, force: bool = False
) -> dict[str, Any]:
    """Scaffolds an empty study workspace with real scan data from repo_dir."""
    s_path = Path(study_dir).resolve()
    r_path = Path(repo_dir).resolve()

    if not r_path.is_dir():
        raise FileNotFoundError(f"Target repository does not exist: {repo_dir}")

    s_path.mkdir(parents=True, exist_ok=True)
    traces_dir = s_path / "traces"
    traces_dir.mkdir(parents=True, exist_ok=True)

    # 1. Run live scan on target repo
    scan_info = scan_repo(r_path)
    dep_info = analyze_dependencies(r_path)
    dep_info["mermaid_dag"] = generate_mermaid(r_path, internal_only=True)
    hotspot_info = get_git_hotspots(r_path)

    arch_file = s_path / "ARCHITECTURE.md"
    if not arch_file.is_file() or force:
        arch_text = synthesize_architecture(r_path.name, scan_info, dep_info, hotspot_info)
        arch_file.write_text(arch_text, encoding="utf-8")

    debug_file = s_path / "DEBUG_NOTES.md"
    if not debug_file.is_file() or force:
        debug_text = synthesize_debug_notes(r_path.name, scan_info)
        debug_file.write_text(debug_text, encoding="utf-8")

    readme_file = s_path / "README.md"
    if not readme_file.is_file() or force:
        readme_content = f"""# {r_path.name} Code Reading Study Workspace

This directory contains deep architectural study documentation for `{r_path.name}`.
Compiled and maintained via `repo-mentor`.

## Workspace Structure
- `ARCHITECTURE.md`: High-level topology, module triage, and system invariants.
- `DEBUG_NOTES.md`: Local debugging setup, core data structures, gotchas, and limit drills.
- `traces/`: Granular domain execution traces and sequence diagrams.
- `dist/index.html`: Compiled single-file interactive HTML whitepaper.
"""
        readme_file.write_text(readme_content, encoding="utf-8")

    return {
        "study_path": str(s_path),
        "target_repo": str(r_path),
        "created_files": [str(arch_file), str(debug_file), str(readme_file), str(traces_dir)],
    }
