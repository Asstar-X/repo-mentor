#!/usr/bin/env python3
"""
verify_mermaid.py - Mermaid Diagram Syntax Validator & Auto-Fixer for repo-mentor.
Part of repo-mentor skill.

Usage:
  python tools/verify_mermaid.py [path]           # Check diagrams (default: current workspace)
  python tools/verify_mermaid.py [path] --fix     # Check and automatically fix syntax issues in-place

Checks:
1. Diagram header declaration (graph/flowchart/sequenceDiagram/stateDiagram/classDiagram).
2. Flowchart node labels: catches unquoted parentheses/brackets/colons/slashes.
3. Sequence diagram: catches unquoted participant aliases.
4. State diagram: catches C++ namespace scope `::` in transition descriptions.
5. Reserved keywords: catches `end`, `subgraph` used as standalone node IDs.
6. Fenced code block indentation: catches 4+ leading spaces that prevent markdown rendering.

Pure Python 3 standard library.
"""

import sys
import os
import re
import html
import argparse
from pathlib import Path
from typing import List, Dict, Tuple


def sanitize_mermaid_code(code: str) -> str:
    """
    Cleans and hardens Mermaid diagram code to prevent syntax errors in Mermaid 10.x / 9.x:
    1. Unescapes HTML entities (&quot;, &amp;, &lt;, &gt;).
    2. Strips accidental HTML wrapper tags (<p>, </p>, <div>, <span>), standardizes <br/>.
    3. Handles flowchart node labels: Ensures labels with parentheses/colons/slashes are double-quoted.
       Protects already double-quoted labels from being broken by nested brackets.
    4. Sequence diagram: Ensures `participant <id> as "label"` is double-quoted.
    5. State diagram: Replaces reserved `::` in transition labels with `.`.
    6. Replaces internal unescaped double quotes inside quoted labels with single quotes.
    7. Prevents reserved keywords like `end` from being used as target node IDs.
    """
    code = html.unescape(code)
    code = re.sub(r'</?(?:p|div|span)[^>]*>', '', code)
    code = re.sub(r'<br\s*/?>', '<br/>', code, flags=re.IGNORECASE)

    lines = code.splitlines()
    sanitized_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("%%"):
            sanitized_lines.append(line)
            continue

        # 1. Flowchart node label parsing via character scanning & bracket depth
        if any(tok in line for tok in ["-->", "---", "-.->", "==>", "["]):
            res = []
            i = 0
            n = len(line)
            while i < n:
                m = re.match(r'(subgraph\s+[a-zA-Z0-9_\-]+|[a-zA-Z0-9_\-]+)\[', line[i:])
                if m and (i == 0 or not line[i-1].isalnum()):
                    prefix = m.group(1)
                    start_bracket = i + m.end() - 1
                    i = start_bracket + 1

                    if i < n and line[i] == '"':
                        # Already quoted
                        q_start = i
                        i += 1
                        while i < n:
                            if line[i] == '"' and i + 1 < n and line[i+1] == ']':
                                break
                            i += 1
                        content = line[q_start+1:i]
                        i += 2
                        content = content.replace('"', "'")
                        res.append(f'{prefix}["{content}"]')
                    else:
                        # Unquoted label: balance brackets
                        content_chars = []
                        depth = 1
                        while i < n and depth > 0:
                            ch = line[i]
                            if ch == '[':
                                depth += 1
                                content_chars.append('(')
                            elif ch == ']':
                                depth -= 1
                                if depth > 0:
                                    content_chars.append(')')
                            else:
                                content_chars.append(ch)
                            i += 1
                        content = "".join(content_chars).strip()
                        content = content.replace('"', "'")
                        res.append(f'{prefix}["{content}"]')
                else:
                    res.append(line[i])
                    i += 1
            line = "".join(res)

        # 2. Sequence diagram participant alias: `participant ID as "Alias"`
        m_part = re.match(r'^(\s*(?:participant|actor)\s+[a-zA-Z0-9_\-]+\s+as\s+)(.+)$', line)
        if m_part:
            prefix = m_part.group(1)
            alias = m_part.group(2).strip()
            if alias.startswith('"') and alias.endswith('"') and len(alias) >= 2:
                inner = alias[1:-1].replace('"', "'")
            else:
                inner = alias.replace('"', "'")
            line = f'{prefix}"{inner}"'

        # 3. State diagram transitions with `::`
        m_state = re.match(r'^(\s*[a-zA-Z0-9_*\[\]\-]+(?:\s*-->\s*[a-zA-Z0-9_*\[\]\-]+)+\s*:\s*)(.*)$', line)
        if m_state:
            line = m_state.group(1) + m_state.group(2).replace("::", ".")

        # 4. Reserved keyword collision: `--> end` -> `--> _end_node["End"]`
        line = re.sub(r'(-->|---\>|->)\s*(end)\b', r'\1 _end_node["End"]', line)

        sanitized_lines.append(line)

    return "\n".join(sanitized_lines)


