"""tests.test_dependency: Tests for internal package dependency DAG and Mermaid generation."""

import tempfile
from pathlib import Path

from repo_mentor.core.dependency import (
    DependencyAnalyzer,
    analyze_dependencies,
    generate_mermaid,
)


def test_go_internal_edges_detection():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "go.mod").write_text("module github.com/gin-gonic/gin\n\ngo 1.22\n")

        # Root file importing internal sub-package
        (root / "gin.go").write_text("""
package gin

import (
    "github.com/gin-gonic/gin/render"
    "github.com/gin-gonic/gin/binding"
)
""")
        # Sub-package directory
        render_dir = root / "render"
        render_dir.mkdir()
        (render_dir / "render.go").write_text("package render\n")

        binding_dir = root / "binding"
        binding_dir.mkdir()
        (binding_dir / "binding.go").write_text("package binding\n")

        analysis = analyze_dependencies(root, internal_only=True)
        internal_mods = analysis["internal_modules"]
        assert "render" in internal_mods
        assert "binding" in internal_mods
        assert analysis["internal_edge_count"] >= 2

        mermaid_str = generate_mermaid(root, internal_only=True)
        assert "```mermaid" in mermaid_str
        assert "subgraph Internal" in mermaid_str
        assert "render" in mermaid_str
        assert "==>|internal|" in mermaid_str


def test_python_internal_package_edges():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "pyproject.toml").write_text("[project]\nname = 'mem0'\n")

        pkg_dir = root / "mem0"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        mem_dir = pkg_dir / "memory"
        mem_dir.mkdir()
        (mem_dir / "__init__.py").write_text("")
        (mem_dir / "main.py").write_text("""
from mem0.vector_stores.base import VectorStoreBase
from mem0.configs.base import MemoryConfig
""")

        vs_dir = pkg_dir / "vector_stores"
        vs_dir.mkdir()
        (vs_dir / "__init__.py").write_text("")
        (vs_dir / "base.py").write_text("class VectorStoreBase: pass\n")

        cfg_dir = pkg_dir / "configs"
        cfg_dir.mkdir()
        (cfg_dir / "__init__.py").write_text("")
        (cfg_dir / "base.py").write_text("class MemoryConfig: pass\n")

        analysis = analyze_dependencies(root, internal_only=True)
        internal_mods = analysis["internal_modules"]
        assert "mem0.memory" in internal_mods
        assert "mem0.vector_stores" in internal_mods
        assert "mem0.configs" in internal_mods
        assert analysis["internal_edge_count"] >= 2


def test_cargo_toml_parsing():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "Cargo.toml").write_text("""
[package]
name = "core_engine"
version = "0.1.0"

[dependencies]
serde = "1.0"
tokio = { version = "1.0", features = ["full"] }
""")
        analyzer = DependencyAnalyzer(root)
        analysis = analyzer.analyze()
        assert analysis["manifest_count"] == 1
        manifest = analysis["manifests"][0]
        assert manifest["module"] == "core_engine"
        assert "serde" in manifest["dependencies"]
        assert "tokio" in manifest["dependencies"]


def test_mermaid_generation_no_modules():
    with tempfile.TemporaryDirectory() as tmp:
        mermaid_str = generate_mermaid(tmp)
        assert "```mermaid" in mermaid_str
        assert "graph TD" in mermaid_str
