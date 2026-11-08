"""repo_mentor.core.parser: AST & Symbol Parsing Engine.

Zero-dependency Python AST parser and resilient lexers for Go, Rust, and TypeScript.
Extracts classes, structs, interfaces, functions, methods, decorators, line spans,
docstrings, imports, and call invocations.
Constructs a queryable SymbolIndex satisfying the interface contract.
"""

from __future__ import annotations

import ast
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class SymbolLocation:
    """Represents the physical location and metadata of a code symbol."""
    file_path: str
    symbol_name: str
    symbol_type: str  # 'class' | 'struct' | 'function' | 'method' | 'interface'
    start_line: int
    end_line: int
    signature: str = ""
    load_bearing_snippet: str = ""
    docstring: str = ""
    decorators: List[str] = field(default_factory=list)
    parent_symbol: Optional[str] = None


@dataclass
class CallInvocation:
    """Represents a function or method invocation extracted from AST."""
    caller: str
    callee: str
    line: int
    file_path: str


class PythonASTExtractor(ast.NodeVisitor):
    """Zero-dependency visitor for Python AST symbol & call extraction."""

    def __init__(self, file_path: str, source_lines: List[str]):
        self.file_path = file_path
        self.source_lines = source_lines
        self.symbols: List[SymbolLocation] = []
        self.calls: List[CallInvocation] = []
        self.imports: List[Dict[str, Any]] = []
        self._current_scope: List[str] = []

    def _get_snippet(self, start: int, end: int, max_lines: int = 8) -> str:
        s = max(0, start - 1)
        e = min(len(self.source_lines), s + max_lines, end)
        return "\n".join(self.source_lines[s:e])

    def _get_signature(self, node: ast.AST) -> str:
        start = getattr(node, "lineno", 1) - 1
        if 0 <= start < len(self.source_lines):
            # If multi-line def/class, join until colon
            idx = start
            sig_lines = []
            while idx < len(self.source_lines) and idx < start + 5:
                curr = self.source_lines[idx].strip()
                sig_lines.append(curr)
                if ":" in curr:
                    break
                idx += 1
            return " ".join(sig_lines)
        return ""

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append({
                "type": "import",
                "module": alias.name,
                "asname": alias.asname,
                "line": node.lineno
            })
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        mod = node.module or ""
        for alias in node.names:
            self.imports.append({
                "type": "from",
                "module": mod,
                "name": alias.name,
                "asname": alias.asname,
                "level": node.level,
                "line": node.lineno
            })
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        full_name = ".".join(self._current_scope + [node.name])
        decs = [ast.unparse(d) if hasattr(ast, "unparse") else getattr(d, "id", "") for d in node.decorator_list]
        doc = ast.get_docstring(node) or ""
        start = node.lineno
        end = getattr(node, "end_lineno", start)

        sym = SymbolLocation(
            file_path=self.file_path,
            symbol_name=node.name,
            symbol_type="class",
            start_line=start,
            end_line=end,
            signature=self._get_signature(node),
            load_bearing_snippet=self._get_snippet(start, end),
            docstring=doc,
            decorators=decs,
            parent_symbol=self._current_scope[-1] if self._current_scope else None
        )
        self.symbols.append(sym)

        # Also register scoped qualified name if nested
        if self._current_scope:
            self.symbols.append(SymbolLocation(
                file_path=self.file_path,
                symbol_name=full_name,
                symbol_type="class",
                start_line=start,
                end_line=end,
                signature=sym.signature,
                load_bearing_snippet=sym.load_bearing_snippet,
                docstring=doc,
                decorators=decs
            ))

        self._current_scope.append(node.name)
        self.generic_visit(node)
        self._current_scope.pop()

    def _visit_func(self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool = False) -> None:
        in_class = len(self._current_scope) > 0
        sym_type = "method" if in_class else "function"
        parent = self._current_scope[-1] if in_class else None
        decs = [ast.unparse(d) if hasattr(ast, "unparse") else getattr(d, "id", "") for d in node.decorator_list]
        doc = ast.get_docstring(node) or ""
        start = node.lineno
        end = getattr(node, "end_lineno", start)

        sig = self._get_signature(node)
        snippet = self._get_snippet(start, end)

        sym = SymbolLocation(
            file_path=self.file_path,
            symbol_name=node.name,
            symbol_type=sym_type,
            start_line=start,
            end_line=end,
            signature=sig,
            load_bearing_snippet=snippet,
            docstring=doc,
            decorators=decs,
            parent_symbol=parent
        )
        self.symbols.append(sym)

        # If it's a method, also register ClassName.method_name for easy lookup
        if in_class and parent:
            scoped_name = f"{parent}.{node.name}"
            self.symbols.append(SymbolLocation(
                file_path=self.file_path,
                symbol_name=scoped_name,
                symbol_type=sym_type,
                start_line=start,
                end_line=end,
                signature=sig,
                load_bearing_snippet=snippet,
                docstring=doc,
                decorators=decs,
                parent_symbol=parent
            ))

        caller_name = f"{parent}.{node.name}" if in_class and parent else node.name
        self._current_scope.append(node.name)

        # Collect function calls inside this function
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                callee_name = ""
                if isinstance(child.func, ast.Name):
                    callee_name = child.func.id
                elif isinstance(child.func, ast.Attribute):
                    val_str = ast.unparse(child.func.value) if hasattr(ast, "unparse") else ""
                    callee_name = f"{val_str}.{child.func.attr}" if val_str else child.func.attr
                if callee_name:
                    self.calls.append(CallInvocation(
                        caller=caller_name,
                        callee=callee_name,
                        line=getattr(child, "lineno", start),
                        file_path=self.file_path
                    ))

        self.generic_visit(node)
        self._current_scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_func(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_func(node, is_async=True)


class GoSymbolLexer:
    """Resilient lexer for Go package, structs, interfaces, functions, methods, and imports."""

    @staticmethod
    def parse(file_path: str, content: str) -> Tuple[List[SymbolLocation], List[str]]:
        symbols: List[SymbolLocation] = []
        imports: List[str] = []
        lines = content.splitlines()

        # 1. Extract imports
        in_import_block = False
        for line in lines:
            trimmed = line.strip()
            if trimmed.startswith("import ("):
                in_import_block = True
                continue
            elif in_import_block:
                if trimmed == ")":
                    in_import_block = False
                    continue
                m = re.search(r'"([^"]+)"', trimmed)
                if m:
                    imports.append(m.group(1))
            elif trimmed.startswith("import "):
                m = re.search(r'"([^"]+)"', trimmed)
                if m:
                    imports.append(m.group(1))

        # 3. Structs and Interfaces
        type_regex = re.compile(
            r"^\s*type\s+([a-zA-Z0-9_]+)\s+(struct|interface)\b",
            re.MULTILINE
        )
        for m in type_regex.finditer(content):
            name = m.group(1)
            kind = m.group(2)
            start_pos = m.start()
            start_line = content[:start_pos].count("\n") + 1

            # Estimate end line by bracket matching or next type/func
            end_line = start_line
            open_b = 0
            found_open = False
            for idx in range(start_line - 1, len(lines)):
                line_str = lines[idx]
                open_b += line_str.count("{") - line_str.count("}")
                if "{" in line_str:
                    found_open = True
                if found_open and open_b <= 0:
                    end_line = idx + 1
                    break
            if end_line == start_line and idx < len(lines):
                end_line = min(len(lines), start_line + 15)

            snippet = "\n".join(lines[start_line - 1:min(len(lines), start_line + 7)])
            symbols.append(SymbolLocation(
                file_path=file_path,
                symbol_name=name,
                symbol_type="struct" if kind == "struct" else "interface",
                start_line=start_line,
                end_line=end_line,
                signature=lines[start_line - 1].strip() if start_line <= len(lines) else "",
                load_bearing_snippet=snippet
            ))

        # 4. Functions & Methods
        # Methods: func (recv Type) Name(...)
        # Functions: func Name(...)
        func_regex = re.compile(
            r"^\s*func\s+(?:\(\s*([a-zA-Z0-9_\*,\s]+)\s*\)\s+)?([a-zA-Z0-9_]+)\s*\(",
            re.MULTILINE
        )
        for m in func_regex.finditer(content):
            receiver = m.group(1)
            name = m.group(2)
            start_pos = m.start()
            start_line = content[:start_pos].count("\n") + 1

            # Determine method vs function
            parent_type = None
            sym_name = name
            sym_type = "function"
            if receiver:
                sym_type = "method"
                # Parse receiver type: e.g. "engine *Engine" -> "Engine"
                parts = receiver.strip().split()
                if len(parts) >= 2:
                    raw_type = parts[-1].lstrip("*")
                    parent_type = raw_type
                elif len(parts) == 1:
                    raw_type = parts[0].lstrip("*")
                    parent_type = raw_type

            # Bracket match to find end_line
            end_line = start_line
            open_b = 0
            found_open = False
            for idx in range(start_line - 1, len(lines)):
                line_str = lines[idx]
                open_b += line_str.count("{") - line_str.count("}")
                if "{" in line_str:
                    found_open = True
                if found_open and open_b <= 0:
                    end_line = idx + 1
                    break

            snippet = "\n".join(lines[start_line - 1:min(len(lines), start_line + 7)])
            sig = lines[start_line - 1].strip() if start_line <= len(lines) else ""

            symbols.append(SymbolLocation(
                file_path=file_path,
                symbol_name=sym_name,
                symbol_type=sym_type,
                start_line=start_line,
                end_line=end_line,
                signature=sig,
                load_bearing_snippet=snippet,
                parent_symbol=parent_type
            ))

            if parent_type:
                # Also index as Receiver.Name
                scoped_name = f"{parent_type}.{name}"
                symbols.append(SymbolLocation(
                    file_path=file_path,
                    symbol_name=scoped_name,
                    symbol_type="method",
                    start_line=start_line,
                    end_line=end_line,
                    signature=sig,
                    load_bearing_snippet=snippet,
                    parent_symbol=parent_type
                ))

        return symbols, imports


class RustSymbolLexer:
    """Resilient lexer for Rust structs, enums, traits, functions, methods, and modules."""

    @staticmethod
    def parse(file_path: str, content: str) -> Tuple[List[SymbolLocation], List[str]]:
        symbols: List[SymbolLocation] = []
        imports: List[str] = []
        lines = content.splitlines()

        # 1. Uses
        for line in lines:
            m = re.match(r"^\s*use\s+([^;]+);", line)
            if m:
                imports.append(m.group(1).strip())

        # 2. Structs, Enums, Traits
        decl_regex = re.compile(
            r"^\s*(?:pub\s+)?(?:pub\([^\)]+\)\s+)?(struct|enum|trait)\s+([a-zA-Z0-9_]+)",
            re.MULTILINE
        )
        for m in decl_regex.finditer(content):
            kind = m.group(1)
            name = m.group(2)
            start_pos = m.start()
            start_line = content[:start_pos].count("\n") + 1

            # End line bracket match
            end_line = start_line
            open_b = 0
            found_open = False
            for idx in range(start_line - 1, len(lines)):
                line_str = lines[idx]
                open_b += line_str.count("{") - line_str.count("}")
                if "{" in line_str:
                    found_open = True
                if found_open and open_b <= 0:
                    end_line = idx + 1
                    break

            snippet = "\n".join(lines[start_line - 1:min(len(lines), start_line + 7)])
            sym_type = "interface" if kind == "trait" else "struct"
            symbols.append(SymbolLocation(
                file_path=file_path,
                symbol_name=name,
                symbol_type=sym_type,
                start_line=start_line,
                end_line=end_line,
                signature=lines[start_line - 1].strip(),
                load_bearing_snippet=snippet
            ))

        # 3. Functions
        fn_regex = re.compile(
            r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+([a-zA-Z0-9_]+)\s*[\(<]",
            re.MULTILINE
        )
        for m in fn_regex.finditer(content):
            name = m.group(1)
            start_pos = m.start()
            start_line = content[:start_pos].count("\n") + 1

            end_line = start_line
            open_b = 0
            found_open = False
            for idx in range(start_line - 1, len(lines)):
                line_str = lines[idx]
                open_b += line_str.count("{") - line_str.count("}")
                if "{" in line_str:
                    found_open = True
                if found_open and open_b <= 0:
                    end_line = idx + 1
                    break

            snippet = "\n".join(lines[start_line - 1:min(len(lines), start_line + 7)])
            symbols.append(SymbolLocation(
                file_path=file_path,
                symbol_name=name,
                symbol_type="function",
                start_line=start_line,
                end_line=end_line,
                signature=lines[start_line - 1].strip(),
                load_bearing_snippet=snippet
            ))

        return symbols, imports


class TypeScriptSymbolLexer:
    """Resilient lexer for TypeScript / JavaScript symbols and imports."""

    @staticmethod
    def parse(file_path: str, content: str) -> Tuple[List[SymbolLocation], List[str]]:
        symbols: List[SymbolLocation] = []
        imports: List[str] = []
        lines = content.splitlines()

        # 1. Imports
        for line in lines:
            m = re.search(r'from\s+["\']([^"\']+)["\']', line)
            if m:
                imports.append(m.group(1))

        # 2. Classes and Interfaces
        decl_regex = re.compile(
            r"^\s*(?:export\s+)?(?:default\s+)?(class|interface|type)\s+([a-zA-Z0-9_]+)",
            re.MULTILINE
        )
        for m in decl_regex.finditer(content):
            kind = m.group(1)
            name = m.group(2)
            start_pos = m.start()
            start_line = content[:start_pos].count("\n") + 1

            end_line = start_line
            open_b = 0
            found_open = False
            for idx in range(start_line - 1, len(lines)):
                line_str = lines[idx]
                open_b += line_str.count("{") - line_str.count("}")
                if "{" in line_str:
                    found_open = True
                if found_open and open_b <= 0:
                    end_line = idx + 1
                    break

            snippet = "\n".join(lines[start_line - 1:min(len(lines), start_line + 7)])
            symbols.append(SymbolLocation(
                file_path=file_path,
                symbol_name=name,
                symbol_type="class" if kind == "class" else "interface",
                start_line=start_line,
                end_line=end_line,
                signature=lines[start_line - 1].strip(),
                load_bearing_snippet=snippet
            ))

        # 3. Functions
        func_regex = re.compile(
            r"^\s*(?:export\s+)?(?:async\s+)?function\s+([a-zA-Z0-9_]+)\s*\(",
            re.MULTILINE
        )
        for m in func_regex.finditer(content):
            name = m.group(1)
            start_pos = m.start()
            start_line = content[:start_pos].count("\n") + 1

            end_line = start_line
            open_b = 0
            found_open = False
            for idx in range(start_line - 1, len(lines)):
                line_str = lines[idx]
                open_b += line_str.count("{") - line_str.count("}")
                if "{" in line_str:
                    found_open = True
                if found_open and open_b <= 0:
                    end_line = idx + 1
                    break

            snippet = "\n".join(lines[start_line - 1:min(len(lines), start_line + 7)])
            symbols.append(SymbolLocation(
                file_path=file_path,
                symbol_name=name,
                symbol_type="function",
                start_line=start_line,
                end_line=end_line,
                signature=lines[start_line - 1].strip(),
                load_bearing_snippet=snippet
            ))

        return symbols, imports


class SymbolIndex:
    """Multi-file symbol index supporting precise and fuzzy grounding queries."""

    def __init__(self, root_dir: Optional[str | Path] = None):
        self.root_dir = Path(root_dir).resolve() if root_dir else None
        self.symbols_by_file: Dict[str, List[SymbolLocation]] = {}
        self.calls_by_file: Dict[str, List[CallInvocation]] = {}
        self.imports_by_file: Dict[str, List[Any]] = {}

    def _normalize_path(self, file_path: str | Path) -> str:
        p = Path(file_path)
        if self.root_dir and p.is_absolute():
            try:
                return p.relative_to(self.root_dir).as_posix()
            except ValueError:
                return p.as_posix()
        return p.as_posix()

    def add_symbol(self, sym: SymbolLocation) -> None:
        norm_path = self._normalize_path(sym.file_path)
        self.symbols_by_file.setdefault(norm_path, []).append(sym)

    def parse_file(self, file_path: str | Path) -> bool:
        p = Path(file_path).resolve()
        if not p.is_file():
            return False

        norm_path = self._normalize_path(p)
        ext = p.suffix.lower()

        try:
            content = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return False

        lines = content.splitlines()

        if ext == ".py":
            try:
                tree = ast.parse(content, filename=str(p))
                visitor = PythonASTExtractor(norm_path, lines)
                visitor.visit(tree)
                self.symbols_by_file[norm_path] = visitor.symbols
                self.calls_by_file[norm_path] = visitor.calls
                self.imports_by_file[norm_path] = visitor.imports
                return True
            except SyntaxError:
                # Fallback to empty on syntax error
                self.symbols_by_file[norm_path] = []
                return False

        elif ext == ".go":
            syms, imps = GoSymbolLexer.parse(norm_path, content)
            self.symbols_by_file[norm_path] = syms
            self.imports_by_file[norm_path] = imps
            return True

        elif ext == ".rs":
            syms, imps = RustSymbolLexer.parse(norm_path, content)
            self.symbols_by_file[norm_path] = syms
            self.imports_by_file[norm_path] = imps
            return True

        elif ext in (".ts", ".tsx", ".js", ".jsx"):
            syms, imps = TypeScriptSymbolLexer.parse(norm_path, content)
            self.symbols_by_file[norm_path] = syms
            self.imports_by_file[norm_path] = imps
            return True

        return False

    def build_index(self, max_depth: int = 5, extensions: Optional[List[str]] = None) -> int:
        if not self.root_dir or not self.root_dir.is_dir():
            return 0

        target_exts = set(extensions) if extensions else {".py", ".go", ".rs", ".ts", ".tsx", ".js"}
        ignored = {
            ".git", "node_modules", "target", "vendor", "__pycache__",
            ".venv", "venv", "dist", "build"
        }

        count = 0
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in ignored and not d.startswith(".")]
            rel_root = Path(root).relative_to(self.root_dir)
            if len(rel_root.parts) > max_depth:
                continue

            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in target_exts:
                    if self.parse_file(Path(root) / f):
                        count += 1

        return count

    def find_symbol_at(self, file_path: str, line: int) -> Optional[SymbolLocation]:
        """Returns the innermost symbol spanning the specified line."""
        norm_path = self._normalize_path(file_path)
        symbols = self.symbols_by_file.get(norm_path)

        if not symbols:
            # Try fuzzy file match (e.g., basename matching)
            for k, v in self.symbols_by_file.items():
                if k.endswith(norm_path) or norm_path.endswith(k):
                    symbols = v
                    break

        if not symbols:
            return None

        candidates = [s for s in symbols if s.start_line <= line <= s.end_line]
        if not candidates:
            return None

        # Return the innermost (smallest line span)
        candidates.sort(key=lambda s: (s.end_line - s.start_line))
        return candidates[0]

    def has_symbol(
        self,
        file_path: str,
        symbol_name: str,
        start_line: int,
        end_line: int,
        drift_tolerance: int = 15
    ) -> bool:
        """
        Verifies whether a named symbol physically exists in file_path spanning [start_line, end_line].
        Includes drift tolerance of ±15 lines for ongoing Git commits.
        """
        norm_path = self._normalize_path(file_path)
        symbols = self.symbols_by_file.get(norm_path)

        if not symbols:
            for k, v in self.symbols_by_file.items():
                if k.endswith(norm_path) or norm_path.endswith(k):
                    symbols = v
                    break

        if not symbols:
            return False

        clean_target = symbol_name.strip().strip("`").strip("'").strip('"')

        for sym in symbols:
            # Check symbol name match: exact or qualifier match
            name_matches = False
            if sym.symbol_name == clean_target:
                name_matches = True
            elif "." in clean_target:
                # e.g., "Memory.add" matching "Memory.add" or class "Memory" with method "add"
                leaf = clean_target.split(".")[-1]
                if sym.symbol_name == clean_target or (sym.symbol_name == leaf and sym.parent_symbol):
                    name_matches = True
            elif "." in sym.symbol_name:
                leaf = sym.symbol_name.split(".")[-1]
                if leaf == clean_target:
                    name_matches = True

            if name_matches:
                # Check line range overlap with drift tolerance
                window_start = max(1, start_line - drift_tolerance)
                window_end = end_line + drift_tolerance
                # Overlap test: not (sym.end_line < window_start or sym.start_line > window_end)
                if not (sym.end_line < window_start or sym.start_line > window_end):
                    return True

        return False
