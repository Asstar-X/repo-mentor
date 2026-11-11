"""tests.test_adversarial_challenger_2: Adversarial Stress Tests for Multi-Language AST & CLI Edge Cases.

Empirical verification suite designed by Challenger 2 (Multi-Language & CLI Edge-Case Challenger).
Stress-tests:
1. Multi-Language AST & Symbol Parsing:
   - Complex Python class hierarchies, async functions, decorators, call graphs
   - Go structs, interfaces, pointer/value receiver methods, package imports
   - Rust structs, enums, traits, functions, and use imports
   - TypeScript/JavaScript classes, interfaces, methods, functions
   - Resilient error recovery: SyntaxError in source code, empty files, comments only
2. Internal Package Dependency DAG:
   - Go intra-repo internal package imports mapping (render, binding, internal/fs)
   - Python multi-package intra-repo import graph
   - Non-package repositories and empty module graph handling
3. CLI Edge Cases & Crash Resistance:
   - Non-git directory fallback for hotspots and scan
   - Empty directory and unrecognized file extensions (.xyz, .bin)
   - Nonexistent paths handling with non-zero exit codes and clean error messages
   - Strict mode exit code gating for verify and eval
4. Dynamic HTML Whitepaper Export Integrity:
   - Export verification on live study repositories
   - Zero hardcoded DeepInfer / canned fallback strings
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from repo_mentor.cli import app
from repo_mentor.core.dependency import DependencyAnalyzer
from repo_mentor.core.parser import (
    SymbolIndex,
)
from repo_mentor.export.html_compiler import compile_study_html

runner = CliRunner()


class TestMultiLanguageAST:
    """Empirical stress-testing of AST parsers across languages."""

    def test_python_complex_constructs_and_calls(self, tmp_path: Path):
        code = '''
from typing import Generic, TypeVar, Optional, Dict, Any
import asyncio

T = TypeVar("T")

class BaseWorker(Generic[T]):
    """Base generic worker."""
    def __init__(self, name: str):
        self.name = name

    def compute(self, val: T) -> T:
        return val

class SpecialWorker(BaseWorker[str]):
    @classmethod
    def spawn(cls) -> "SpecialWorker":
        return cls("spawned")

    @property
    def identity(self) -> str:
        return self.name

    async def async_dispatch(self, payload: Dict[str, Any]) -> bool:
        """Async execution flow."""
        await asyncio.sleep(0.01)
        self.compute("test")
        return True

    class NestedState:
        def step(self):
            return 1
'''
        py_file = tmp_path / "worker.py"
        py_file.write_text(code, encoding="utf-8")

        index = SymbolIndex(tmp_path)
        assert index.parse_file(py_file) is True

        norm = index._normalize_path(py_file.resolve())
        syms = index.symbols_by_file[norm]
        calls = index.calls_by_file[norm]
        sym_names = {s.symbol_name for s in syms}

        # Check classes and methods
        assert "BaseWorker" in sym_names
        assert "SpecialWorker" in sym_names
        assert "SpecialWorker.async_dispatch" in sym_names
        assert "SpecialWorker.spawn" in sym_names
        assert "NestedState" in sym_names or "SpecialWorker.NestedState" in sym_names

        # Check async method metadata
        async_method = next(s for s in syms if s.symbol_name == "async_dispatch")
        assert async_method.symbol_type == "method"
        assert async_method.parent_symbol == "SpecialWorker"

        # Check extracted calls
        callees = [c.callee for c in calls]
        assert "asyncio.sleep" in callees
        assert "self.compute" in callees

    def test_python_syntax_error_resilience(self, tmp_path: Path):
        corrupted_file = tmp_path / "corrupted.py"
        corrupted_file.write_text("class Unfinished(:\n  def foo(:\n", encoding="utf-8")

        index = SymbolIndex(tmp_path)
        # Should gracefully return False without raising an uncaught exception
        parsed = index.parse_file(corrupted_file)
        assert parsed is False
        norm = index._normalize_path(corrupted_file.resolve())
        assert index.symbols_by_file[norm] == []

    def test_python_empty_and_comments_only(self, tmp_path: Path):
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("", encoding="utf-8")
        comments_file = tmp_path / "comments.py"
        comments_file.write_text("# Line 1\n# Line 2\n", encoding="utf-8")

        index = SymbolIndex(tmp_path)
        assert index.parse_file(empty_file) is True
        assert index.parse_file(comments_file) is True

    def test_go_symbols_and_imports(self, tmp_path: Path):
        go_code = """
package server

import (
    "context"
    "fmt"
    "github.com/gin-gonic/gin/binding"
    "github.com/gin-gonic/gin/render"
    myfs "github.com/gin-gonic/gin/internal/fs"
)

type Engine struct {
    port int
}

type IRouter interface {
    Handle(path string) error
}

func (e *Engine) ServeHTTP(ctx context.Context) error {
    return nil
}

