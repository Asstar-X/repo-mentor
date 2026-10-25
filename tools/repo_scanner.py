#!/usr/bin/env python3
"""
repo_scanner.py - Universal Multi-Language Repository Topology & Entrypoint Scanner
Part of repo-mentor skill.

Pure Python 3 standard library. No external dependencies.
Scans any codebase, detects language ecosystems, project manifests,
entrypoints, directory layout, and test directories, returning a clean JSON report.
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Directories to ignore during scanning
IGNORED_DIRS = {
    ".git", ".svn", ".hg", "node_modules", "target", "vendor",
    "__pycache__", ".venv", "venv", "env", ".idea", ".vscode",
    "dist", "build", "out", "bin", "obj", ".next", ".nuxt",
    ".cache", "coverage", ".pytest_cache", ".mypy_cache",
    ".cargo", ".agents", ".claude"
}

# Multi-language manifest and configuration file signatures
MANIFEST_MAP = {
    "Go": ["go.mod", "go.sum", "Gopkg.toml"],
    "Rust": ["Cargo.toml", "Cargo.lock"],
    "Python": ["pyproject.toml", "setup.py", "setup.cfg", "Pipfile", "requirements.txt", "poetry.lock"],
    "TypeScript/JavaScript": ["package.json", "tsconfig.json", "pnpm-workspace.yaml", "lerna.json", "yarn.lock"],
    "Java/Kotlin": ["pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle"],
    "C/C++": ["CMakeLists.txt", "Makefile", "meson.build", "configure.ac"],
    "C#/.NET": ["*.sln", "*.csproj", "Directory.Build.props"],
    "Ruby": ["Gemfile", "Gemfile.lock", "*.gemspec"],
    "PHP": ["composer.json", "composer.lock"],
    "Swift": ["Package.swift"],
    "Elixir": ["mix.exs"]
}

# Common entrypoint patterns across ecosystems
ENTRYPOINT_PATTERNS = {
    "Go": ["main.go", "cmd/**/main.go"],
    "Rust": ["src/main.rs", "src/lib.rs", "main.rs", "lib.rs"],
    "Python": ["main.py", "app.py", "cli.py", "__main__.py", "server.py", "run.py", "manage.py", "tools/*.py", "*.py"],
    "TypeScript/JavaScript": ["src/index.ts", "src/index.js", "src/main.ts", "src/main.js", "src/cli.ts", "src/server.ts", "index.ts", "index.js", "server.js", "app.js"],
    "Java/Kotlin": ["*Application.java", "Main.java", "App.java", "*Application.kt", "Main.kt"],
    "C/C++": ["main.c", "main.cpp", "src/main.c", "src/main.cpp", "src/main.cc"],
    "C#/.NET": ["Program.cs", "Startup.cs"]
}

# File extension to language mapping for LOC calculation
EXT_TO_LANG = {
    ".py": "Python",
    ".go": "Go",
    ".rs": "Rust",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".java": "Java",
    ".kt": "Kotlin",
    ".c": "C",
    ".h": "C/C++ Header",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".hpp": "C++ Header",
    ".cs": "C#",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".sh": "Shell",
    ".md": "Markdown",
    ".sql": "SQL"
}


def scan_repo(root_dir: str, max_depth: int = 3) -> dict:
    root_path = Path(root_dir).resolve()
    if not root_path.is_dir():
        return {"error": f"Path is not a directory: {root_dir}"}

    manifests_found = {}
    detected_ecosystems = set()
    entrypoints = []
    lang_loc = {}
    top_level_dirs = []
    test_dirs = []
    total_files = 0

    # 1. Inspect top-level directory layout
    try:
        for entry in root_path.iterdir():
            if entry.is_dir() and entry.name not in IGNORED_DIRS:
                dir_summary = {
                    "name": entry.name,
                    "is_test": entry.name.lower() in {"test", "tests", "testing", "spec", "specs"},
                    "is_doc": entry.name.lower() in {"doc", "docs", "documentation"},
                    "is_src": entry.name.lower() in {"src", "pkg", "cmd", "internal", "lib", "core", "app", "packages"}
                }
                top_level_dirs.append(dir_summary)
                if dir_summary["is_test"]:
                    test_dirs.append(entry.name)
    except PermissionError:
        pass

    # 2. Check for manifests in root
    for eco, manifest_list in MANIFEST_MAP.items():
        for manifest_pattern in manifest_list:
            if "*" in manifest_pattern:
                matches = list(root_path.glob(manifest_pattern))
                if matches:
                    manifests_found.setdefault(eco, []).extend([m.name for m in matches[:3]])
                    detected_ecosystems.add(eco)
            else:
                m_path = root_path / manifest_pattern
                if m_path.is_file():
                    manifests_found.setdefault(eco, []).append(manifest_pattern)
                    detected_ecosystems.add(eco)

    # 2b. Check for special Agent/Workflow signatures
    agent_frameworks = []
    if (root_path / "AGENTS.md").is_file() or (root_path / ".agents").is_dir():
        agent_frameworks.append("Agent Skills / Codex")
    if (root_path / "CLAUDE.md").is_file() or (root_path / ".claude").is_dir():
        agent_frameworks.append("Claude Code Workspace")
    if (root_path / "SKILL.md").is_file() or (root_path / ".gemini").is_dir():
        agent_frameworks.append("Antigravity Skill")

    # 3. Check for entrypoints across detected or all ecosystems
    check_ecosystems = detected_ecosystems if detected_ecosystems else ENTRYPOINT_PATTERNS.keys()
    for eco in check_ecosystems:
        patterns = ENTRYPOINT_PATTERNS.get(eco, [])
        for pattern in patterns:
            try:
                for match in root_path.glob(pattern):
                    rel = match.relative_to(root_path).as_posix()
                    # avoid matching files in ignored dirs
                    parts = rel.split("/")
                    if not any(p in IGNORED_DIRS for p in parts[:-1]):
                        entrypoints.append({
                            "ecosystem": eco,
                            "path": rel,
                            "name": match.name
                        })
            except Exception:
                pass

    # 4. Walk directory tree to calculate language distribution (up to max_depth)
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        rel_root = Path(root).relative_to(root_path)
        depth = len(rel_root.parts)
        if depth > max_depth:
            continue

        for f in files:
            total_files += 1
            ext = os.path.splitext(f)[1].lower()
            if ext in EXT_TO_LANG:
                lang = EXT_TO_LANG[ext]
                file_path = Path(root) / f
                try:
                    with open(file_path, "rb") as fp:
                        lines = sum(1 for _ in fp)
                    lang_loc[lang] = lang_loc.get(lang, 0) + lines
                except Exception:
                    pass

    sorted_langs = sorted(lang_loc.items(), key=lambda x: x[1], reverse=True)
    primary_language = sorted_langs[0][0] if sorted_langs else "Unknown"

    return {
        "root": str(root_path),
        "total_files_scanned": total_files,
        "primary_language": primary_language,
        "language_distribution": dict(sorted_langs[:8]),
        "detected_ecosystems": list(detected_ecosystems),
        "agent_frameworks": agent_frameworks,
        "manifests": manifests_found,
        "entrypoints": entrypoints[:10],
        "top_level_dirs": top_level_dirs,
        "test_dirs": test_dirs,
        "test_directories": test_dirs
    }


def main():
    parser = argparse.ArgumentParser(description="Scan repository structure, language ecosystem, and entrypoints.")
    parser.add_argument("path", nargs="?", default=".", help="Root directory of the repository (default: current directory)")
    parser.add_argument("--depth", type=int, default=3, help="Max depth to scan for code statistics (default: 3)")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")
    args = parser.parse_args()

    result = scan_repo(args.path, max_depth=args.depth)
    if args.pretty:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
