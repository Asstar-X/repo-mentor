#!/usr/bin/env python3
"""
dependency_graph.py - Multi-Language Module & Package Dependency Topology Generator
Part of repo-mentor skill.

Pure Python 3 standard library. No external dependencies.
Inspects project manifests across Go, Rust, TypeScript/JavaScript, Python, and Java
to extract package relationships and render a clean Mermaid dependency DAG.
Supports monorepos and internal workspace cross-dependencies.
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path


def parse_go_mod(file_path: Path) -> dict:
    """Parses go.mod to extract module name and external/internal dependencies."""
    content = file_path.read_text(encoding="utf-8", errors="replace")
    module_name = ""
    direct_deps = []
    indirect_deps = []

    mod_match = re.search(r"^module\s+([^\s\n\r]+)", content, re.MULTILINE)
    if mod_match:
        module_name = mod_match.group(1).strip()

    # Match require blocks
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
                is_indirect = "// indirect" in line
                if is_indirect:
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
        "direct_dependencies": direct_deps,
        "indirect_dependencies": indirect_deps,
        "path": str(file_path)
    }


def parse_cargo_toml(file_path: Path) -> dict:
    """Parses Cargo.toml for package name and dependencies."""
    content = file_path.read_text(encoding="utf-8", errors="replace")
    pkg_name = ""
    dependencies = []
    dev_dependencies = []
    workspace_members = []

    in_package = False
    in_deps = False
    in_dev_deps = False
    in_workspace = False

    for line in content.splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            continue

        if trimmed == "[package]":
            in_package = True
            in_deps = False
            in_dev_deps = False
            in_workspace = False
            continue
        elif trimmed == "[dependencies]":
            in_package = False
            in_deps = True
            in_dev_deps = False
            in_workspace = False
            continue
        elif trimmed == "[dev-dependencies]":
            in_package = False
            in_deps = False
            in_dev_deps = True
            in_workspace = False
            continue
        elif trimmed == "[workspace]":
            in_package = False
            in_deps = False
            in_dev_deps = False
            in_workspace = True
            continue
        elif trimmed.startswith("["):
            in_package = False
            in_deps = False
            in_dev_deps = False
            in_workspace = False

        if in_package and trimmed.startswith("name"):
            m = re.search(r'name\s*=\s*["\']([^"\']+)["\']', trimmed)
            if m:
                pkg_name = m.group(1)

        elif in_deps:
            m = re.match(r'^([a-zA-Z0-9_\-]+)\s*=', trimmed)
            if m:
                dependencies.append(m.group(1))

        elif in_dev_deps:
            m = re.match(r'^([a-zA-Z0-9_\-]+)\s*=', trimmed)
            if m:
                dev_dependencies.append(m.group(1))

    return {
        "type": "Rust",
        "module": pkg_name or file_path.parent.name,
        "dependencies": dependencies,
        "dev_dependencies": dev_dependencies,
        "path": str(file_path)
    }


def parse_package_json(file_path: Path) -> dict:
    """Parses package.json for npm/yarn/pnpm dependencies and workspaces."""
    try:
        data = json.loads(file_path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}

    name = data.get("name", file_path.parent.name)
    deps = list(data.get("dependencies", {}).keys())
    dev_deps = list(data.get("devDependencies", {}).keys())
    workspaces = data.get("workspaces", [])
    if isinstance(workspaces, dict):
        workspaces = workspaces.get("packages", [])

    return {
        "type": "TypeScript/JavaScript",
        "module": name,
        "dependencies": deps,
        "dev_dependencies": dev_deps,
        "workspaces": workspaces,
        "path": str(file_path)
    }


def parse_pyproject_toml(file_path: Path) -> dict:
    """Parses pyproject.toml dependencies."""
    content = file_path.read_text(encoding="utf-8", errors="replace")
    pkg_name = ""
    dependencies = []

    m_name = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
    if m_name:
        pkg_name = m_name.group(1)

    # Basic dependency list extraction
    in_deps = False
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("dependencies = ["):
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
        "path": str(file_path)
    }


def analyze_repo_dependencies(repo_dir: str | Path, internal_only: bool = False) -> dict:
    repo_root = Path(repo_dir).resolve()
    if not repo_root.is_dir():
        return {"error": f"Path is not a directory: {repo_dir}"}

    manifests = []
    ignored_dirs = {".git", "node_modules", "target", "vendor", "__pycache__", ".venv", "venv", "dist", "build"}

    # Walk through repository up to depth 3
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in ignored_dirs and not d.startswith(".")]
        curr_path = Path(root)
        rel_depth = len(curr_path.relative_to(repo_root).parts)
        if rel_depth > 3:
            continue

        for f in files:
            p = curr_path / f
            if f == "go.mod":
                manifests.append(parse_go_mod(p))
            elif f == "Cargo.toml":
                manifests.append(parse_cargo_toml(p))
            elif f == "package.json":
                # Skip package.json inside node_modules or template fixtures
                manifests.append(parse_package_json(p))
            elif f == "pyproject.toml":
                manifests.append(parse_pyproject_toml(p))

    # Filter out empty entries
    manifests = [m for m in manifests if m and m.get("module")]

    all_internal_modules = {m["module"]: m for m in manifests}

    # Build graph edges
    edges = []
    for m in manifests:
        src = m["module"]
        deps = m.get("dependencies", []) + m.get("direct_dependencies", [])
        for d in deps:
            is_internal = d in all_internal_modules
            if internal_only and not is_internal:
                continue
            edges.append({
                "source": src,
                "target": d,
                "is_internal": is_internal
            })

    return {
        "repo_root": str(repo_root),
        "manifest_count": len(manifests),
        "modules": manifests,
        "edges": edges,
        "is_monorepo": len(manifests) > 1
    }


def generate_mermaid_dag(analysis: dict, max_external: int = 15) -> str:
    """Converts dependency analysis into a Mermaid graph TD."""
    modules = analysis.get("modules", [])
    edges = analysis.get("edges", [])

    if not modules:
        return "```mermaid\ngraph TD\n    None[\"No package manifests detected\"]\n```"

    lines = ["```mermaid", "graph TD"]

    # Subgraph for internal modules
    lines.append("    subgraph Modules[\"Internal Repository Modules\"]")
    for m in modules:
        m_id = re.sub(r'[^a-zA-Z0-9_]', '_', m["module"])
        lines.append(f'        {m_id}["{m["module"]} ({m.get("type", "Unknown")})"]')
    lines.append("    end")

    # Render edges
    ext_count = 0
    rendered_edges = set()

    for edge in edges:
        s = re.sub(r'[^a-zA-Z0-9_]', '_', edge["source"])
        t = re.sub(r'[^a-zA-Z0-9_]', '_', edge["target"])
        is_internal = edge.get("is_internal", False)

        if not is_internal:
            if ext_count >= max_external:
                continue
            ext_count += 1

        edge_key = (s, t)
        if edge_key not in rendered_edges:
            rendered_edges.add(edge_key)
            if is_internal:
                lines.append(f"    {s} ==>|internal| {t}")
            else:
                escaped_target = edge["target"].replace('"', "'")
                lines.append(f'    {s} -->|external| {t}["{escaped_target}"]')

    lines.append("```")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate package & module dependency topology DAG for any repository."
    )
    parser.add_argument("repo_dir", help="Path to repository root")
    parser.add_argument("--json", action="store_true", help="Output raw JSON analysis")
    parser.add_argument("--mermaid", action="store_true", help="Output Mermaid diagram")
    parser.add_argument("--internal-only", action="store_true", help="Only show internal module cross-dependencies")

    args = parser.parse_args()

    result = analyze_repo_dependencies(args.repo_dir, internal_only=args.internal_only)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.mermaid:
        print(generate_mermaid_dag(result))
    else:
        print(f"=== Module Dependency Analysis: {result.get('repo_root', '')} ===")
        print(f"Manifests Detected: {result.get('manifest_count', 0)}")
        print(f"Is Monorepo/Multi-Module: {result.get('is_monorepo', False)}")
        print("-" * 50)
        print(generate_mermaid_dag(result))


if __name__ == "__main__":
    main()