func NewEngine() *Engine {
    return &Engine{port: 8080}
}
"""
        go_file = tmp_path / "server.go"
        go_file.write_text(go_code, encoding="utf-8")

        index = SymbolIndex(tmp_path)
        assert index.parse_file(go_file) is True

        norm = index._normalize_path(go_file.resolve())
        syms = index.symbols_by_file[norm]
        imps = index.imports_by_file[norm]
        sym_names = {s.symbol_name for s in syms}

        assert "Engine" in sym_names
        assert "IRouter" in sym_names
        assert "ServeHTTP" in sym_names
        assert "Engine.ServeHTTP" in sym_names
        assert "NewEngine" in sym_names

        assert "github.com/gin-gonic/gin/binding" in imps
        assert "github.com/gin-gonic/gin/render" in imps
        assert "github.com/gin-gonic/gin/internal/fs" in imps

    def test_rust_symbols_and_imports(self, tmp_path: Path):
        rs_code = """
use std::collections::HashMap;
use tokio::sync::Mutex;

pub struct ConfigPool {
    size: usize,
}

pub enum PoolStatus {
    Ready,
    Draining,
}

pub trait PoolManager {
    fn acquire(&self) -> bool;
}

impl ConfigPool {
    pub fn new(size: usize) -> Self {
        ConfigPool { size }
    }
}

pub fn create_default_pool() -> ConfigPool {
    ConfigPool::new(10)
}
"""
        rs_file = tmp_path / "pool.rs"
        rs_file.write_text(rs_code, encoding="utf-8")

        index = SymbolIndex(tmp_path)
        assert index.parse_file(rs_file) is True

        norm = index._normalize_path(rs_file.resolve())
        syms = index.symbols_by_file[norm]
        imps = index.imports_by_file[norm]
        sym_names = {s.symbol_name for s in syms}

        assert "ConfigPool" in sym_names
        assert "PoolStatus" in sym_names
        assert "PoolManager" in sym_names
        assert "new" in sym_names
        assert "create_default_pool" in sym_names
        assert "std::collections::HashMap" in imps

    def test_typescript_symbols_and_imports(self, tmp_path: Path):
        ts_code = """
import { EventEmitter } from "events";
import * as path from "path";

export interface IService {
    start(): Promise<void>;
}

export type Handler = (req: any) => Promise<void>;

export class GatewayService implements IService {
    async start(): Promise<void> {
        console.log("Started");
    }

    private dispatchEvent(evt: string): void {}
}

