"""tests.test_parser: Tests for Python AST and multi-language symbol parsers."""

import tempfile
from pathlib import Path

from repo_mentor.core.parser import (
    GoSymbolLexer,
    RustSymbolLexer,
    SymbolIndex,
    TypeScriptSymbolLexer,
)

SAMPLE_PYTHON = """
import os
from pathlib import Path

@decorator_a
class MemoryManager:
    \"\"\"Docstring for MemoryManager.\"\"\"
    def __init__(self, capacity: int = 100):
        self.capacity = capacity

    def add_memory(self, item: str) -> bool:
        self.validate(item)
        return True

    def validate(self, item: str) -> None:
        pass

async def async_fetch():
    pass
"""

SAMPLE_GO = """
package router

import (
    "net/http"
    "github.com/gin-gonic/gin/render"
)

type Engine struct {
    trees methodTrees
}

type IEngine interface {
    Run(addr string) error
}

func New() *Engine {
    return &Engine{}
}

func (engine *Engine) Run(addr string) error {
    return nil
}
"""

SAMPLE_RUST = """
use std::collections::HashMap;

pub struct Config {
    pub max_size: usize,
}

pub enum Event {
    Start,
    Stop,
}

pub trait Runner {
    fn run(&self);
}

pub fn execute() -> bool {
    true
}
"""

SAMPLE_TS = """
import { Request, Response } from 'express';

export interface ServerConfig {
    port: number;
}

export class AppServer {
    start(): void {}
}

export function createServer(): AppServer {
    return new AppServer();
}
"""


def test_python_ast_extraction():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "sample.py"
        p.write_text(SAMPLE_PYTHON)

        idx = SymbolIndex(tmp)
        success = idx.parse_file(p)
        assert success is True

        symbols = idx.symbols_by_file.get("sample.py", [])
        names = {s.symbol_name for s in symbols}
        assert "MemoryManager" in names
        assert "add_memory" in names
        assert "MemoryManager.add_memory" in names
        assert "async_fetch" in names

        # Verify query methods
        sym = idx.find_symbol_at("sample.py", 11)
        assert sym is not None
        assert sym.symbol_name in ("add_memory", "MemoryManager.add_memory")

        has_sym = idx.has_symbol("sample.py", "MemoryManager.add_memory", 10, 15)
        assert has_sym is True


def test_go_symbol_lexer():
    symbols, imports = GoSymbolLexer.parse("sample.go", SAMPLE_GO)
    names = {s.symbol_name for s in symbols}
    types = {s.symbol_name: s.symbol_type for s in symbols}

    assert "Engine" in names
    assert types["Engine"] == "struct"
    assert "IEngine" in names
    assert types["IEngine"] == "interface"
    assert "New" in names
    assert types["New"] == "function"
    assert "Run" in names
    assert "Engine.Run" in names

    assert "github.com/gin-gonic/gin/render" in imports


def test_rust_symbol_lexer():
    symbols, imports = RustSymbolLexer.parse("sample.rs", SAMPLE_RUST)
    names = {s.symbol_name for s in symbols}
    types = {s.symbol_name: s.symbol_type for s in symbols}

    assert "Config" in names
    assert types["Config"] == "struct"
    assert "Event" in names
    assert "Runner" in names
    assert types["Runner"] == "interface"
    assert "execute" in names
    assert types["execute"] == "function"


def test_typescript_symbol_lexer():
    symbols, imports = TypeScriptSymbolLexer.parse("sample.ts", SAMPLE_TS)
    names = {s.symbol_name for s in symbols}

    assert "ServerConfig" in names
    assert "AppServer" in names
    assert "createServer" in names
    assert "express" in imports


def test_symbol_index_queries_and_drift_tolerance():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "main.py"
        p.write_text("def target_function():\n    pass\n")

        idx = SymbolIndex(tmp)
        idx.parse_file(p)

        # Within bounds
        assert idx.has_symbol("main.py", "target_function", 1, 2) is True
        # Within drift tolerance (e.g., ±10 lines)
        assert idx.has_symbol("main.py", "target_function", 5, 8, drift_tolerance=15) is True
        # Non-existent symbol
        assert idx.has_symbol("main.py", "phantom_func", 1, 2) is False


def test_symbol_index_syntax_error_handling():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "broken.py"
        p.write_text("def broken_syntax(:\n")

        idx = SymbolIndex(tmp)
        success = idx.parse_file(p)
        assert success is False
        assert idx.symbols_by_file.get("broken.py") == []
