"""tests.test_scanner: Tests for repository topology and entrypoint scanner."""

import tempfile
from pathlib import Path

from repo_mentor.core.scanner import scan_repo


def test_scan_repo_non_directory_error():
    res = scan_repo("/non/existent/path/for/testing")
    assert "error" in res
    assert "Path is not a directory" in res["error"]


def test_scan_repo_empty_dir():
    with tempfile.TemporaryDirectory() as tmp:
        res = scan_repo(tmp)
        assert res["total_files_scanned"] == 0
        assert res["primary_language"] == "Unknown"
        assert res["detected_ecosystems"] == []
        assert res["entrypoints"] == []


def test_scan_repo_detects_python_project():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "pyproject.toml").write_text("[project]\nname = 'test-pkg'\n")
        (root / "main.py").write_text("print('hello world')\n")
        tests_dir = root / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("def test_ok(): pass\n")

        res = scan_repo(root)
        assert res["primary_language"] == "Python"
        assert "Python" in res["detected_ecosystems"]
        entrypoint_names = [e["name"] for e in res["entrypoints"]]
        assert "main.py" in entrypoint_names
        assert "tests" in res["test_suites"]["test_directories"]
        assert res["test_suites"]["has_colocated_tests"] is True


def test_scan_repo_detects_go_project():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "go.mod").write_text("module github.com/example/sample\n\ngo 1.22\n")
        (root / "sample.go").write_text("package sample\n\nfunc New() {}\n")
        (root / "sample_test.go").write_text("package sample\n\nfunc TestNew(t *testing.T) {}\n")

        res = scan_repo(root)
        assert res["primary_language"] == "Go"
        assert "Go" in res["detected_ecosystems"]
        entrypoint_names = [e["name"] for e in res["entrypoints"]]
        assert "sample.go" in entrypoint_names
        assert res["test_suites"]["has_colocated_tests"] is True
        assert "go test" in res["test_suites"]["frameworks"]


def test_scan_repo_detects_rust_project():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "Cargo.toml").write_text("[package]\nname = 'test-crate'\nversion = '0.1.0'\n")
        src_dir = root / "src"
        src_dir.mkdir()
        (src_dir / "main.rs").write_text("fn main() {}\n")

        res = scan_repo(root)
        assert res["primary_language"] == "Rust"
        assert "Rust" in res["detected_ecosystems"]
        entrypoint_paths = [e["path"] for e in res["entrypoints"]]
        assert "src/main.rs" in entrypoint_paths


def test_scan_repo_detects_agent_frameworks():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "AGENTS.md").write_text("# Agents\n")
        (root / "SKILL.md").write_text("# Skill\n")

        res = scan_repo(root)
        assert "Agent Skills / Codex" in res["agent_frameworks"]
        assert "Antigravity Skill" in res["agent_frameworks"]
