"""tests.test_docs_smoke: every documented CLI example must match the real CLI.

Dogfooding gate: the project sells fact-grounding, so its own docs are audited
against the actual Typer command tree, and the documented workflow is executed
end-to-end against this repository.
"""

import re
import tempfile
from collections.abc import Iterator
from pathlib import Path

from typer.main import get_command
from typer.testing import CliRunner

from repo_mentor.cli import app

REPO_ROOT = Path(__file__).resolve().parent.parent
EXCLUDED_DIRS = {".git", ".pytest_cache", "studies", "examples", "dist", "node_modules", ".venv"}

INVOCATION_RE = re.compile(r"\brepo-mentor\s+([a-z][a-z0-9-]*)")
LONG_FLAG_RE = re.compile(r"(?<![\w-])--([a-z][a-z0-9-]*)")
SHORT_FLAG_RE = re.compile(r"(?<![\w-])-([a-z])(?![\w-])")


def _cli_flags() -> dict[str, set[str]]:
    group = get_command(app)
    flags: dict[str, set[str]] = {}
    for name, cmd in group.commands.items():
        opts: set[str] = set()
        for param in cmd.params:
            opts.update(param.opts)
            opts.update(param.secondary_opts)
        flags[name] = opts
    return flags


def _doc_files() -> Iterator[Path]:
    for path in sorted(REPO_ROOT.rglob("*.md")):
        if EXCLUDED_DIRS.isdisjoint(path.parts):
            yield path


def _code_lines(text: str) -> Iterator[tuple[int, str]]:
    for fence in re.finditer(r"```[^\n]*\n(.*?)```", text, re.DOTALL):
        base = text[: fence.start()].count("\n") + 2
        for offset, line in enumerate(fence.group(1).splitlines()):
            yield base + offset, line
    for span in re.finditer(r"`([^`\n]+)`", text):
        yield text[: span.start()].count("\n") + 1, span.group(1)


def test_documented_commands_and_flags_exist() -> None:
    flags = _cli_flags()
    errors = []
    for doc in _doc_files():
        text = doc.read_text(encoding="utf-8")
        for line_no, line in _code_lines(text):
            match = INVOCATION_RE.search(line)
            if not match:
                continue
            sub = match.group(1)
            rel = doc.relative_to(REPO_ROOT)
            if sub not in flags:
                errors.append(f"{rel}:{line_no}: unknown subcommand '{sub}'")
                continue
            rest = line[match.end() :]
            for flag in LONG_FLAG_RE.findall(rest):
                if f"--{flag}" not in flags[sub]:
                    errors.append(f"{rel}:{line_no}: '{sub}' has no option '--{flag}'")
            for flag in SHORT_FLAG_RE.findall(rest):
                if f"-{flag}" not in flags[sub]:
                    errors.append(f"{rel}:{line_no}: '{sub}' has no option '-{flag}'")
    assert not errors, "Documented CLI examples drifted from the real CLI:\n" + "\n".join(errors)


def test_documented_workflow_runs_end_to_end() -> None:
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmp:
        study = Path(tmp) / "study"
        out_html = Path(tmp) / "whitepaper.html"
        commands = [
            ["scan", str(REPO_ROOT)],
            ["map", str(REPO_ROOT), "--mermaid"],
            ["hotspots", str(REPO_ROOT), "--top", "5"],
            ["ast", str(REPO_ROOT), "repo_mentor", "--calls"],
            ["init", str(study), "--repo", str(REPO_ROOT)],
            ["verify", str(REPO_ROOT), str(study)],
            ["eval", str(REPO_ROOT), str(study), "--format", "json"],
            ["export", str(study), "--out", str(out_html)],
        ]
        for args in commands:
            result = runner.invoke(app, args)
            assert result.exit_code == 0, f"`repo-mentor {' '.join(args)}` failed:\n{result.output}"

        html_text = out_html.read_text(encoding="utf-8")
        assert re.search(r"<script[^>]+src=", html_text) is None
        assert "mermaid.initialize" in html_text