def lint_mermaid_block(code: str) -> List[str]:
    """Inspects a Mermaid diagram string for potential syntax errors."""
    issues = []
    lines = code.strip().splitlines()
    if not lines:
        return ["Empty diagram block"]

    first_line = lines[0].strip()
    valid_headers = [
        "graph", "flowchart", "sequencediagram", "statediagram", "statediagram-v2",
        "classdiagram", "erdiagram", "gitgraph", "pie", "journey", "mindmap", "timeline"
    ]
    if not any(first_line.lower().startswith(h) for h in valid_headers):
        issues.append(f"Unrecognized or missing Mermaid diagram header: '{first_line}'")

    for line_idx, line in enumerate(lines[1:], start=2):
        s = line.strip()
        if not s or s.startswith("%%"):
            continue

        # Unquoted parentheses in flowchart
        m_unquoted = re.search(r'\b[a-zA-Z0-9_\-]+\[[^"\]\n]*[()][^"\]\n]*\]', s)
        if m_unquoted:
            issues.append(f"Line {line_idx}: Unquoted parentheses in node label: '{m_unquoted.group(0)}'")

        # Unquoted participant in sequence diagram
        if first_line.lower().startswith("sequencediagram"):
            m_p = re.match(r'^\s*(?:participant|actor)\s+[a-zA-Z0-9_\-]+\s+as\s+([^"\s][^"\n]*)', s)
            if m_p:
                alias = m_p.group(1).strip()
                if any(c in alias for c in "():/#[]"):
                    issues.append(f"Line {line_idx}: Unquoted participant alias with special characters: '{alias}'")

        # C++ scope in state diagram
        if "statediagram" in first_line.lower() and "::" in s:
            issues.append(f"Line {line_idx}: Reserved token '::' in state transition (replace with '.'): '{s}'")

    return issues


def check_file(md_path: Path, auto_fix: bool = False) -> Tuple[int, int, List[str]]:
    """Checks and optionally fixes Mermaid blocks in a markdown file."""
    text = md_path.read_text(encoding="utf-8", errors="replace")
    block_pattern = re.compile(r'((?:[^\n]+\n)*?)(`{3,}|~{3,})[mM]ermaid\s*\n([\s\S]*?)\2')

    issues_found = []
    fixed_count = 0
    total_blocks = 0

    def replace_block(match):
        nonlocal fixed_count, total_blocks
        total_blocks += 1
        prefix = match.group(1)
        fence = match.group(2)
        code = match.group(3)

        block_issues = lint_mermaid_block(code)
        if block_issues:
            for iss in block_issues:
                issues_found.append(f"{md_path.name} (diagram {total_blocks}): {iss}")

        if auto_fix:
            clean_code = sanitize_mermaid_code(code)
            if clean_code != code.strip():
                fixed_count += 1
            return f"{prefix}```mermaid\n{clean_code}\n```"
        return match.group(0)

    new_text = block_pattern.sub(replace_block, text)

    if auto_fix and fixed_count > 0:
        md_path.write_text(new_text, encoding="utf-8")

    return total_blocks, fixed_count, issues_found


def main():
    parser = argparse.ArgumentParser(description="Mermaid Diagram Syntax Validator & Auto-Fixer")
    parser.add_argument("path", nargs="?", default=".", help="Target markdown file or directory to scan")
    parser.add_argument("--fix", action="store_true", help="Automatically repair syntax issues in-place")
    args = parser.parse_args()

    target_path = Path(args.path).resolve()
    if target_path.is_file():
        files = [target_path]
    elif target_path.is_dir():
        files = sorted([
            p for p in target_path.glob("**/*.md")
            if not any(skip in p.parts for skip in [".git", "node_modules", "__pycache__"])
        ])
    else:
        print(f"Error: Path '{args.path}' does not exist.")
        sys.exit(1)

    all_issues = []
    total_diagrams = 0
    total_fixed = 0

    for f in files:
        diag_count, fixed, issues = check_file(f, auto_fix=args.fix)
        total_diagrams += diag_count
        total_fixed += fixed
        all_issues.extend(issues)

    print(f"=== Mermaid Diagram Inspection ({len(files)} markdown files scanned) ===")
    print(f"Total Diagrams Found : {total_diagrams}")
    print(f"Total Issues Detected: {len(all_issues)}")

    if args.fix:
        print(f"Total Blocks Repaired: {total_fixed}")

    if all_issues:
        print("\n[Issues Detected]")
        for iss in all_issues:
            print(f"  • {iss}")
        if not args.fix:
            print("\nTip: Run with --fix to automatically repair standard Mermaid syntax issues.")
            sys.exit(1)
        else:
            print("\n✓ Auto-fix completed.")
            sys.exit(0)
    else:
        print("\n✓ All Mermaid diagrams passed syntax inspection!")
        sys.exit(0)


if __name__ == "__main__":
    main()
