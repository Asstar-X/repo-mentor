"""tests.test_cli: Tests for unified Typer/Rich CLI interface."""

import json
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from repo_mentor.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "scan" in result.stdout
    assert "map" in result.stdout
    assert "hotspots" in result.stdout
    assert "ast" in result.stdout
    assert "init" in result.stdout
    assert "export" in result.stdout


def test_cli_scan():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "main.py").write_text("print('test')\n")

        # Rich format
        res_rich = runner.invoke(app, ["scan", str(root)])
        assert res_rich.exit_code == 0
        assert "Repository Topology Scan" in res_rich.stdout
        assert "Python" in res_rich.stdout

        # JSON format
        res_json = runner.invoke(app, ["scan", str(root), "--format", "json"])
        assert res_json.exit_code == 0
        data = json.loads(res_json.stdout)
        assert data["primary_language"] == "Python"
        assert data["total_files_scanned"] == 1


def test_cli_map():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "go.mod").write_text("module github.com/test/mod\n\ngo 1.22\n")

        res = runner.invoke(app, ["map", str(root), "--mermaid"])
        assert res.exit_code == 0
        assert "```mermaid" in res.stdout
        assert "github_test_mod" in res.stdout or "github.com/test/mod" in res.stdout


def test_cli_hotspots():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "a.py").write_text("x = 1\n" * 50)

        res = runner.invoke(app, ["hotspots", str(root), "--top", "5"])
        assert res.exit_code == 0
        assert "Architectural Hotspots" in res.stdout or "Static File Gravity" in res.stdout
        assert "a.py" in res.stdout


def test_cli_ast():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "test_mod.py").write_text("""
class Greeter:
    def greet(self):
        print('hello')
""")

        res = runner.invoke(app, ["ast", str(root), "test_mod.py", "--symbols"])
        assert res.exit_code == 0
        assert "Greeter" in res.stdout


def test_cli_init_and_export():
    with tempfile.TemporaryDirectory() as tmp:
        repo_dir = Path(tmp) / "source_repo"
        repo_dir.mkdir()
        (repo_dir / "pyproject.toml").write_text("[project]\nname = 'sample'\n")
        (repo_dir / "sample.py").write_text("def hello(): pass\n")

        study_dir = Path(tmp) / "study_workspace"

        # 1. Init
        init_res = runner.invoke(app, ["init", str(study_dir), "--repo", str(repo_dir)])
        assert init_res.exit_code == 0
        assert (study_dir / "ARCHITECTURE.md").is_file()
        assert (study_dir / "DEBUG_NOTES.md").is_file()

        # 2. Export
        export_out = Path(tmp) / "dist_manual.html"
        exp_res = runner.invoke(app, ["export", str(study_dir), "--out", str(export_out)])
        assert exp_res.exit_code == 0
        assert export_out.is_file()
        assert "<!DOCTYPE html>" in export_out.read_text(encoding="utf-8")


def test_cli_verify_and_eval_placeholders():
    v_res = runner.invoke(app, ["verify"])
    assert v_res.exit_code == 0
    assert "Milestone 4" in v_res.stdout

    e_res = runner.invoke(app, ["eval", ".", "README.md"])
    assert e_res.exit_code == 0
    assert "Milestone 4" in e_res.stdout
