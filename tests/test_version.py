"""版本唯一来源校验：pyproject.toml 是权威，安装元数据与 __version__ 必须一致。"""

import re
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import pytest

import repo_mentor

REPO_ROOT = Path(__file__).resolve().parent.parent


def _pyproject_version() -> str:
    text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    project_section = text.split("[project]", 1)[1].split("\n[", 1)[0]
    m = re.search(r'^version\s*=\s*"([^"]+)"', project_section, re.MULTILINE)
    assert m, "pyproject.toml [project] version not found"
    return m.group(1)


def test_installed_metadata_matches_pyproject():
    try:
        installed = version("repo-mentor")
    except PackageNotFoundError:
        pytest.skip("repo-mentor not installed; run pip install -e . first")
    assert installed == _pyproject_version()
    assert repo_mentor.__version__ == installed
