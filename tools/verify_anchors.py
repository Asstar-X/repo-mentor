#!/usr/bin/env python3
"""
verify_anchors.py - Deterministic Code Anchor & Line Number Verifier
Part of repo-mentor skill.

Pure Python 3 standard library. No external dependencies.
Scans generated Markdown files for file references and line-number anchors
(e.g., [src/engine.go#L45-L60], [path/to/file.py#L12], `path/to/file.rs#L10-L20`),
and validates that the target files actually exist in the target repository
and the referenced line numbers fall strictly within the valid range of the file.
Prevents LLM code hallucination and fictitious line anchors.
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path

# Regular expressions to catch various code anchor patterns:
# 1. Standard markdown link: [text](path/to/file#L10-L20) or [text](file:///path/to/file#L10-L20)
MD_LINK_RE = re.compile(r'\[([^\]]+)\]\((?:file://)?([^)#]+)(?:#L(\d+)(?:-L?(\d+))?)?\)')

# 2. Shorthand anchor with line numbers: [path/to/file#L10-L20] or [path/to/file#L10]
BRACKET_LINE_RE = re.compile(r'\[([a-zA-Z0-9_\-\./\\]+)#L(\d+)(?:-L?(\d+))?\]')

# 3. Shorthand anchor without line numbers: [path/to/file.ext] or [dir/file]
BRACKET_FILE_RE = re.compile(r'\[([a-zA-Z0-9_\-\./\\]*(?:/[a-zA-Z0-9_\-\.]+|\.[a-zA-Z0-9_]{1,10}))\]')

# 4. Inline backtick anchor: `path/to/file#L10-L20`
BACKTICK_ANCHOR_RE = re.compile(r'`([a-zA-Z0-9_\-\./\\]+)#L(\d+)(?:-L?(\d+))?`')

# Ignored extensions and schemes
IGNORED_SCHEMES = ("http://", "https://", "mailto:", "ftp://", "#")
IGNORED_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".pdf"}


def extract_anchors_from_text(text: str) -> list[dict]:
    """
    Extracts all candidate code file references and line ranges from Markdown text.
    """
    anchors = []
    seen = set()

    def add_anchor(raw_path: str, start_line: str | None, end_line: str | None, source_type: str):
        raw_path = raw_path.strip()
        # Filter out web links and pure anchor jumps
        if any(raw_path.startswith(sch) for sch in IGNORED_SCHEMES):
            return
        # Filter out image files
        ext = os.path.splitext(raw_path)[1].lower()
        if ext in IGNORED_EXTS:
            return
        # Normalize slashes
        clean_path = raw_path.replace("\\", "/")
        s_line = int(start_line) if start_line else None
        e_line = int(end_line) if end_line else (s_line if s_line else None)
        
        key = (clean_path, s_line, e_line)
        if key not in seen:
            seen.add(key)
            anchors.append({
                "path": clean_path,
                "start_line": s_line,
                "end_line": e_line,
                "type": source_type
            })

    # Match pattern 1: Markdown links [label](path#Lstart-Lend)
    for match in MD_LINK_RE.finditer(text):
        label, p, s, e = match.groups()
        add_anchor(p, s, e, "markdown_link")

    # Match pattern 2: Bracketed shorthand with line numbers [file#Lstart-Lend]
    for match in BRACKET_LINE_RE.finditer(text):
        p, s, e = match.groups()
        add_anchor(p, s, e, "bracket_line_anchor")

    # Match pattern 3: Bracketed file path [dir/file] or [file.ext]
    for match in BRACKET_FILE_RE.finditer(text):
        p = match.group(1)
        # Avoid matching markdown section labels like [NEW], [DELETE], [MODIFY], [TODO]
        if p.upper() in {"NEW", "DELETE", "MODIFY", "TODO", "NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION"}:
            continue
        add_anchor(p, None, None, "bracket_file_anchor")

    # Match pattern 4: Backticked anchors `file#Lstart-Lend`
    for match in BACKTICK_ANCHOR_RE.finditer(text):
        p, s, e = match.groups()
        add_anchor(p, s, e, "backtick_anchor")

    return anchors


def verify_anchors(repo_dir: str | Path, markdown_path: str | Path) -> dict:
    """
    Verifies all anchors in a given markdown file against the repo root.
    """
    repo_root = Path(repo_dir).resolve()
    md_file = Path(markdown_path).resolve()

    if not repo_root.is_dir():
        return {
            "valid": False,
            "error": f"Repository root directory not found: {repo_dir}",
            "total_anchors": 0,
            "verified": 0,
            "failed": []
        }

    if not md_file.is_file():
        return {
            "valid": False,
            "error": f"Markdown file not found: {markdown_path}",
            "total_anchors": 0,
            "verified": 0,
            "failed": []
        }

    try:
        content = md_file.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {
            "valid": False,
            "error": f"Failed to read markdown file: {str(e)}",
            "total_anchors": 0,
            "verified": 0,
            "failed": []
        }

    anchors = extract_anchors_from_text(content)
    failed = []
    verified_count = 0
    file_line_cache: dict[str, int] = {}

    for anchor in anchors:
        rel_path = anchor["path"]
        start_line = anchor["start_line"]
        end_line = anchor["end_line"]

        # Resolve target file path (check relative to repo root, or if absolute matches repo, or study-local link)
        if os.path.isabs(rel_path):
            target_file = Path(rel_path).resolve()
        elif (repo_root / rel_path).resolve().exists():
            target_file = (repo_root / rel_path).resolve()
        elif (md_file.parent / rel_path).resolve().exists():
            # Local study documentation link (e.g. ARCHITECTURE.md, traces/foo.md)
            target_file = (md_file.parent / rel_path).resolve()
            if target_file.is_file() or target_file.is_dir():
                verified_count += 1
                continue
        else:
            target_file = (repo_root / rel_path).resolve()
        
        # Security check: must not escape repo root (unless it is study local documentation)
        try:
            target_file.relative_to(repo_root)
        except ValueError:
            failed.append({
                "anchor": anchor,
                "reason": f"Path escapes repository root: {rel_path}"
            })
            continue

        if target_file.is_dir():
            if start_line is not None:
                failed.append({
                    "anchor": anchor,
                    "reason": f"Directory cannot have line number anchor: {rel_path}"
                })
            else:
                verified_count += 1
            continue

        if not target_file.is_file():
            failed.append({
                "anchor": anchor,
                "reason": f"Target file does not exist in repo: {rel_path}"
            })
            continue

        # Count lines with cache
        target_str = str(target_file)
        if target_str not in file_line_cache:
            try:
                with open(target_file, "r", encoding="utf-8", errors="replace") as f:
                    file_line_cache[target_str] = sum(1 for _ in f)
            except Exception as e:
                failed.append({
                    "anchor": anchor,
                    "reason": f"Could not read target file {rel_path}: {str(e)}"
                })
                continue

        total_lines = file_line_cache[target_str]

        # Line number validation
        if start_line is not None:
            if start_line <= 0:
                failed.append({
                    "anchor": anchor,
                    "reason": f"Invalid start line {start_line} (must be >= 1)"
                })
                continue
            if start_line > total_lines:
                failed.append({
                    "anchor": anchor,
                    "reason": f"Start line {start_line} exceeds file length ({total_lines} lines) in {rel_path}"
                })
                continue

        if end_line is not None:
            if end_line < (start_line or 1):
                failed.append({
                    "anchor": anchor,
                    "reason": f"End line {end_line} is before start line {start_line} in {rel_path}"
                })
                continue
            if end_line > total_lines:
                failed.append({
                    "anchor": anchor,
                    "reason": f"End line {end_line} exceeds file length ({total_lines} lines) in {rel_path}"
                })
                continue

        verified_count += 1

    is_valid = len(failed) == 0

    return {
        "valid": is_valid,
        "markdown_file": str(md_file),
        "repo_root": str(repo_root),
        "total_anchors": len(anchors),
        "verified": verified_count,
        "failed": failed
    }


def main():
    parser = argparse.ArgumentParser(
        description="Verify code anchors and line numbers in Markdown notes against a target repository."
    )
    parser.add_argument("repo_dir", help="Path to the target codebase repository root")
    parser.add_argument("markdown_file", help="Path to the Markdown file containing code anchors")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    result = verify_anchors(args.repo_dir, args.markdown_file)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"=== Code Anchor Verification: {result.get('markdown_file', '')} ===")
        print(f"Repository Root: {result.get('repo_root', '')}")
        print(f"Total Anchors Found: {result.get('total_anchors', 0)}")
        print(f"Verified Valid:      {result.get('verified', 0)}")
        print(f"Failed / Invalid:    {len(result.get('failed', []))}")
        print("-" * 50)

        if result.get("valid"):
            print("✓ All code anchors and line references are 100% verified against live repository files.")
            sys.exit(0)
        else:
            print("✗ FAILED: Found invalid or hallucinated code anchors:")
            for item in result.get("failed", []):
                anchor = item.get("anchor", {})
                reason = item.get("reason", "Unknown error")
                path = anchor.get("path", "")
                s = anchor.get("start_line")
                e = anchor.get("end_line")
                line_str = f"#L{s}-L{e}" if s and e and s != e else (f"#L{s}" if s else "")
                print(f"  - [{path}{line_str}]: {reason}")
            sys.exit(1)


if __name__ == "__main__":
    main()
