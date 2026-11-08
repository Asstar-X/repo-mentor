"""tests.test_hotspots: Tests for git churn and architectural hotspot analyzer."""

import tempfile
from pathlib import Path

from repo_mentor.core.hotspots import get_git_hotspots


def test_hotspots_non_directory():
    res = get_git_hotspots("/non/existent/path/for/hotspots")
    assert "error" in res
    assert res["is_git_repo"] is False


def test_hotspots_non_git_fallback():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "file_a.py").write_text("x = 1\n" * 100)
        (root / "file_b.py").write_text("y = 2\n" * 30)

        res = get_git_hotspots(root, top_n=5)
        assert res["is_git_repo"] is False
        assert "Falling back to static size ranking" in res["message"]
        assert len(res["hotspots"]) == 2

        # Sorted by LOC
        first = res["hotspots"][0]
        assert first["path"] == "file_a.py"
        assert first["loc"] == 100
        assert first["hotspot_rank"] == 1


def test_hotspots_ignored_files_filter():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n" * 10)
        (root / "package-lock.json").write_text("{}" * 10)
        (root / "main.py").write_text("print('hello')\n" * 20)

        res = get_git_hotspots(root)
        paths = [h["path"] for h in res["hotspots"]]
        assert "main.py" in paths
        assert "image.png" not in paths
        assert "package-lock.json" not in paths
