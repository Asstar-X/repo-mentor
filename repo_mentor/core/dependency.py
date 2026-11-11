"""repo_mentor.core.dependency: Internal & External Package Dependency DAG Analyzer.

Resolves intra-repo module and package dependencies across Go, Python, Rust, and TypeScript.
Solves the single-module internal package edge defect by parsing intra-repo imports
(e.g., Go `github.com/gin-gonic/gin/render` -> `render/`, Python `from mem0.memory import ...`).
Generates valid, quoted Mermaid DAG diagrams.
"""

from __future__ import annotations

import ast
import json
import os
import re
from pathlib import Path
from typing import Any

IGNORED_DIRS: set[str] = {
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    "target",
    "vendor",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".idea",
    ".vscode",
    "dist",
    "build",
    "out",
    "bin",
    "obj",
    ".next",
    ".nuxt",
    ".cache",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
    ".cargo",
    ".agents",
    ".claude",
}


def _sanitize_mermaid_id(name: str) -> str:
    """Sanitizes any identifier into a valid Mermaid node ID."""
    clean = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    if not clean or clean[0].isdigit():
        clean = "mod_" + clean
    return clean


def _sanitize_mermaid_label(label: str) -> str:
    """Escapes label text for safe rendering in Mermaid node strings."""
    return label.replace('"', "'").replace("\n", " ").strip()


