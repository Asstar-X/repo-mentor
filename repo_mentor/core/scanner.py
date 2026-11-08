"""repo_mentor.core.scanner: Multi-Language Topology & Entrypoint Scanner.

Pure Python standard library implementation with zero external dependencies.
Scans codebases, detects language ecosystems, project manifests,
primary entrypoints (including Go package entrypoints, CLI roots),
and test suites (directories and co-located tests).
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Set

IGNORED_DIRS: Set[str] = {
    ".git", ".svn", ".hg", "node_modules", "target", "vendor",
    "__pycache__", ".venv", "venv", "env", ".idea", ".vscode",
    "dist", "build", "out", "bin", "obj", ".next", ".nuxt",
    ".cache", "coverage", ".pytest_cache", ".mypy_cache",
    ".cargo", ".agents", ".claude"
}

MANIFEST_MAP: Dict[str, List[str]] = {
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

ENTRYPOINT_PATTERNS: Dict[str, List[str]] = {
    "Go": ["main.go", "cmd/**/main.go"],
    "Rust": ["src/main.rs", "src/lib.rs", "main.rs", "lib.rs", "examples/*.rs"],
    "Python": [
        "main.py", "app.py", "cli.py", "__main__.py", "server.py",
        "run.py", "manage.py", "wsgi.py", "asgi.py"
    ],
    "TypeScript/JavaScript": [
        "src/index.ts", "src/index.js", "src/main.ts", "src/main.js",
        "src/cli.ts", "src/server.ts", "index.ts", "index.js",
        "server.js", "app.js", "bin/*.js"
    ],
    "Java/Kotlin": ["*Application.java", "Main.java", "App.java", "*Application.kt", "Main.kt"],
    "C/C++": ["main.c", "main.cpp", "src/main.c", "src/main.cpp", "src/main.cc"],
    "C#/.NET": ["Program.cs", "Startup.cs"]
}

EXT_TO_LANG: Dict[str, str] = {
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


def _detect_go_package_entrypoints(root_path: Path) -> List[Dict[str, str]]:
    """Detects Go library root entrypoints (e.g., gin.go or root package entrypoints)."""
    entrypoints: List[Dict[str, str]] = []
    go_mod = root_path / "go.mod"
    module_leaf = ""
    if go_mod.is_file():
        try:
            content = go_mod.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"^module\s+([^\s\n\r]+)", content, re.MULTILINE)
            if m:
                module_name = m.group(1).strip()
                module_leaf = module_name.split("/")[-1]
        except Exception:
            pass

    # Look for root .go files that act as package entrypoints
    try:
        for go_file in root_path.glob("*.go"):
            if go_file.name.endswith("_test.go"):
                continue
            is_entry = False
            reason = ""
            if module_leaf and go_file.stem == module_leaf:
                is_entry = True
                reason = f"Matches go.mod module name '{module_leaf}'"
            elif go_file.name in ("lib.go", "engine.go", "api.go", "client.go"):
                is_entry = True
                reason = "Common library entrypoint name"
            else:
                # Check for exported constructors
                try:
                    text = go_file.read_text(encoding="utf-8", errors="replace")
                    if re.search(r"\bfunc\s+(?:New|Default|Create|Init)\b", text):
                        is_entry = True
                        reason = "Exports primary constructor (New/Default)"
                except Exception:
                    pass

            if is_entry:
                entrypoints.append({
                    "ecosystem": "Go",
                    "path": go_file.relative_to(root_path).as_posix(),
                    "name": go_file.name,
                    "type": "library_entrypoint",
                    "reason": reason
                })
    except Exception:
        pass

    return entrypoints


def scan_repo(root_dir: str | Path, max_depth: int = 3) -> Dict[str, Any]:
    """Scans repository structure, language ecosystem, entrypoints, and test suites."""
    root_path = Path(root_dir).resolve()
    if not root_path.is_dir():
        return {"error": f"Path is not a directory: {root_dir}"}

    manifests_found: Dict[str, List[str]] = {}
    detected_ecosystems: Set[str] = set()
    entrypoints: List[Dict[str, Any]] = []
    lang_loc: Dict[str, int] = {}
    top_level_dirs: List[Dict[str, Any]] = []
    test_dirs: List[str] = []
    colocated_tests: List[str] = []
    total_files = 0

    # 1. Inspect top-level directory layout
    try:
        for entry in root_path.iterdir():
            if entry.is_dir() and entry.name not in IGNORED_DIRS:
                is_test = entry.name.lower() in {"test", "tests", "testing", "spec", "specs", "__tests__"}
                is_doc = entry.name.lower() in {"doc", "docs", "documentation"}
                is_src = entry.name.lower() in {"src", "pkg", "cmd", "internal", "lib", "core", "app", "packages"}
                dir_summary = {
                    "name": entry.name,
                    "is_test": is_test,
                    "is_doc": is_doc,
                    "is_src": is_src
                }
                top_level_dirs.append(dir_summary)
                if is_test:
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
    agent_frameworks: List[str] = []
    if (root_path / "AGENTS.md").is_file() or (root_path / ".agents").is_dir():
        agent_frameworks.append("Agent Skills / Codex")
    if (root_path / "CLAUDE.md").is_file() or (root_path / ".claude").is_dir():
        agent_frameworks.append("Claude Code Workspace")
    if (root_path / "SKILL.md").is_file() or (root_path / ".gemini").is_dir():
        agent_frameworks.append("Antigravity Skill")

    # 3. Check for standard pattern entrypoints
    check_ecosystems = detected_ecosystems if detected_ecosystems else set(ENTRYPOINT_PATTERNS.keys())
    for eco in check_ecosystems:
        patterns = ENTRYPOINT_PATTERNS.get(eco, [])
        for pattern in patterns:
            try:
                for match in root_path.glob(pattern):
                    rel = match.relative_to(root_path).as_posix()
                    parts = rel.split("/")
                    if not any(p in IGNORED_DIRS for p in parts[:-1]):
                        entrypoints.append({
                            "ecosystem": eco,
                            "path": rel,
                            "name": match.name,
                            "type": "executable_entrypoint",
                            "reason": f"Matches standard {eco} pattern '{pattern}'"
                        })
            except Exception:
                pass

    # 3b. Go package-level entrypoints
    if "Go" in detected_ecosystems or any(root_path.glob("*.go")):
        go_entries = _detect_go_package_entrypoints(root_path)
        existing_paths = {e["path"] for e in entrypoints}
        for ge in go_entries:
            if ge["path"] not in existing_paths:
                entrypoints.append(ge)

    # 4. Walk directory tree to calculate language distribution & discover co-located tests
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        rel_root = Path(root).relative_to(root_path)
        depth = len(rel_root.parts)
        if depth > max_depth:
            continue

        for f in files:
            total_files += 1
            file_path = Path(root) / f
            rel_file_path = file_path.relative_to(root_path).as_posix()

            # Check co-located test files
            if (
                f.endswith("_test.go")
                or (f.startswith("test_") and f.endswith(".py"))
                or (f.endswith("_test.py"))
                or (f.endswith(".test.ts") or f.endswith(".spec.ts"))
                or (f.endswith(".test.js") or f.endswith(".spec.js"))
                or (f.endswith("_test.rs"))
            ):
                colocated_tests.append(rel_file_path)

            ext = os.path.splitext(f)[1].lower()
            if ext in EXT_TO_LANG:
                lang = EXT_TO_LANG[ext]
                try:
                    with open(file_path, "rb") as fp:
                        lines = sum(1 for _ in fp)
                    lang_loc[lang] = lang_loc.get(lang, 0) + lines
                except Exception:
                    pass

    sorted_langs = sorted(lang_loc.items(), key=lambda x: x[1], reverse=True)
    primary_language = sorted_langs[0][0] if sorted_langs else "Unknown"

    # Identify test frameworks
    test_frameworks: List[str] = []
    if "Go" in detected_ecosystems or any(f.endswith("_test.go") for f in colocated_tests):
        test_frameworks.append("go test")
    if "Python" in detected_ecosystems:
        if (root_path / "pytest.ini").is_file() or any("pytest" in str(m) for m in manifests_found.get("Python", [])):
            test_frameworks.append("pytest")
        elif test_dirs or colocated_tests:
            test_frameworks.append("unittest/pytest")
    if "Rust" in detected_ecosystems:
        test_frameworks.append("cargo test")
    if "TypeScript/JavaScript" in detected_ecosystems:
        test_frameworks.append("jest/vitest/mocha")

    test_suites_summary = {
        "frameworks": test_frameworks,
        "test_directories": test_dirs,
        "has_colocated_tests": len(colocated_tests) > 0,
        "colocated_test_count": len(colocated_tests),
        "sample_test_files": colocated_tests[:10]
    }

    return {
        "root": str(root_path),
        "total_files_scanned": total_files,
        "primary_language": primary_language,
        "language_distribution": dict(sorted_langs[:8]),
        "detected_ecosystems": list(detected_ecosystems),
        "agent_frameworks": agent_frameworks,
        "manifests": manifests_found,
        "entrypoints": entrypoints[:15],
        "top_level_dirs": top_level_dirs,
        "test_dirs": test_dirs,
        "test_directories": test_dirs,
        "test_suites": test_suites_summary
    }