export function createGateway(): GatewayService {
    return new GatewayService();
}
"""
        ts_file = tmp_path / "gateway.ts"
        ts_file.write_text(ts_code, encoding="utf-8")

        index = SymbolIndex(tmp_path)
        assert index.parse_file(ts_file) is True

        norm = index._normalize_path(ts_file.resolve())
        syms = index.symbols_by_file[norm]
        imps = index.imports_by_file[norm]
        sym_names = {s.symbol_name for s in syms}

        assert "IService" in sym_names
        assert "GatewayService" in sym_names
        assert "createGateway" in sym_names
        assert "Handler" in sym_names
        assert "events" in imps
        assert "path" in imps


class TestDependencyDAG:
    """Stress-testing intra-repo dependency analysis."""

    def test_go_internal_package_mapping(self, tmp_path: Path):
        (tmp_path / "go.mod").write_text(
            "module github.com/sample/app\n\ngo 1.22\n", encoding="utf-8"
        )

        render_dir = tmp_path / "render"
        render_dir.mkdir()
        (render_dir / "render.go").write_text(
            "package render\ntype Renderer struct{}\n", encoding="utf-8"
        )

        binding_dir = tmp_path / "binding"
        binding_dir.mkdir()
        (binding_dir / "binding.go").write_text(
            "package binding\ntype Binder struct{}\n", encoding="utf-8"
        )

        fs_dir = tmp_path / "internal" / "fs"
        fs_dir.mkdir(parents=True)
        (fs_dir / "fs.go").write_text(
            'package fs\nimport "github.com/sample/app/render"\nvar _ = render.Renderer{}\n',
            encoding="utf-8",
        )

        server_dir = tmp_path / "server"
        server_dir.mkdir()
        (server_dir / "server.go").write_text(
            'package server\nimport (\n\t"github.com/sample/app/binding"\n\t"github.com/sample/app/internal/fs"\n)\n',
            encoding="utf-8",
        )

        analyzer = DependencyAnalyzer(tmp_path)
        res = analyzer.analyze(internal_only=True)
        internal_modules = res["internal_modules"]
        edges = res["edges"]

        assert "render" in internal_modules
        assert "binding" in internal_modules
        assert "internal/fs" in internal_modules
        assert "server" in internal_modules
        assert len(edges) >= 3

    def test_python_internal_package_mapping(self, tmp_path: Path):
        pkg_dir = tmp_path / "mypkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

        mem_dir = pkg_dir / "memory"
        mem_dir.mkdir()
        (mem_dir / "__init__.py").write_text("", encoding="utf-8")
        (mem_dir / "main.py").write_text(
            "from mypkg.configs import Config\nfrom mypkg.storage import Store\n", encoding="utf-8"
        )

        cfg_dir = pkg_dir / "configs"
        cfg_dir.mkdir()
        (cfg_dir / "__init__.py").write_text("", encoding="utf-8")
        (cfg_dir / "settings.py").write_text("class Config: pass\n", encoding="utf-8")

        storage_dir = pkg_dir / "storage"
        storage_dir.mkdir()
        (storage_dir / "__init__.py").write_text("", encoding="utf-8")
        (storage_dir / "db.py").write_text("class Store: pass\n", encoding="utf-8")

        analyzer = DependencyAnalyzer(tmp_path)
        res = analyzer.analyze(internal_only=True)
        internal_modules = res["internal_modules"]
        edges = res["edges"]

        assert "mypkg.memory" in internal_modules
        assert "mypkg.configs" in internal_modules
        assert "mypkg.storage" in internal_modules
        assert len(edges) >= 2

    def test_empty_repo_dependency_dag(self, tmp_path: Path):
        analyzer = DependencyAnalyzer(tmp_path)
        res = analyzer.analyze(internal_only=True)
        assert res["internal_modules"] == []
        assert res["edges"] == []
        mermaid = analyzer.generate_mermaid_dag(res)
        assert "No package manifests or internal modules detected" in mermaid


class TestCLIEdgeCases:
    """Adversarial stress-testing of CLI commands and crash resistance."""

    def test_non_git_directory_fallback(self, tmp_path: Path):
        # Scan on non-git dir
        res_scan = runner.invoke(app, ["scan", str(tmp_path)])
        assert res_scan.exit_code == 0
        assert "Primary Ecosystem: Unknown" in res_scan.output

        # Hotspots on non-git dir
        res_hotspots = runner.invoke(app, ["hotspots", str(tmp_path)])
        assert res_hotspots.exit_code == 0
        assert "Static File Gravity (Non-Git Fallback)" in res_hotspots.output

    def test_empty_and_unrecognized_file_types(self, tmp_path: Path):
        (tmp_path / "data.xyz").write_text("random binary/text", encoding="utf-8")
        (tmp_path / "firmware.bin").write_bytes(b"\x00\x01\x02\x03\xff")

        res_scan = runner.invoke(app, ["scan", str(tmp_path)])
        assert res_scan.exit_code == 0
        assert "Total Files: 2" in res_scan.output

        res_ast = runner.invoke(app, ["ast", str(tmp_path), "data.xyz"])
        assert res_ast.exit_code == 0
        assert "Indexed Files: 0" in res_ast.output

    def test_invalid_cli_options_exit_code(self):
        res = runner.invoke(app, ["scan", "--completely-invalid-flag"])
        assert res.exit_code != 0
        assert "No such option" in res.output

    def test_nonexistent_paths_exit_gracefully(self):
        nonexistent = "/path/definitely/does/not/exist"

        res_scan = runner.invoke(app, ["scan", nonexistent])
        assert res_scan.exit_code == 1
        assert "Error: Path is not a directory" in res_scan.output
        assert "Traceback" not in res_scan.output

        res_ast = runner.invoke(app, ["ast", ".", nonexistent])
        assert res_ast.exit_code == 1
        assert "Error: Target path does not exist" in res_ast.output
        assert "Traceback" not in res_ast.output

        res_init = runner.invoke(app, ["init", "/tmp/study", "--repo", nonexistent])
        assert res_init.exit_code == 1
        assert "Failed to initialize study workspace" in res_init.output
        assert "Traceback" not in res_init.output

        res_export = runner.invoke(app, ["export", nonexistent])
        assert res_export.exit_code == 1
        assert "Export error" in res_export.output
        assert "Traceback" not in res_export.output

    def test_strict_mode_gating_exit_codes(self):
        res_verify = runner.invoke(app, ["verify", "/nonexistent", "/nonexistent", "--strict"])
        assert res_verify.exit_code == 1
        assert "Strict verification failed" in res_verify.output

        res_eval = runner.invoke(app, ["eval", "/nonexistent", "/nonexistent.md", "--strict"])
        assert res_eval.exit_code == 1
        assert "Evaluation failed under strict gating" in res_eval.output


class TestDynamicHTMLExportIntegrity:
    """Verifies that HTML export is dynamic and completely free of hardcoded DeepInfer strings."""

    def test_export_cleanliness_synthetic(self, tmp_path: Path):
        study_path = tmp_path / "sample_study"
        study_path.mkdir(parents=True, exist_ok=True)
        (study_path / "ARCHITECTURE.md").write_text(
            "# Sample Engine Architecture\n\nModular actor engine implementation.\n",
            encoding="utf-8",
        )
        (study_path / "DEBUG_NOTES.md").write_text(
            "# Sample Debug Notes\n\nNotes on crash recovery drills.\n",
            encoding="utf-8",
        )

        out_html = compile_study_html(study_path)
        assert Path(out_html).is_file()
        content = Path(out_html).read_text(encoding="utf-8").lower()

        # Strictly assert zero canned strings
        assert "deepinfer" not in content
        assert "driver/worker adapter" not in content
        assert "pre-allocated pools" not in content
