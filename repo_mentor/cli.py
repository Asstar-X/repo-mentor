"""repo_mentor.cli: Unified Typer/Rich CLI Entrypoint.

Provides an ergonomic, typed command-line interface:
- scan: Inspect repository structure, language distribution, entrypoints, and test suites.
- map: Extract package topology and render clean Mermaid DAGs.
- hotspots: Analyze Git churn and architectural hotspots.
- ast: Extract symbols, classes, functions, and call invocations.
- init: Initialize a standardized study workspace.
- export: Compile dynamic single-file HTML whitepaper manual.
- verify & eval: Verification and evaluation judge.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from repo_mentor.core.dependency import analyze_dependencies, generate_mermaid
from repo_mentor.core.hotspots import get_git_hotspots
from repo_mentor.core.parser import SymbolIndex
from repo_mentor.core.scanner import scan_repo
from repo_mentor.export.html_compiler import compile_study_html
from repo_mentor.export.markdown_synth import scaffold_study_workspace

app = typer.Typer(
    name="repo-mentor",
    help="Universal Open-Source Codebase Deep-Reading & Architectural Analysis Assistant.",
    add_completion=False,
    no_args_is_help=True
)

console = Console()
err_console = Console(stderr=True)


@app.command()
def scan(
    repo_path: str = typer.Argument(".", help="Path to repository root"),
    depth: int = typer.Option(3, "--depth", "-d", help="Max directory depth to scan"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich or json")
) -> None:
    """Inspect repository topology, language breakdown, entrypoints, and test layout."""
    res = scan_repo(repo_path, max_depth=depth)
    if "error" in res:
        err_console.print(f"[bold red]Error:[/bold red] {res['error']}")
        raise typer.Exit(code=1)

    if format.lower() == "json":
        console.print(json.dumps(res, indent=2, ensure_ascii=False))
        return

    # Rich formatting
    console.print(Panel(
        f"[bold white]{res['root']}[/bold white]\n"
        f"Primary Ecosystem: [bold cyan]{res['primary_language']}[/bold cyan] | "
        f"Total Files: [bold]{res['total_files_scanned']}[/bold]",
        title="[bold green]Repository Topology Scan[/bold green]",
        border_style="green"
    ))

    # Language table
    lang_table = Table(title="Language Distribution", show_header=True, header_style="bold magenta")
    lang_table.add_column("Language", style="cyan")
    lang_table.add_column("Lines of Code (LOC)", justify="right")
    for lang, loc in res.get("language_distribution", {}).items():
        lang_table.add_row(lang, f"{loc:,}")
    console.print(lang_table)

    # Entrypoints
    entries = res.get("entrypoints", [])
    if entries:
        ent_table = Table(title="Detected Primary Entrypoints", show_header=True, header_style="bold yellow")
        ent_table.add_column("Type", style="green")
        ent_table.add_column("File Path", style="bold white")
        ent_table.add_column("Reason / Detection", style="dim")
        for e in entries:
            ent_table.add_row(e.get("type", "entrypoint"), e.get("path", ""), e.get("reason", ""))
        console.print(ent_table)

    # Test Suites
    test_info = res.get("test_suites", {})
    frameworks = ", ".join(test_info.get("frameworks", ["None detected"]))
    console.print(Panel(
        f"Frameworks: [bold]{frameworks}[/bold]\n"
        f"Directories: [dim]{', '.join(test_info.get('test_directories', [])) or 'None'}[/dim]\n"
        f"Co-located Test Files: [bold]{test_info.get('colocated_test_count', 0)}[/bold]",
        title="Test Suites & Layout",
        border_style="blue"
    ))


@app.command()
def map(
    repo_path: str = typer.Argument(".", help="Path to repository root"),
    internal_only: bool = typer.Option(False, "--internal-only", help="Include only internal module dependencies"),
    mermaid: bool = typer.Option(False, "--mermaid", help="Output Mermaid diagram directly"),
    out: Optional[str] = typer.Option(None, "--out", "-o", help="Write Mermaid or JSON output to file")
) -> None:
    """Extract internal package dependency DAG and generate Mermaid diagrams."""
    analysis = analyze_dependencies(repo_path, internal_only=internal_only)
    if "error" in analysis:
        err_console.print(f"[bold red]Error:[/bold red] {analysis['error']}")
        raise typer.Exit(code=1)

    mermaid_str = generate_mermaid(repo_path, internal_only=internal_only)

    if out:
        out_p = Path(out).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        if out_p.suffix.lower() == ".json":
            out_p.write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            out_p.write_text(mermaid_str, encoding="utf-8")
        console.print(f"[bold green]✓[/bold green] Wrote output to: {out_p}")
        return

    if mermaid:
        console.print(mermaid_str)
        return

    # Rich summary
    console.print(Panel(
        f"Root: [bold]{analysis.get('repo_root', '')}[/bold]\n"
        f"Internal Modules Detected: [bold cyan]{len(analysis.get('internal_modules', []))}[/bold cyan]\n"
        f"Internal Edge Relationships: [bold green]{analysis.get('internal_edge_count', 0)}[/bold green]",
        title="[bold green]Package Dependency Topology[/bold green]",
        border_style="green"
    ))

    mod_table = Table(title="Internal Modules & Packages", show_header=True, header_style="bold magenta")
    mod_table.add_column("Module / Sub-package", style="cyan")
    for mod in analysis.get("internal_modules", [])[:15]:
        mod_table.add_row(mod)
    console.print(mod_table)

    console.print("\n[bold]Mermaid DAG Preview:[/bold]")
    syntax = Syntax(mermaid_str, "markdown", theme="monokai", line_numbers=False)
    console.print(syntax)


@app.command()
def hotspots(
    repo_path: str = typer.Argument(".", help="Path to repository root"),
    commits: int = typer.Option(300, "--commits", "-c", help="Number of recent commits to analyze"),
    top: int = typer.Option(15, "--top", "-t", help="Number of top hotspot files to output")
) -> None:
    """Analyze Git churn, revision frequency, and architectural complexity gravity."""
    res = get_git_hotspots(repo_path, max_commits=commits, top_n=top)
    if "error" in res:
        err_console.print(f"[bold red]Error:[/bold red] {res['error']}")
        raise typer.Exit(code=1)

    is_git = res.get("is_git_repo", False)
    header_title = (
        "[bold green]Git Churn & Architectural Hotspots[/bold green]"
        if is_git
        else "[bold yellow]Static File Gravity (Non-Git Fallback)[/bold yellow]"
    )

    console.print(Panel(
        f"Git Repository: [bold]{is_git}[/bold] | Commits Analyzed: [bold]{res.get('commits_analyzed', 0)}[/bold]\n"
        f"Active Tracked Files: [bold]{res.get('total_active_files', 0)}[/bold]",
        title=header_title,
        border_style="green" if is_git else "yellow"
    ))

    table = Table(title=f"Top {top} Architectural Hotspots", show_header=True, header_style="bold cyan")
    table.add_column("Rank", justify="right", style="bold")
    table.add_column("File Path", style="bold white")
    table.add_column("LOC", justify="right", style="dim")
    table.add_column("Churn", justify="right", style="yellow")
    table.add_column("Revisions", justify="right", style="magenta")
    table.add_column("Hotspot Score", justify="right", style="bold red")

    for h in res.get("hotspots", []):
        table.add_row(
            str(h.get("hotspot_rank", "")),
            h.get("path", ""),
            f"{h.get('loc', 0):,}",
            f"{h.get('churn', 0):,}",
            f"{h.get('revisions', 0):,}",
            f"{h.get('hotspot_score', 0.0):,}"
        )
    console.print(table)


@app.command()
def ast(
    repo_path: str = typer.Argument(".", help="Path to repository root"),
    file_or_dir: str = typer.Argument(..., help="File or directory path to parse"),
    symbols: bool = typer.Option(True, "--symbols/--no-symbols", help="Show extracted symbols"),
    calls: bool = typer.Option(False, "--calls", help="Show function call invocations")
) -> None:
    """Extract AST symbols (classes, functions, methods, interfaces) and call graphs."""
    root_p = Path(repo_path).resolve()
    target_p = (root_p / file_or_dir).resolve() if not Path(file_or_dir).is_absolute() else Path(file_or_dir).resolve()

    index = SymbolIndex(root_p)
    if target_p.is_file():
        index.parse_file(target_p)
    elif target_p.is_dir():
        index.build_index(max_depth=3)
    else:
        err_console.print(f"[bold red]Error:[/bold red] Target path does not exist: {target_p}")
        raise typer.Exit(code=1)

    all_symbols = [s for syms in index.symbols_by_file.values() for s in syms]
    all_calls = [c for calls_list in index.calls_by_file.values() for c in calls_list]

    console.print(Panel(
        f"Target: [bold]{target_p}[/bold]\n"
        f"Indexed Files: [bold]{len(index.symbols_by_file)}[/bold] | "
        f"Extracted Symbols: [bold cyan]{len(all_symbols)}[/bold cyan] | "
        f"Call Invocations: [bold green]{len(all_calls)}[/bold green]",
        title="[bold green]AST & Symbol Parser[/bold green]",
        border_style="green"
    ))

    if symbols and all_symbols:
        s_table = Table(title="Extracted Symbols", show_header=True, header_style="bold magenta")
        s_table.add_column("Type", style="green")
        s_table.add_column("Symbol Name", style="bold white")
        s_table.add_column("Lines", justify="right", style="cyan")
        s_table.add_column("Signature", style="dim")
        for sym in all_symbols[:30]:
            s_table.add_row(
                sym.symbol_type,
                sym.symbol_name,
                f"L{sym.start_line}-L{sym.end_line}",
                sym.signature[:60] + ("..." if len(sym.signature) > 60 else "")
            )
        console.print(s_table)

    if calls and all_calls:
        c_table = Table(title="Call Graph Invocations", show_header=True, header_style="bold yellow")
        c_table.add_column("Caller", style="cyan")
        c_table.add_column("Line", justify="right", style="dim")
        c_table.add_column("Callee Invocations", style="bold green")
        for cl in all_calls[:30]:
            c_table.add_row(cl.caller, f"L{cl.line}", cl.callee)
        console.print(c_table)


@app.command()
def init(
    study_dir: str = typer.Argument(..., help="Path to study directory to initialize"),
    repo: str = typer.Option(..., "--repo", "-r", help="Path to target repository to study"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing study files")
) -> None:
    """Initialize a standardized study workspace with live topology and deliverable templates."""
    try:
        res = scaffold_study_workspace(study_dir, repo, force=force)
        console.print(Panel(
            f"Workspace: [bold]{res['study_path']}[/bold]\n"
            f"Target: [bold cyan]{res['target_repo']}[/bold cyan]\n"
            f"Created Scaffolding: [dim]{len(res['created_files'])} assets[/dim]",
            title="[bold green]✓ Study Workspace Initialized[/bold green]",
            border_style="green"
        ))
    except Exception as e:
        err_console.print(f"[bold red]Failed to initialize study workspace:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def export(
    study_dir: str = typer.Argument(..., help="Path to study directory"),
    out: Optional[str] = typer.Option(None, "--out", "-o", help="Output single-file HTML manual path")
) -> None:
    """Compile study assets into an offline, interactive HTML whitepaper manual."""
    try:
        out_path = compile_study_html(study_dir, output_file=out)
        console.print(Panel(
            f"Source Study: [bold]{study_dir}[/bold]\n"
            f"Compiled Whitepaper: [bold green]{out_path}[/bold green]",
            title="[bold green]✓ HTML Whitepaper Exported[/bold green]",
            border_style="green"
        ))
    except Exception as e:
        err_console.print(f"[bold red]Export error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def verify(
    repo_path: str = typer.Argument(".", help="Path to target repository"),
    study_path: str = typer.Argument(".", help="Path to study markdown file or directory"),
    fix: bool = typer.Option(False, "--fix", help="Attempt automated repair"),
    strict: bool = typer.Option(False, "--strict", help="Enforce zero-tolerance gating")
) -> None:
    """Verify semantic code anchors and Mermaid syntax in study notes."""
    try:
        from repo_mentor.verification.anchor_verifier import verify_study_anchors
        from repo_mentor.verification.mermaid_verifier import verify_study_mermaid

        anchor_res = verify_study_anchors(repo_path, study_path, fix=fix)
        mermaid_res = verify_study_mermaid(study_path, fix=fix)

        if mermaid_res.get("issues"):
            m_table = Table(title="Mermaid Syntax Issues", header_style="bold red")
            m_table.add_column("File", style="cyan")
            m_table.add_column("Line", justify="right")
            m_table.add_column("Rule", style="yellow")
            m_table.add_column("Issue")
            for iss in mermaid_res["issues"][:10]:
                m_table.add_row(Path(iss["file"]).name, str(iss["line"]), iss["rule"], iss["message"])
            console.print(m_table)

        if strict and (not anchor_res.get("success", False) or not mermaid_res.get("success", False)):
            err_console.print("[bold red]Strict verification failed: issues detected.[/bold red]")
            raise typer.Exit(code=1)
    except ImportError as e:
        console.print(Panel(
            "[bold yellow]Verification Engine Notice[/bold yellow]\n\n"
            "The semantic anchor verification and Mermaid repair engine is packaged in "
            "[bold cyan]repo_mentor.verification[/bold cyan].\n"
            f"Details: {e}",
            title="Verification Module",
            border_style="yellow"
        ))


@app.command()
def eval(
    repo_path: str = typer.Argument(".", help="Path to target repository"),
    report_path: str = typer.Argument(..., help="Path to report markdown file"),
    strict: bool = typer.Option(False, "--strict", help="Enforce zero-tolerance gating"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich or json")
) -> None:
    """Run 100-Point Rubric Automated Evaluation Judge on study deliverables."""
    try:
        from repo_mentor.verification.judge import evaluate_report
        report = evaluate_report(repo_path, report_path, strict=strict, format=format)
        if strict and not report.passed:
            err_console.print(
                f"[bold red]Evaluation failed under strict gating "
                f"(Score: {report.total_score}/100, Grade: {report.grade}).[/bold red]"
            )
            raise typer.Exit(code=1)
    except ImportError as e:
        console.print(Panel(
            "[bold yellow]Evaluation Judge Notice[/bold yellow]\n\n"
            "The 100-Point Rubric Objective Evaluation Judge is packaged in "
            "[bold cyan]repo_mentor.verification.judge[/bold cyan].\n"
            f"Details: {e}",
            title="Automated Judge Module",
            border_style="yellow"
        ))


if __name__ == "__main__":
    app()