class DependencyAnalyzer:
    """Extracts internal and external dependency relationships across languages."""

    def __init__(self, repo_dir: str | Path):
        self.repo_root = Path(repo_dir).resolve()
        self.manifests: list[dict[str, Any]] = []
        self.internal_modules: set[str] = set()
        self.edges: list[dict[str, Any]] = []

    def _parse_go_mod(self, file_path: Path) -> dict[str, Any]:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        module_name = ""
        direct_deps: list[str] = []
        indirect_deps: list[str] = []

        mod_match = re.search(r"^module\s+([^\s\n\r]+)", content, re.MULTILINE)
        if mod_match:
            module_name = mod_match.group(1).strip()

        in_require = False
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("require ("):
                in_require = True
                continue
            elif in_require and line.startswith(")"):
                in_require = False
                continue
            elif in_require:
                parts = line.split()
                if parts and not parts[0].startswith("//"):
                    dep_pkg = parts[0]
                    if "// indirect" in line:
                        indirect_deps.append(dep_pkg)
                    else:
                        direct_deps.append(dep_pkg)
            elif line.startswith("require ") and "(" not in line:
                parts = line.split()
                if len(parts) >= 2:
                    dep_pkg = parts[1]
                    if "// indirect" in line:
                        indirect_deps.append(dep_pkg)
                    else:
                        direct_deps.append(dep_pkg)

        return {
            "type": "Go",
            "module": module_name or file_path.parent.name,
            "root_module": module_name,
            "direct_dependencies": direct_deps,
            "indirect_dependencies": indirect_deps,
            "path": str(file_path.relative_to(self.repo_root).as_posix()),
        }

    def _parse_cargo_toml(self, file_path: Path) -> dict[str, Any]:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        pkg_name = ""
        dependencies: list[str] = []
        in_package = False
        in_deps = False

        for line in content.splitlines():
            trimmed = line.strip()
            if not trimmed or trimmed.startswith("#"):
                continue
            if trimmed == "[package]":
                in_package = True
                in_deps = False
                continue
            elif trimmed == "[dependencies]":
                in_package = False
                in_deps = True
                continue
            elif trimmed.startswith("["):
                in_package = False
                in_deps = False

            if in_package and trimmed.startswith("name"):
                m = re.search(r'name\s*=\s*["\']([^"\']+)["\']', trimmed)
                if m:
                    pkg_name = m.group(1)
            elif in_deps:
                m = re.match(r"^([a-zA-Z0-9_\-]+)\s*=", trimmed)
                if m:
                    dependencies.append(m.group(1))

        return {
            "type": "Rust",
            "module": pkg_name or file_path.parent.name,
            "dependencies": dependencies,
            "path": str(file_path.relative_to(self.repo_root).as_posix()),
        }

    def _parse_package_json(self, file_path: Path) -> dict[str, Any]:
        try:
            data = json.loads(file_path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            return {}

        name = data.get("name", file_path.parent.name)
        deps = list(data.get("dependencies", {}).keys())
        dev_deps = list(data.get("devDependencies", {}).keys())

        return {
            "type": "TypeScript/JavaScript",
            "module": name,
            "dependencies": deps,
            "dev_dependencies": dev_deps,
            "path": str(file_path.relative_to(self.repo_root).as_posix()),
        }

    def _parse_pyproject_toml(self, file_path: Path) -> dict[str, Any]:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        pkg_name = ""
        dependencies: list[str] = []

        m_name = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
        if m_name:
            pkg_name = m_name.group(1)

        in_deps = False
        for line in content.splitlines():
            line = line.strip()
            if "dependencies = [" in line or line.startswith("dependencies = ["):
                in_deps = True
                continue
            elif in_deps and line.endswith("]"):
                in_deps = False
                continue
            elif in_deps:
                dep_m = re.search(r'["\']([a-zA-Z0-9_\-]+)[^"\']*["\']', line)
                if dep_m:
                    dependencies.append(dep_m.group(1))

        return {
            "type": "Python",
            "module": pkg_name or file_path.parent.name,
            "dependencies": dependencies,
            "path": str(file_path.relative_to(self.repo_root).as_posix()),
        }

    def _discover_go_internal_edges(self, go_mod_info: dict[str, Any]) -> None:
        """Parses Go source files to detect internal package imports."""
        root_module = go_mod_info.get("root_module", "")
        if not root_module:
            return

        # Scan all .go files for intra-repo imports
        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
            rel_dir = Path(root).relative_to(self.repo_root).as_posix()
            source_pkg = rel_dir if rel_dir != "." else go_mod_info.get("module", "root")

            for f in files:
                if not f.endswith(".go") or f.endswith("_test.go"):
                    continue
                file_p = Path(root) / f
                try:
                    content = file_p.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue

                # Match imports like "github.com/gin-gonic/gin/render"
                matches = re.findall(rf'"{re.escape(root_module)}/([^"]+)"', content)
                for subpkg in matches:
                    clean_target = subpkg.strip("/")
                    self.internal_modules.add(source_pkg)
                    self.internal_modules.add(clean_target)
                    self.edges.append(
                        {
                            "source": source_pkg,
                            "target": clean_target,
                            "is_internal": True,
                            "ecosystem": "Go",
                        }
                    )

    def _discover_python_internal_edges(self) -> None:
        """Parses Python source files to detect internal package and sub-package edges."""
        # Detect top-level packages (directories containing __init__.py or containing py files)
        py_packages: set[str] = set()
        for item in self.repo_root.iterdir():
            if item.is_dir() and item.name not in IGNORED_DIRS and not item.name.startswith("."):
                if (item / "__init__.py").is_file() or any(item.glob("*.py")):
                    py_packages.add(item.name)

        if not py_packages:
            return

        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
            rel_dir = Path(root).relative_to(self.repo_root).as_posix()
            parts = rel_dir.split("/")
            if not parts or parts[0] not in py_packages:
                continue

            # Determine source package name, e.g. "mem0.memory" or "mem0"
            source_mod = ".".join(parts[:2]) if len(parts) >= 2 else parts[0]

            for f in files:
                if not f.endswith(".py") or f.startswith("test_") or f.endswith("_test.py"):
                    continue
                file_p = Path(root) / f
                try:
                    content = file_p.read_text(encoding="utf-8", errors="replace")
                    tree = ast.parse(content, filename=str(file_p))
                except Exception:
                    continue

                for node in ast.walk(tree):
                    target_mod = ""
                    if isinstance(node, ast.ImportFrom) and node.module:
                        mod_parts = node.module.split(".")
                        if mod_parts[0] in py_packages:
                            target_mod = (
                                ".".join(mod_parts[:2]) if len(mod_parts) >= 2 else mod_parts[0]
                            )
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            mod_parts = alias.name.split(".")
                            if mod_parts[0] in py_packages:
                                target_mod = (
                                    ".".join(mod_parts[:2]) if len(mod_parts) >= 2 else mod_parts[0]
                                )

                    if target_mod and target_mod != source_mod:
                        self.internal_modules.add(source_mod)
                        self.internal_modules.add(target_mod)
                        self.edges.append(
                            {
                                "source": source_mod,
                                "target": target_mod,
                                "is_internal": True,
                                "ecosystem": "Python",
                            }
                        )

    def analyze(self, internal_only: bool = False) -> dict[str, Any]:
        """Runs comprehensive dependency analysis across manifests and source code."""
        # 1. Discover manifests up to depth 3
        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
            curr_path = Path(root)
            rel_depth = len(curr_path.relative_to(self.repo_root).parts)
            if rel_depth > 3:
                continue

            for f in files:
                p = curr_path / f
                if f == "go.mod":
                    parsed = self._parse_go_mod(p)
                    self.manifests.append(parsed)
                    self._discover_go_internal_edges(parsed)
                elif f == "Cargo.toml":
                    self.manifests.append(self._parse_cargo_toml(p))
                elif f == "package.json":
                    # Skip examples / docs package.json if desired or include as external
                    self.manifests.append(self._parse_package_json(p))
                elif f == "pyproject.toml":
                    self.manifests.append(self._parse_pyproject_toml(p))

        # 2. Discover Python internal package imports
        self._discover_python_internal_edges()

        # 3. Add manifest-level dependencies
        manifest_modules = {m["module"]: m for m in self.manifests if m and m.get("module")}
        for mod_name in manifest_modules:
            self.internal_modules.add(mod_name)

        for m in self.manifests:
            src = m["module"]
            deps = m.get("dependencies", []) + m.get("direct_dependencies", [])
            for d in deps:
                is_internal = d in self.internal_modules
                if internal_only and not is_internal:
                    continue
                self.edges.append(
                    {
                        "source": src,
                        "target": d,
                        "is_internal": is_internal,
                        "ecosystem": m.get("type", "Unknown"),
                    }
                )

        # Deduplicate edges
        seen_edges: set[tuple[str, str]] = set()
        unique_edges: list[dict[str, Any]] = []
        for e in self.edges:
            pair = (e["source"], e["target"])
            if pair not in seen_edges:
                seen_edges.add(pair)
                if not internal_only or e["is_internal"]:
                    unique_edges.append(e)

        return {
            "repo_root": str(self.repo_root),
            "manifest_count": len(self.manifests),
            "manifests": self.manifests,
            "internal_modules": sorted(self.internal_modules),
            "edges": unique_edges,
            "is_monorepo": len(self.manifests) > 1,
            "internal_edge_count": sum(1 for e in unique_edges if e["is_internal"]),
        }

    def generate_mermaid_dag(
        self, analysis: dict[str, Any] | None = None, max_external: int = 15
    ) -> str:
        """Converts dependency analysis into a clean, valid Mermaid graph TD."""
        data = analysis or self.analyze()
        internal_mods = data.get("internal_modules", [])
        edges = data.get("edges", [])

        if not internal_mods and not edges:
            return '```mermaid\ngraph TD\n    None["No package manifests or internal modules detected"]\n```'

        lines = ["```mermaid", "graph TD"]

        # Subgraph for internal repository modules
        if internal_mods:
            lines.append('    subgraph Internal["Internal Repository Modules"]')
            for mod in internal_mods:
                mod_id = _sanitize_mermaid_id(mod)
                mod_label = _sanitize_mermaid_label(mod)
                lines.append(f'        {mod_id}["{mod_label}"]')
            lines.append("    end")

        # Render edges
        ext_count = 0
        rendered_edges: set[tuple[str, str]] = set()

        for edge in edges:
            s_name = edge["source"]
            t_name = edge["target"]
            is_internal = edge.get("is_internal", False)

            if not is_internal:
                if ext_count >= max_external:
                    continue
                ext_count += 1

            s_id = _sanitize_mermaid_id(s_name)
            t_id = _sanitize_mermaid_id(t_name)
            edge_key = (s_id, t_id)

            if edge_key not in rendered_edges:
                rendered_edges.add(edge_key)
                if is_internal:
                    lines.append(f"    {s_id} ==>|internal| {t_id}")
                else:
                    escaped_target = _sanitize_mermaid_label(t_name)
                    lines.append(f'    {s_id} -->|external| {t_id}["{escaped_target}"]')

        lines.append("```")
        return "\n".join(lines)


def analyze_dependencies(repo_dir: str | Path, internal_only: bool = False) -> dict[str, Any]:
    """Functional entrypoint for dependency analysis."""
    analyzer = DependencyAnalyzer(repo_dir)
    return analyzer.analyze(internal_only=internal_only)


def generate_mermaid(
    repo_dir: str | Path, internal_only: bool = False, max_external: int = 15
) -> str:
    """Functional entrypoint for generating a Mermaid DAG string."""
    analyzer = DependencyAnalyzer(repo_dir)
    analysis = analyzer.analyze(internal_only=internal_only)
    return analyzer.generate_mermaid_dag(analysis, max_external=max_external)
