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

import os
import subprocess
import tempfile
from pathlib import Path
import pytest
from typer.testing import CliRunner

from repo_mentor.cli import app
from repo_mentor.core.parser import (
    SymbolIndex,
    PythonASTExtractor,
    GoSymbolLexer,
    RustSymbolLexer,
    TypeScriptSymbolLexer,
)
from repo_mentor.core.dependency import DependencyAnalyzer
from repo_mentor.core.scanner import scan_repo
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
        go_code = '''
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
'''
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
        rs_code = '''
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
'''
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
        ts_code = '''
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
'''
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

    def test_go_internal_package_mapping_gin(self):
        gin_path = Path("/tmp/benchmark-repos/gin")
        if not gin_path.is_dir():
            pytest.skip("Gin benchmark repository not found at /tmp/benchmark-repos/gin")

        analyzer = DependencyAnalyzer(gin_path)
        res = analyzer.analyze(internal_only=True)
        internal_modules = res["internal_modules"]
        edges = res["edges"]

        # Internal package imports must be captured and non-empty
        assert len(internal_modules) >= 5
        assert len(edges) >= 8

        # Explicitly verify required packages
        for req_pkg in ["render", "binding", "internal/fs", "internal/bytesconv"]:
            assert req_pkg in internal_modules, f"Missing Go internal package: {req_pkg}"
            pkg_edges = [e for e in edges if e["source"] == req_pkg or e["target"] == req_pkg]
            assert len(pkg_edges) > 0, f"No edges mapped for internal package: {req_pkg}"

    def test_python_internal_package_mapping_mem0(self):
        mem0_path = Path("/Users/xing/AI/Project/Memory/mem0")
        if not mem0_path.is_dir():
            pytest.skip("Mem0 repository not found at /Users/xing/AI/Project/Memory/mem0")

        analyzer = DependencyAnalyzer(mem0_path)
        res = analyzer.analyze(internal_only=True)
        internal_modules = res["internal_modules"]
        edges = res["edges"]

        assert len(internal_modules) >= 5
        assert len(edges) >= 10
        assert "mem0.memory" in internal_modules
        assert "mem0.configs" in internal_modules

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

    def test_export_mem0_and_check_cleanliness(self):
        study_path = Path("/Users/xing/Coding/Skills项目/repo-mentor/studies/mem0")
        if not study_path.is_dir():
            pytest.skip("mem0 study directory not found")

        out_html = compile_study_html(study_path)
        assert Path(out_html).is_file()
        content = Path(out_html).read_text(encoding="utf-8").lower()

        # Strictly assert zero canned strings
        assert "deepinfer" not in content
        assert "driver/worker adapter" not in content
        assert "pre-allocated pools" not in content

    def test_export_gin_and_check_cleanliness(self):
        study_path = Path("/Users/xing/Coding/Skills项目/repo-mentor/benchmarks/studies/gin")
        if not study_path.is_dir():
            pytest.skip("gin study directory not found")

        out_html = compile_study_html(study_path)
        assert Path(out_html).is_file()
        content = Path(out_html).read_text(encoding="utf-8").lower()

        # Strictly assert zero canned strings
        assert "deepinfer" not in content
        assert "driver/worker adapter" not in content
        assert "pre-allocated pools" not in content
