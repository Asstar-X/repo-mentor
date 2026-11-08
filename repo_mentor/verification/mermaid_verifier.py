"""repo_mentor.verification.mermaid_verifier: Mermaid Diagram Syntax Validator & Repair Engine.

Inspects Mermaid diagram syntax, unclosed braces/quotes, participant aliases,
reserved characters, and repairs common syntax issues automatically.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple

from rich.console import Console

console = Console()

VALID_HEADERS = (
    "graph", "flowchart", "sequencediagram", "statediagram", "statediagram-v2",
    "classdiagram", "erdiagram", "gitgraph", "pie", "journey", "mindmap", "timeline"
)


@dataclass
class MermaidIssue:
    """Represents a syntax issue detected in a Mermaid diagram."""
    line_num: int
    rule: str
    raw_line: str
    message: str


@dataclass
class MermaidVerificationResult:
    """Outcome of validating and/or repairing Mermaid diagrams in a document."""
    target_file: str
    total_diagrams: int
    valid_diagrams: int
    issues: List[MermaidIssue] = field(default_factory=list)
    repaired: bool = False


def lint_mermaid_code(code: str) -> List[MermaidIssue]:
    """Inspects a Mermaid diagram string for potential syntax errors."""
    issues: List[MermaidIssue] = []
    lines = code.strip().splitlines()
    if not lines:
        return [MermaidIssue(line_num=1, rule="empty_diagram", raw_line="", message="Empty Mermaid diagram block")]

    # 1. Header check
    first_non_empty = 0
    header_line = ""
    for idx, l in enumerate(lines):
        s = l.strip()
        if s and not s.startswith("%%"):
            first_non_empty = idx + 1
            header_line = s
            break

    if not header_line:
        return [MermaidIssue(line_num=1, rule="no_header", raw_line="", message="Mermaid block contains only comments")]

    if not any(header_line.lower().startswith(h) for h in VALID_HEADERS):
        issues.append(MermaidIssue(
            line_num=first_non_empty,
            rule="invalid_header",
            raw_line=header_line,
            message=f"Unrecognized or missing Mermaid diagram header: '{header_line}'"
        ))

    is_flowchart = any(header_line.lower().startswith(h) for h in ("graph", "flowchart"))
    is_sequence = header_line.lower().startswith("sequencediagram")
    is_state = header_line.lower().startswith("statediagram")

    for line_idx, line in enumerate(lines, start=1):
        s = line.strip()
        if not s or s.startswith("%%"):
            continue

        # Skip the header line itself
        if line_idx == first_non_empty:
            continue

        # 2. Check for unclosed double quotes
        quote_count = s.count('"')
        if quote_count % 2 != 0:
            issues.append(MermaidIssue(
                line_num=line_idx,
                rule="unclosed_quotes",
                raw_line=s,
                message=f"Odd number of double quotes ({quote_count}) detected"
            ))

        # 3. Flowchart unquoted parentheses/brackets/colons/slashes
        if is_flowchart:
            m_unquoted_parens = re.search(r'\b[a-zA-Z0-9_\-]+\[[^"\]\n]*[()][^"\]\n]*\]', s)
            if m_unquoted_parens:
                issues.append(MermaidIssue(
                    line_num=line_idx,
                    rule="unquoted_flowchart_label",
                    raw_line=s,
                    message=f"Unquoted parentheses in flowchart node label: '{m_unquoted_parens.group(0)}'"
                ))
            # Reserved keyword 'end' as target node: e.g. '--> end'
            if re.search(r'(?:-->|---\>|->)\s*end\b', s):
                issues.append(MermaidIssue(
                    line_num=line_idx,
                    rule="reserved_node_id",
                    raw_line=s,
                    message="Reserved keyword 'end' used as target node ID without quoting"
                ))

        # 4. Sequence diagram unquoted participant aliases
        if is_sequence:
            m_part = re.match(r'^\s*(?:participant|actor)\s+[a-zA-Z0-9_\-]+\s+as\s+(.+)$', s)
            if m_part:
                alias = m_part.group(1).strip()
                if not (alias.startswith('"') and alias.endswith('"')):
                    issues.append(MermaidIssue(
                        line_num=line_idx,
                        rule="unquoted_participant_alias",
                        raw_line=s,
                        message=f"Unquoted participant alias in sequence diagram: '{alias}'"
                    ))

        # 5. State diagram reserved :: in transition descriptions
        if is_state:
            m_state = re.match(r'^\s*[a-zA-Z0-9_*\[\]\-]+(?:\s*-->\s*[a-zA-Z0-9_*\[\]\-]+)+\s*:\s*(.*)$', s)
            if m_state and "::" in m_state.group(1):
                issues.append(MermaidIssue(
                    line_num=line_idx,
                    rule="state_transition_colons",
                    raw_line=s,
                    message="Reserved '::' detected in state transition label (breaks parser)"
                ))

    return issues


def repair_mermaid_code(code: str) -> str:
    """
    Cleans and hardens Mermaid diagram code to prevent rendering crashes:
    1. Unescapes HTML entities.
    2. Strips accidental HTML wrapper tags (<p>, </p>, <div>, <span>), standardizes <br/>.
    3. Handles flowchart node labels: Ensures labels with parentheses/colons/slashes are double-quoted.
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


def extract_mermaid_blocks(markdown_text: str) -> List[Tuple[int, int, str]]:
    """Extracts all ```mermaid ... ``` code blocks with start/end character offsets."""
    pattern = re.compile(r'```(?:mermaid)\r?\n(.*?)```', re.DOTALL)
    blocks = []
    for m in pattern.finditer(markdown_text):
        blocks.append((m.start(), m.end(), m.group(1)))
    return blocks


def verify_study_mermaid(
    study_dir_or_file: str | Path,
    fix: bool = False
) -> Dict[str, Any]:
    """
    Scans markdown files in target directory/file for Mermaid diagram syntax errors.
    Optionally repairs issues in-place.
    """
    target = Path(study_dir_or_file).resolve()
    if target.is_file():
        md_files = [target]
    elif target.is_dir():
        md_files = [p for p in target.rglob("*.md") if not p.name.startswith(".")]
    else:
        return {"success": False, "error": f"Path not found: {study_dir_or_file}"}

    total_diagrams = 0
    valid_diagrams = 0
    all_issues: List[Dict[str, Any]] = []
    fixed_files = 0

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        blocks = extract_mermaid_blocks(content)
        if not blocks:
            continue

        modified = False
        new_content = content

        for start_pos, end_pos, block_code in blocks:
            total_diagrams += 1
            issues = lint_mermaid_code(block_code)
            if not issues:
                valid_diagrams += 1
            else:
                for iss in issues:
                    all_issues.append({
                        "file": str(md_file),
                        "line": iss.line_num,
                        "rule": iss.rule,
                        "message": iss.message,
                        "raw": iss.raw_line
                    })

                if fix:
                    repaired_block = repair_mermaid_code(block_code)
                    if repaired_block != block_code:
                        new_content = new_content.replace(f"```mermaid\n{block_code}```", f"```mermaid\n{repaired_block}\n```")
                        modified = True

        if fix and modified:
            md_file.write_text(new_content, encoding="utf-8")
            fixed_files += 1

    return {
        "success": len(all_issues) == 0,
        "files_scanned": len(md_files),
        "total_diagrams": total_diagrams,
        "valid_diagrams": valid_diagrams,
        "issues_count": len(all_issues),
        "issues": all_issues,
        "fixed_files": fixed_files
    }
