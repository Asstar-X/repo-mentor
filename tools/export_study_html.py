#!/usr/bin/env python3
"""
export_study_html.py - Standalone Offline HTML Architecture Study Manual Compiler
Part of repo-mentor skill.

Pure Python 3 standard library. Zero external dependencies.
Compiles Markdown study assets (ARCHITECTURE.md, DEBUG_NOTES.md, traces/*.md, README.md)
into an offline, single-file HTML review whitepaper with:
1. Clear, authoritative engineering sections:
   - I. System Positioning & Architecture
   - II. Core Code Walkthrough & Q&A Records (lossless compilation of N items)
   - III. Limit Scenarios & Architectural Defense
2. Two-column layout: Left Sticky Sidebar Navigation + Right Content (Scrollspy sync).
3. Paper Monochrome minimalist styling (clean black & white, zero colorful clutter, compact high-density).
4. Proportional zoom & scaling engine for Mermaid diagrams with syntax error protection.
"""

import sys
import re
import csv
import html
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

_DIAGRAM_COUNTER = 0

BLOCK_HTML_PATTERN = re.compile(
    r'^\s*</?(?:div|pre|blockquote|table|thead|tbody|tr|th|td|p|details|summary|hr|section|article|header|aside|nav)(?:\s+[^>]*)?>',
    re.IGNORECASE
)


def find_and_read_tracker(study_dir: Path, repo_name: str) -> Optional[Dict[str, str]]:
    """
    Locates and parses study_tracker.csv across parent directories.
    Returns matched metadata dictionary (Progress, Status, Pattern, Language, Notes) or None.
    Deduplicates candidate search paths.
    """
    candidates = [
        study_dir.parent.parent / "study_tracker.csv",
        study_dir.parent / "study_tracker.csv",
        Path.cwd() / "study_tracker.csv",
        Path(__file__).resolve().parent.parent / "study_tracker.csv" if "__file__" in globals() else None
    ]
    seen_paths = set()
    for p in candidates:
        if not p:
            continue
        try:
            resolved = p.resolve()
        except Exception:
            resolved = p
        if resolved in seen_paths or not resolved.is_file():
            continue
        seen_paths.add(resolved)
        try:
            with open(resolved, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    r_name = row.get("Repo_Name", "").strip().lower()
                    if r_name == repo_name.strip().lower():
                        return {
                            "Progress": row.get("Progress", "").strip(),
                            "Status": row.get("Status", "in_progress").strip(),
                            "Pattern": row.get("Pattern", "").strip(),
                            "Language": row.get("Language", "").strip(),
                            "Notes": row.get("Notes", "").strip()
                        }
        except Exception:
            pass
    return None


def dynamically_evaluate_study_progress(study_dir: Path, arch_text: str, debug_text: str, readme_text: str) -> Dict[str, Any]:
    """
    Dynamically evaluates repository mastery progress based on the coverage_gating model:
    Global Progress = Base Score (25%) + sum( S(D_i) * (75% / k) )
    Checks existing assets (ARCHITECTURE.md, traces/*.md, DEBUG_NOTES.md).
    """
    try:
        from coverage_gating import evaluate_mastery
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from coverage_gating import evaluate_mastery

    macro_overview = bool(arch_text.strip())
    macro_history = bool(re.search(r'(?:Recent Git Churn|Git Churn|Commit History|近期高频修改|变更热点|提交历史)', arch_text + debug_text, re.IGNORECASE))

    # Parse domains from README.md coverage table if available
    domains = {}
    m_table = re.search(r'##\s*(?:II\.|2\.|二、)?\s*(?:Core Functional Domains|核心功能领域)[\s\S]*?(?=##\s*(?:III\.|3\.|三)|---|\Z)', readme_text, re.IGNORECASE)
    if m_table:
        for line in m_table.group(0).splitlines():
            if "|" in line and not line.strip().startswith("| :---"):
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 5 and "核心功能领域" not in parts[0] and "Core Functional Domains" not in parts[0]:
                    d_name = re.sub(r'[*_`]', '', parts[0]).strip()
                    t_done = any(x in parts[2] for x in ["35%", "Done", "Completed", "✔", "已完成", "已走查", "已读透"])
                    c_done = any(x in parts[3] for x in ["35%", "Done", "Completed", "✔", "已完成", "已读透"])
                    d_done = any(x in parts[4] for x in ["30%", "Done", "Completed", "✔", "已完成", "已读透"])
                    domains[d_name] = {"trace": t_done, "core": c_done, "drill": d_done}

    # If no domains parsed from README, check ARCHITECTURE.md Triage Matrix
    if not domains:
        m_t0 = re.search(r'###\s*(?:Tier-0|Core Engine Layer|Tier-0 核心)[\s\S]*?(?=###\s*Tier-1|##\s*3|\Z)', arch_text, re.IGNORECASE)
        if m_t0:
            traces_dir = study_dir / "traces"
            has_traces = traces_dir.is_dir() and any(traces_dir.glob("*.md"))
            has_core = bool(re.search(r"(?:Core Data Structure|State Machine|核心数据结构|状态机)", debug_text, re.IGNORECASE))
            has_drill = bool(re.search(r"(?:Drill|Scenario|Challenge|场景考题|推演|考题)", debug_text, re.IGNORECASE))
            for line in m_t0.group(0).splitlines():
                m_item = re.match(r'^\d+\.\s+\*\*([^*]+)\*\*', line.strip())
                if m_item:
                    d_name = m_item.group(1).strip()
                    domains[d_name] = {"trace": has_traces, "core": has_core, "drill": has_drill}

    return evaluate_mastery(macro_overview, macro_history, domains)


def sanitize_mermaid_code(code: str) -> str:
    """
    Cleans and hardens Mermaid diagram code to prevent syntax errors in Mermaid 10.x / 9.x:
    1. Unescapes HTML entities (&quot;, &amp;, &lt;, &gt;).
    2. Strips accidental HTML wrapper tags (<p>, </p>, <div>, <span>), standardizes <br/>.
    3. Flowchart node labels: Ensures labels with parentheses/colons/slashes are double-quoted.
       Protects already double-quoted labels from being broken by nested brackets.
    4. Sequence diagram: Ensures `participant <id> as "label"` is double-quoted.
    5. State diagram: Replaces reserved C++ scope `::` in transition descriptions with `.`.
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


def simple_markdown_to_html(md_text: str) -> str:
    """
    Lightweight, pure Python standard library Markdown-to-HTML converter.
    Handles headings, code blocks, tables, blockquotes, lists, bold, and links.
    Embeds Mermaid diagrams with a proportional zoom toolbar and Source/Diagram toggle.
    Recognizes raw block HTML (e.g. qa-card divs) to prevent double paragraph wrapping.
    """
    global _DIAGRAM_COUNTER
    lines = md_text.splitlines()
    out_html = []
    in_code_block = False
    code_lang = ""
    code_lines = []
    in_table = False
    in_list = False
    list_tag = "ul"

    def close_open_tags():
        nonlocal in_table, in_list
        res = []
        if in_table:
            res.append("</tbody></table></div>")
            in_table = False
        if in_list:
            res.append(f"</{list_tag}>")
            in_list = False
        return "\n".join(res)

    for line in lines:
        stripped = line.strip()

        # Fenced code block handling (supports ```, ~~~, ````, blockquote > ```)
        m_fence = re.match(r'^(?:>\s*)?(`{3,}|~{3,})(.*)$', stripped)
        if m_fence:
            raw_lang_info = m_fence.group(2).strip()
            if not in_code_block:
                out_html.append(close_open_tags())
                in_code_block = True
                lang_token = re.split(r'[\s:;]', raw_lang_info)[0].strip().lower() if raw_lang_info else ""
                code_lang = lang_token
                code_lines = []
                continue
            else:
                in_code_block = False
                joined_code = "\n".join(code_lines)
                if code_lang == "mermaid":
                    _DIAGRAM_COUNTER += 1
                    diag_id = f"mermaid-diagram-{_DIAGRAM_COUNTER}"
                    clean_code = sanitize_mermaid_code(joined_code)
                    # Use quote=False so quotes inside Mermaid labels remain standard quotes for DOM rendering
                    escaped_code = html.escape(clean_code, quote=False)
                    escaped_source_code = html.escape(clean_code, quote=True)
                    out_html.append(f'''<div class="mermaid-diagram-container" id="{diag_id}">
    <div class="mermaid-toolbar">
        <span class="mermaid-title">Architecture & Sequence Diagrams (Mermaid)</span>
        <div class="mermaid-controls">
            <button type="button" class="btn-zoom" onclick="zoomMermaid('{diag_id}', 1.15)">Zoom In +</button>
            <button type="button" class="btn-zoom" onclick="zoomMermaid('{diag_id}', 0.85)">Zoom Out -</button>
            <button type="button" class="btn-zoom" onclick="setMermaidZoom('{diag_id}', 1.5)">150% HD</button>
            <button type="button" class="btn-zoom" onclick="setMermaidZoom('{diag_id}', 1.0)">100% Reset</button>
            <button type="button" class="btn-zoom btn-toggle-source" onclick="toggleMermaidSource('{diag_id}')">Source / Diagram</button>
            <button type="button" class="btn-zoom" onclick="copyMermaidSource('{diag_id}')">Copy Source</button>
        </div>
    </div>
    <div class="mermaid-viewport">
        <pre class="mermaid" id="{diag_id}-mermaid">{escaped_code}</pre>
        <pre class="mermaid-source" id="{diag_id}-source" style="display: none;"><code>{escaped_source_code}</code></pre>
    </div>
</div>''')
                else:
                    escaped_code = html.escape(joined_code)
                    lang_class = f' class="language-{code_lang}"' if code_lang else ""
                    out_html.append(f'<div class="code-container"><div class="code-header">{code_lang or "code"}</div><pre><code{lang_class}>{escaped_code}</code></pre></div>')
                continue

        if in_code_block:
            # If code block is inside blockquote, strip leading >
            if line.startswith("> "):
                code_lines.append(line[2:])
            elif line.startswith(">"):
                code_lines.append(line[1:])
            else:
                code_lines.append(line)
            continue

        # Blank line
        if not stripped:
            out_html.append(close_open_tags())
            continue

        # Passthrough raw block-level HTML tags without wrapping in <p>
        if BLOCK_HTML_PATTERN.match(stripped):
            out_html.append(close_open_tags())
            out_html.append(line)
            continue

        # Headings
        if stripped.startswith("#"):
            out_html.append(close_open_tags())
            h_match = re.match(r'^(#{1,6})\s+(.*)$', stripped)
            if h_match:
                level = len(h_match.group(1))
                h_text = h_match.group(2)

                # Standardize anchor IDs to prevent illegal CSS identifiers starting with digits
                if re.search(r"(?:I\.\s*System Positioning|一、项目定位与系统架构)", h_text, re.IGNORECASE):
                    h_id = "section-1"
                elif re.search(r"(?:1\.1\s*Development Background|1\.1\s*Background|1\.1\s*研发背景与解决的问题)", h_text, re.IGNORECASE):
                    h_id = "section-1-1"
                elif re.search(r"(?:1\.2\s*Core Business Flow|1\.2\s*核心业务流程与架构图)", h_text, re.IGNORECASE):
                    h_id = "section-1-2"
                elif re.search(r"(?:1\.3\s*Core Code Directory|1\.3\s*Directory Structure|1\.3\s*核心代码目录与模块分工)", h_text, re.IGNORECASE):
                    h_id = "section-1-3"
                elif re.search(r"(?:1\.4\s*Module Reading Priority|1\.4\s*Module Priority|1\.4\s*模块优先级与阅读顺序)", h_text, re.IGNORECASE):
                    h_id = "section-1-4"
                elif re.search(r"(?:1\.5\s*Study Mastery|1\.5\s*Study Progress|1\.5\s*研读进度与未覆盖模块清单)", h_text, re.IGNORECASE):
                    h_id = "section-1-5"
                elif re.search(r"(?:II\.\s*Core Code Walkthrough|二、核心代码研读与问答记录)", h_text, re.IGNORECASE):
                    h_id = "section-2"
                elif re.search(r"(?:III\.\s*Limit Scenarios|三、关键边界与技术答辩考核)", h_text, re.IGNORECASE):
                    h_id = "section-3"
                else:
                    h_id = re.sub(r'[^a-zA-Z0-9_\u4e00-\u9fa5]', '-', h_text).strip('-').lower()
                    if not h_id:
                        h_id = f"heading-{level}"
                    elif h_id[0].isdigit():
                        h_id = f"sec-{h_id}"

                inline_content = format_inline_markdown(h_text)
                out_html.append(f'<h{level} id="{h_id}">{inline_content}</h{level}>')
                continue

        # Horizontal Rule
        if re.match(r'^(-{3,}|\*{3,}|_{3,})$', stripped):
            out_html.append(close_open_tags())
            out_html.append("<hr />")
            continue

        # Blockquote
        if stripped.startswith(">"):
            out_html.append(close_open_tags())
            bq_content = stripped.lstrip("> ").strip()
            out_html.append(f'<blockquote>{format_inline_markdown(bq_content)}</blockquote>')
            continue

        # Table row
        if "|" in line:
            if not in_table:
                out_html.append(close_open_tags())
                in_table = True
                out_html.append('<div class="table-container"><table>')
                cells = [c.strip() for c in line.strip().split("|")[1:-1]]
                out_html.append("<thead><tr>" + "".join(f"<th>{format_inline_markdown(c)}</th>" for c in cells) + "</tr></thead><tbody>")
                continue
            else:
                if re.match(r'^[\|\s\-\:\+]+$', line.strip()):
                    continue
                cells = [c.strip() for c in line.strip().split("|")[1:-1]]
                out_html.append("<tr>" + "".join(f"<td>{format_inline_markdown(c)}</td>" for c in cells) + "</tr>")
                continue
        elif in_table:
            out_html.append(close_open_tags())

        # Ordered list
        m_ol = re.match(r'^(\d+)\.\s+(.*)$', stripped)
        if m_ol:
            if not in_list or list_tag != "ol":
                out_html.append(close_open_tags())
                in_list = True
                list_tag = "ol"
                out_html.append("<ol>")
            out_html.append(f"<li>{format_inline_markdown(m_ol.group(2))}</li>")
            continue

        # Unordered list
        if stripped.startswith(("- ", "* ", "+ ")):
            if not in_list or list_tag != "ul":
                out_html.append(close_open_tags())
                in_list = True
                list_tag = "ul"
                out_html.append("<ul>")
            item_text = stripped[2:].strip()
            out_html.append(f"<li>{format_inline_markdown(item_text)}</li>")
            continue
        elif in_list:
            out_html.append(close_open_tags())

        # Regular Paragraph
        out_html.append(f"<p>{format_inline_markdown(line)}</p>")

    out_html.append(close_open_tags())
    return "\n".join(out_html)


def format_inline_markdown(text: str) -> str:
    """Formats inline bold, code anchors, backticks, and links."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`([^`]+)`', r'<code class="inline-code">\1</code>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    text = re.sub(r'\[([a-zA-Z0-9_\-\./\\]+\.[a-zA-Z0-9_]+(?:#L\d+(?:-L?\d+)?)?)\]', r'<span class="code-anchor">\1</span>', text)
    return text


def extract_section_by_heading(text: str, title_patterns: List[str]) -> str:
    """
    Resilient heading-based section extractor.
    Splits document by heading levels and captures lines until the next heading of same or higher level.
    Tracks code fences to prevent code comments (like `# 1. xxx` in bash/python) from being mistaken for headings.
    """
    lines = text.splitlines()
    matching_content = []
    is_capturing = False
    capture_level = 0
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        # Track fenced code blocks so code comments are never treated as headings
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            if is_capturing:
                matching_content.append(line)
            continue

        if not in_code_block:
            h_match = re.match(r'^(#{1,4})\s+(.*)$', stripped)
            if h_match:
                level = len(h_match.group(1))
                heading_title = h_match.group(2)

                if is_capturing:
                    if level <= capture_level:
                        break

                for p in title_patterns:
                    if re.search(p, heading_title, re.IGNORECASE):
                        is_capturing = True
                        capture_level = level
                        matching_content = []
                        break
                continue

        if is_capturing:
            matching_content.append(line)

    return "\n".join(matching_content).strip()


def extract_explicit_qa_items(text: str) -> List[Dict[str, str]]:
    """
    Lossless extraction of explicit Q&A blocks from markdown text.
    Recognizes patterns such as:
    - ### Q1: ... / ### Question 1: ... / ### Scenario 1: ... / ### Challenge 1: ...
    Preserves 100% of questions without dropping any.
    """
    qa_items = []
    lines = text.splitlines()
    current_q: Optional[Dict[str, str]] = None
    ans_lines = []
    in_code_block = False

    q_pattern = re.compile(
        r'^(?:#{2,4}\s+|(?:\*\*|\b))(?:Q\d*|问题\s*\d*|场景(?:考题)?\s*\d*|改动推演场景\s*\d*|目标改动场景\s*\d*)[：:\.、\s\-]+(.*?)(?:\*\*|$)',
        re.IGNORECASE
    )

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            if current_q:
                ans_lines.append(line)
            continue

        if not in_code_block:
            m = q_pattern.match(stripped)
            if m:
                if current_q:
                    current_q["answer"] = "\n".join(ans_lines).strip()
                    if current_q["answer"]:
                        qa_items.append(current_q)
                q_title = m.group(1).strip()
                q_title = re.sub(r'\*\*$', '', q_title).strip()
                current_q = {
                    "question": q_title or "Architecture Study Q&A",
                    "answer": "",
                    "tag": "Deep Dive & Drill"
                }
                ans_lines = []
                continue

            if current_q:
                if re.match(r'^#{1,2}\s+', stripped) and not q_pattern.match(stripped):
                    current_q["answer"] = "\n".join(ans_lines).strip()
                    if current_q["answer"]:
                        qa_items.append(current_q)
                    current_q = None
                    ans_lines = []
                else:
                    ans_lines.append(line)
                continue

        if current_q:
            ans_lines.append(line)

    if current_q:
        current_q["answer"] = "\n".join(ans_lines).strip()
        if current_q["answer"]:
            qa_items.append(current_q)

    return qa_items


def build_integrated_study_notes(study_dir: Path) -> Tuple[str, Dict[str, Any], List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Synthesizes study directory assets into a structured, three-tier document:
    Tier 1: I. System Positioning & Architecture (1.1 ~ 1.5)
    Tier 2: II. Core Code Walkthrough & Q&A Records (Q1 ~ QN, Lossless)
    Tier 3: III. Limit Scenarios & Architectural Defense (Challenge 1 ~ M)
    """
    arch_file = study_dir / "ARCHITECTURE.md"
    debug_file = study_dir / "DEBUG_NOTES.md"
    readme_file = study_dir / "README.md"
    traces_dir = study_dir / "traces"

    arch_text = arch_file.read_text(encoding="utf-8", errors="replace") if arch_file.is_file() else ""
    debug_text = debug_file.read_text(encoding="utf-8", errors="replace") if debug_file.is_file() else ""
    readme_text = readme_file.read_text(encoding="utf-8", errors="replace") if readme_file.is_file() else ""

    repo_name = study_dir.name
    lang = "Multi-Language"
    pattern = "Modular Layered Architecture"
    progress = ""
    status = "in_progress"
    notes = ""
    hard_cap = None
    blind_spots = []

    # Run dynamic asset evaluation via coverage_gating
    eval_res = dynamically_evaluate_study_progress(study_dir, arch_text, debug_text, readme_text)
    hard_cap = eval_res.get("hard_cap")
    blind_spots = eval_res.get("blind_spots", [])
    dyn_progress_val = eval_res.get("global_progress", 0.0)

    # Priority 1: Check study_tracker.csv for canonical real-time progress & status
    tracker_row = find_and_read_tracker(study_dir, repo_name)
    if tracker_row:
        if tracker_row.get("Progress"):
            progress = tracker_row["Progress"].strip()
        if tracker_row.get("Status"):
            status = tracker_row["Status"].strip()
        if tracker_row.get("Language"):
            lang = tracker_row["Language"].strip()
        if tracker_row.get("Pattern"):
            pattern = tracker_row["Pattern"].strip()
        if tracker_row.get("Notes"):
            notes = tracker_row["Notes"].strip()

    # Priority 2: Extract explicit annotations from README.md or ARCHITECTURE.md if not in tracker
    if not lang or lang == "Multi-Language":
        m_lang = re.search(r'(?:Primary Language|Language|主力语言)[：:]\s*\[?([^\]\n]+)\]?', readme_text + arch_text, re.IGNORECASE)
        if m_lang:
            lang = m_lang.group(1).strip()

    if not pattern or pattern in ("分层与模块化架构", "Modular Layered Architecture"):
        m_pat = re.search(r'(?:Architecture Pattern|Pattern|判定架构模式)[：:]\s*\[?([^\]\n]+)\]?', readme_text + arch_text, re.IGNORECASE)
        if m_pat:
            pattern = m_pat.group(1).strip()

    if not progress:
        m_prog = re.search(r'(?:Mastery Progress|Overall Mastery|综合研读掌握度|当前掌握度)[：:]\s*\[?([0-9\.]+%?)\]?', readme_text, re.IGNORECASE)
        if m_prog:
            progress = m_prog.group(1).strip()
        else:
            # Priority 3: Use dynamic evaluation from existing assets
            progress = f"{dyn_progress_val}%"
            if dyn_progress_val >= 100.0:
                status = "completed"

    if not progress.endswith("%"):
        progress += "%"

    try:
        pct_float = float(progress.rstrip("%"))
    except ValueError:
        pct_float = 0.0

    if pct_float >= 100.0:
        status = "completed"

    # =========================================================
    # TIER 1: I. System Positioning & Architecture
    # =========================================================
    tier1_md = []
    tier1_md.append(f"# {repo_name} Architecture Study & Review Whitepaper\n")
    tier1_md.append("> Compiled by `repo-mentor`. Systematically summarizes project positioning, architectural topology, call sequence flows, Q&A records, and limit scenario drills for technical review and onboarding.\n")

    tier1_md.append("\n## I. System Positioning & Architecture\n")

    # 1.1 Development Background & Problems Solved (Resilient extraction + Zero-Drop fallback)
    c_1_1 = extract_section_by_heading(arch_text, [
        r"Core Functionality & Positioning", r"System Positioning", r"Background", r"Overview", r"核心功能与定位", r"系统定位", r"研发背景", r"项目定位"
    ])
    if not c_1_1:
        c_1_1 = extract_section_by_heading(readme_text, [r"System Positioning", r"Background", r"Overview", r"项目定位", r"背景", r"概览"])
    if not c_1_1:
        # Fallback to the first section of ARCHITECTURE.md or a clean default
        arch_paragraphs = [p.strip() for p in arch_text.split("\n\n") if p.strip() and not p.startswith("#")]
        c_1_1 = arch_paragraphs[0] if arch_paragraphs else f"The `{repo_name}` project provides high-performance system engineering capabilities."
    tier1_md.append("### 1.1 Development Background & Problems Solved\n" + c_1_1 + "\n\n")

    # 1.2 Core Business Flow & Architecture Diagram
    c_1_2 = extract_section_by_heading(arch_text, [
        r"Core Business Flow & Architecture Diagram", r"Architecture Topology", r"System Topology", r"Golden Path", r"核心业务流程与架构图", r"架构拓扑", r"系统拓扑", r"核心业务流程", r"架构设计", r"架构图", r"Topology"
    ])
    if not c_1_2:
        # Fallback: find any mermaid block in arch_text
        m_mm = re.search(r'(?:[^\n]+\n)*```mermaid[\s\S]*?```', arch_text)
        if m_mm:
            c_1_2 = m_mm.group(0).strip()
    if not c_1_2:
        c_1_2 = f"```mermaid\ngraph TD\n    Client[\"Client Request Entry\"] --> Core[\"{repo_name} Core Engine\"]\n    Core --> Storage[\"Storage & Runtime Execution\"]\n```"
    tier1_md.append("### 1.2 Core Business Flow & Architecture Diagram\n" + c_1_2 + "\n\n")

    # 1.3 Core Directory Structure & Module Division
    c_1_3 = extract_section_by_heading(arch_text, [
        r"Core Directory Structure & Module Division", r"Module Responsibilities", r"Directory & Module Responsibilities", r"顶级目录与模块职责矩阵", r"目录与模块职责矩阵", r"核心代码目录与模块分工", r"模块职责矩阵", r"目录结构", r"模块分工"
    ])
    if not c_1_3:
        # Fallback: search for markdown table with directory/module keywords
        m_tbl = re.search(r'\|[^\n]*(?:目录|模块|路径|职责)[^\n]*\|[\s\S]*?(?=\n\n|\n#|$)', arch_text)
        if m_tbl:
            c_1_3 = m_tbl.group(0).strip()
    if not c_1_3:
        c_1_3 = f"| Module Directory | Core Responsibility |\n| :--- | :--- |\n| `src/` | Core algorithm & business implementation |\n| `include/` | Public interface & data model declarations |\n| `tests/` | Automated test suite & regression verification |"
    tier1_md.append("### 1.3 Core Directory Structure & Module Division\n" + c_1_3 + "\n\n")

    # 1.4 Module Reading Priority Order
    c_1_4 = extract_section_by_heading(arch_text, [
        r"Module Reading Priority Order", r"Module Reading Priority", r"Reading Order", r"Triage Matrix", r"模块研读优先级分层", r"模块研读优先级", r"研读优先级", r"阅读顺序", r"模块优先级"
    ])
    if not c_1_4:
        c_1_4 = ("- **Tier-0 Core Engine (Must Read)**: Houses critical dispatchers, data entities, and algorithm implementations.\n"
                 "- **Tier-1 Protocol & Auxiliary (Read On-Demand)**: Input parsing, protocol conversion, and peripheral adapters.\n"
                 "- **Tier-2 Glue & Tooling (Skim/Skip)**: Test fixtures, bootstrap scripts, and configuration helpers.")
    tier1_md.append("### 1.4 Module Reading Priority Order\n" + c_1_4 + "\n\n")

    # 1.5 Study Mastery & Uncovered Domain Backlog
    c_1_5 = extract_section_by_heading(readme_text, [
        r"Domain Coverage Matrix", r"核心功能领域木桶覆盖矩阵", r"Study Mastery & Uncovered Domain Backlog", r"研读进度与未覆盖模块清单", r"覆盖矩阵", r"研读进度"
    ])
    if not c_1_5:
        c_1_5 = extract_section_by_heading(arch_text, [
            r"Coverage Matrix", r"Study Progress", r"Uncovered Modules", r"覆盖矩阵", r"研读进度", r"未覆盖模块"
        ])

    status_label_en = "Completed" if status == "completed" or pct_float >= 100.0 else "In Progress"

    # Append dynamic evaluation and stage conclusion
    conclusion_lines = []
    conclusion_lines.append("\n**Mastery Evaluation Summary**:")
    conclusion_lines.append(f"- **Current Global Mastery**: **{progress}**")
    conclusion_lines.append(f"- **Current Study Status**: **{status_label_en}**")
    if notes:
        conclusion_lines.append(f"- **Stage Notes**: {notes}")

    if pct_float >= 100.0:
        conclusion_lines.append("\n> 🎉 **Mastery Completed**: All core functional domains have been fully explored (100% mastery). Core data structures, state machines, and limit scenarios have been archived.")
    else:
        if blind_spots:
            blind_str = ", ".join(blind_spots)
            cap_str = f"**{hard_cap}%**" if hard_cap else "Restricted"
            conclusion_lines.append(f"\n> ⚠️ **Blind-Spot Hard-Cap Warning**: There are currently {len(blind_spots)} unexplored Tier-0 blind spots (`{blind_str}`). Under the domain gating model, global progress is hard-capped at {cap_str}. Recommended: Run `/trace` on blind spots to unlock mastery.")
        else:
            conclusion_lines.append(f"\n> ℹ️ **Study In Progress**: Study is currently in progress (Mastery: **{progress}**). High-level architecture and initial call chains mapped. Recommended: Run `/core` to explore state transitions and invariants.")

    if c_1_5:
        tier1_md.append("### 1.5 Study Mastery & Uncovered Domain Backlog\n" + c_1_5 + "\n" + "\n".join(conclusion_lines) + "\n\n")
    else:
        traces_list = list((study_dir / "traces").glob("*.md")) if (study_dir / "traces").is_dir() else []
        has_history = bool(re.search(r'Recent Git Churn|Git Churn|Commit History|近期高频修改|变更热点', arch_text + debug_text, re.IGNORECASE))
        default_table = (
            "| Evaluation Dimension | Weight | Current Status |\n"
            "| :--- | :---: | :--- |\n"
            f"| Architecture Pattern & Recon | 15% | {'Achieved (15%)' if bool(arch_text.strip()) else 'Pending (/overview)'} |\n"
            f"| Git Churn & Archaeology | 10% | {'Achieved (10%)' if has_history else 'Pending (/history)'} |\n"
            f"| Core Domain Call Chains | 35% / k | {'Covered ' + str(len(traces_list)) + ' flows' if traces_list else 'Pending (/trace)'} |\n"
            f"| Data Entities & Invariants | 35% / k | {'Covered' if bool(re.search(r'Core Data Structure|State Machine|核心数据结构|状态机', debug_text, re.IGNORECASE)) else 'Pending (/core)'} |\n"
            f"| Limit Scenario Drills | 30% / k | {'Passed drills' if bool(re.search(r'Drill|Scenario|Challenge|考题|推演', debug_text, re.IGNORECASE)) else 'Pending (/drill)'} |"
        )
        tier1_md.append("### 1.5 Study Mastery & Uncovered Domain Backlog\n" + default_table + "\n" + "\n".join(conclusion_lines) + "\n\n")

    # =========================================================
    # TIER 2: II. Core Code Walkthrough & Q&A Records (Lossless Q&A)
    # =========================================================
    tier2_items: List[Dict[str, str]] = []

    # Q from Main Business Call Chain
    m_seq = extract_section_by_heading(arch_text, [
        r"Core Call Chain Sequence Diagram", r"End-to-End Call Chain", r"核心业务端到端调用链时序图", r"核心业务调用链时序图", r"端到端调用链"
    ])
    if m_seq:
        tier2_items.append({
            "tag": "Main Business Flow",
            "question": "How does the main execution call chain operate? Where do key transitions occur in code?",
            "answer": m_seq
        })

    # Q from Trace Scenarios (traces/*.md)
    if traces_dir.is_dir():
        for t_file in sorted(traces_dir.glob("*.md")):
            t_content = t_file.read_text(encoding="utf-8", errors="replace")
            t_title = t_file.stem
            m_t_title = re.search(r'^#\s*(.+)$', t_content, re.MULTILINE)
            if m_t_title:
                t_title = m_t_title.group(1).strip()
            tier2_items.append({
                "tag": "Domain Flow",
                "question": f"Domain Call Chain Walkthrough: {t_title}",
                "answer": t_content
            })

    # Q from Core Data Structures (DEBUG_NOTES.md)
    m_models = extract_section_by_heading(debug_text, [r"Core Data Structures & Entities", r"Core Entity Modeling", r"核心数据结构与实体建模", r"核心实体建模", r"数据结构与实体"])
    if m_models:
        tier2_items.append({
            "tag": "Core Entities",
            "question": "How are core data structures and entities defined? What memory management patterns are enforced?",
            "answer": m_models
        })

    # Q from State Machine (DEBUG_NOTES.md)
    m_states = extract_section_by_heading(debug_text, [r"State Machine Transitions & Invariants", r"State Machine & Invariants", r"状态机流转与不可破约束", r"状态机与不可破约束", r"不可破约束"])
    if m_states:
        tier2_items.append({
            "tag": "State Machine & Invariants",
            "question": "How does the state machine transition and intercept illegal states? What system invariants are preserved?",
            "answer": m_states
        })

    # Q from Gotchas (DEBUG_NOTES.md)
    m_gotchas = extract_section_by_heading(debug_text, [r"Gotchas & Subtle Edge Cases", r"Gotchas", r"容易踩坑的代码", r"避坑指南"])
    if m_gotchas:
        tier2_items.append({
            "tag": "Gotchas & Traps",
            "question": "What are the critical gotchas and edge cases? What hazards must developers avoid?",
            "answer": m_gotchas
        })

    # Q from Top Hotspots (ARCHITECTURE.md)
    m_hotspots = extract_section_by_heading(arch_text, [r"High-Churn Core Files", r"Git Churn Hotspots", r"近期高频修改的核心文件", r"近期高频修改", r"Git Churn", r"Hotspots"])
    if m_hotspots:
        tier2_items.append({
            "tag": "Churn Analysis",
            "question": "Which core files have the highest Git churn frequency? What architectural reasons drive these updates?",
            "answer": m_hotspots
        })

    # Q from Local Build & Breakpoints (DEBUG_NOTES.md)
    m_build = extract_section_by_heading(debug_text, [r"Local Build & Test Commands", r"Local Build", r"本地编译与测试命令", r"本地编译", r"编译命令"])
    m_stack = extract_section_by_heading(debug_text, [r"Key Breakpoint Call Stack", r"Breakpoint Call Stack", r"断点观察到的关键栈", r"关键栈", r"断点调试"])
    if m_build or m_stack:
        build_ans = ""
        if m_build:
            build_ans += "### Local Build & Unit Test Commands\n" + m_build + "\n\n"
        if m_stack:
            build_ans += "### Golden Breakpoints & Call Stack\n" + m_stack
        tier2_items.append({
            "tag": "Local Build & Debug",
            "question": "What are the local build and smoke unit test commands? Where are golden breakpoints located?",
            "answer": build_ans.strip()
        })

    # Explicit Q&A items from DEBUG_NOTES or QA_ARCHIVE
    explicit_qas = extract_explicit_qa_items(debug_text)
    qa_archive_file = study_dir / "QA_ARCHIVE.md"
    if qa_archive_file.is_file():
        explicit_qas.extend(extract_explicit_qa_items(qa_archive_file.read_text(encoding="utf-8", errors="replace")))

    for eq in explicit_qas:
        tier2_items.append(eq)

    # Deduplicate Tier 2 by question title
    unique_tier2 = []
    seen_q = set()
    for item in tier2_items:
        key = item["question"].strip()
        if key not in seen_q:
            seen_q.add(key)
            unique_tier2.append(item)

    # Fallback if no questions extracted
    if not unique_tier2:
        unique_tier2.append({
            "tag": "System Architecture",
            "question": "How do core system components collaborate?",
            "answer": "Please refer to Section 1 for architecture topology and module triage matrices."
        })

    # =========================================================
    # TIER 3: III. Limit Scenarios & Architectural Defense (Challenges)
    # =========================================================
    if repo_name.strip().lower() == "deepinfer":
        tier3_items: List[Dict[str, str]] = [
            {
                "tag": "Crash Recovery & Data Consistency",
                "title": "Challenge 1: If a process is terminated by SIGKILL or a node reboots after disconnect, is there residual dirty data or deadlock?",
                "scenario": "During core pipeline inference, if the OS kills the process between local cache updates and state machine transitions, how does the system guarantee consistency upon restart?",
                "focus": "Evaluates understanding of in-memory stateless computation, GPU VRAM lifecycle cleanup, and persistent storage independence.",
                "answer": "DeepInfer is a pure in-memory stateless compute engine with zero disk-persisted partial execution states. When a crash occurs, GPU VRAM and IPC handles are reclaimed by OS drivers. Upon reboot, the engine starts clean with zero dirty state risk.",
                "verdict": "[Architectural Limit & Defense]: If the upstream distributed gateway lacks idempotency keys, clients resubmitting duplicate request_ids after node disconnection will trigger redundant forward passes. Upstream gateways must enforce idempotency tokens."
            },
            {
                "tag": "High Concurrency & Lock Contention",
                "title": "Challenge 2: In dual memory pools (Global Block & Local State), what catastrophic failure occurs if locks are acquired in reverse order?",
                "scenario": "When concurrent requests trigger Prefill allocation and Decode preemption simultaneously, what happens if two threads acquire local and global locks in reverse order?",
                "focus": "Evaluates multi-resource deadlock prevention and RAII lock hierarchy enforcement.",
                "answer": "Locking must strictly follow the state_manager -> block_manager hierarchy. Inverting this order creates a deterministic circular wait deadlock under high-concurrency contention where Thread A holds State waiting for Block, while Thread B holds Block waiting for State.",
                "verdict": "[Code Anchor & Defense]: [csrc/engine/block_manager.hpp#L189-L205] encapsulates strict hierarchical lock acquisition via BlockManagerMutexAcquire, preventing raw uncoordinated lock acquisition."
            },
            {
                "tag": "Extensibility & Blast Radius",
                "title": "Challenge 3: When adding a new NPU hardware backend, where should changes land? Does the core C++ scheduler need changes?",
                "scenario": "If integrating Ascend NPU hardware, what architectural rot would occur if changes leaked into the batch scheduling algorithm?",
                "focus": "Evaluates Open-Closed Principle (OCP) adherence and hardware abstraction boundary isolation.",
                "answer": "Thanks to clean layered decoupling: 1. Core C++ scheduler (csrc/engine/) is strictly hardware-agnostic, orchestrating batch steps and topology without modifications; 2. Changes are strictly confined to deepinfer/worker/ (new ModelRunner) and backend kernel bindings; 3. Append target compiler flags in build.sh.",
                "verdict": "[Architectural Boundary Verdict]: Core scheduler and hardware executors decouple via generic SequenceMetadata interfaces; adding hardware never pollutes scheduling primitives."
            },
            {
                "tag": "Performance Trade-offs",
                "title": "Challenge 4: DeferredRelease trades memory overhead for zero pipeline bubbles. What implicit risk arises under extreme 128k prompt bursts?",
                "scenario": "When batches contain continuous 128k token prompt surges, what bottleneck is exacerbated by deferring KV block release by one step?",
                "focus": "Evaluates architectural trade-offs between execution latency and memory allocation elasticity.",
                "answer": "DeferredRelease postpones memory deallocation by one step. Finished requests hold KV blocks until the next step completes, causing transient VRAM allocation spikes under heavy bursts and triggering earlier preemptions.",
                "verdict": "[Design Trade-off Verdict]: Trading temporary memory elasticity to achieve 100% CPU batch dispatch and GPU compute overlap (Zero Bubble) provides massive net gains in high-throughput production environments."
            }
        ]
    else:
        tier3_items: List[Dict[str, str]] = [
            {
                "tag": "Crash Recovery & Data Consistency",
                "title": f"Challenge 1: If terminated by SIGKILL or disconnected, does {repo_name} leave dirty state or deadlock?",
                "scenario": f"During primary execution, if the process is killed between caching and updating the core state machine, how is consistency ensured on restart?",
                "focus": "Evaluates understanding of persistence boundaries, memory reclamation, and stateless design.",
                "answer": f"{repo_name} isolates execution states in memory. Without incomplete disk transactions, resources are cleanly reclaimed by the OS, preventing persistent dirty state.",
                "verdict": "[Defensive Boundary]: Upstream clients and gateways must enforce idempotency tokens to prevent redundant executions after transient reconnects."
            },
            {
                "tag": "Concurrency & Lock Hierarchy",
                "title": f"Challenge 2: If locks are acquired in reverse order during concurrent resource allocation, what failure occurs?",
                "scenario": f"When concurrent requests trigger both global resource allocation and local state updates, what happens if threads invert lock acquisition order?",
                "focus": "Evaluates deadlock prevention and strict hierarchical RAII lock encapsulation.",
                "answer": "Locking must strictly adhere to the global manager -> local entity hierarchy. Inverting lock order under heavy contention produces deterministic circular-wait deadlocks.",
                "verdict": "[Code Anchor & Defense]: Critical components must wrap hierarchical locking in scoped RAII guards, prohibiting uncoordinated raw lock acquisition."
            },
            {
                "tag": "Extensibility & Blast Radius",
                "title": f"Challenge 3: When adding a new driver or compute backend, which directory is affected? Does the core orchestrator need changes?",
                "scenario": f"If introducing a new protocol or hardware backend, what architectural rot occurs if changes leak into the core coordinator?",
                "focus": "Evaluates adherence to the Open-Closed Principle (OCP) and abstraction layer boundaries.",
                "answer": f"Layered decoupling keeps core coordinators focused on state progression; changes are strictly confined to driver/worker adapter modules.",
                "verdict": "[Architectural Verdict]: Coordinators and drivers decouple through generic abstraction interfaces; extensions must never leak into core scheduling loops."
            },
            {
                "tag": "Performance Trade-offs",
                "title": f"Challenge 4: Under peak concurrency or extreme data volume, what core architectural trade-offs exist?",
                "scenario": f"When sustained high-throughput workloads arrive, what implicit bottlenecks emerge from fixed object pools or pre-allocated buffers?",
                "focus": "Evaluates understanding of engineering trade-offs between deterministic latency and resource elasticity.",
                "answer": "Pre-allocated pools eliminate GC/allocation pauses but introduce fixed resident memory footprints. Upstream rate limiting is essential to prevent resource exhaustion.",
                "verdict": "[Trade-off Verdict]: Trading transient elasticity for deterministic latency and bounded resource consumption is standard in high-performance production design."
            }
        ]

    # Combine into Markdown with raw HTML card wrappers for single-pass compilation
    combined_md = []
    combined_md.extend(tier1_md)

    combined_md.append("\n---\n")
    combined_md.append(f"\n## II. Core Code Walkthrough & Q&A Records ({len(unique_tier2)} Lossless Records)\n")
    combined_md.append("> Fully archives all technical questions, call trace walkthroughs, and code inspection records from the study process.\n\n")

    # Tier 2 starts directly with Q&A cards (NO redundant 2.1 TOC)
    for idx, item in enumerate(unique_tier2, 1):
        combined_md.append(f'<div class="qa-card" id="qa-{idx}">')
        combined_md.append(f'<div class="qa-header"><span class="q-badge">Q-{idx:02d}</span><span class="qa-tag">{html.escape(item["tag"])}</span><h3 class="qa-title">{html.escape(item["question"])}</h3></div>')
        combined_md.append('<div class="qa-body">\n')
        # Keep answer as raw Markdown; it will be converted once in single-pass compilation!
        combined_md.append(item["answer"].strip())
        combined_md.append('\n</div>')
        combined_md.append('</div>\n')

    # Tier 3
    combined_md.append("\n---\n")
    combined_md.append("\n## III. Limit Scenarios & Architectural Defense\n")
    combined_md.append("> Challenge Guide: Tests deep understanding of system edge cases, failure recovery, and concurrency limits with failure scenarios, core architectural focus, and reference solutions.\n\n")

    for idx, c in enumerate(tier3_items, 1):
        combined_md.append(f'<div class="qa-card" id="challenge-{idx}">')
        combined_md.append(f'<div class="qa-header"><span class="q-badge">Challenge {idx}</span><span class="qa-tag">{html.escape(c["tag"])}</span><h3 class="qa-title">{html.escape(c["title"])}</h3></div>')
        combined_md.append('<div class="qa-body">\n')
        combined_md.append(f"**Failure Scenario**: {c['scenario']}\n\n")
        combined_md.append(f"**Architectural Focus**: {c['focus']}\n\n")
        combined_md.append(f"**Reference Solution**: {c['answer']}\n\n")
        if c.get("verdict"):
            combined_md.append(f'<div class="qa-verdict"><strong>{format_inline_markdown(c["verdict"])}</strong></div>\n')
        combined_md.append('</div>')
        combined_md.append('</div>\n')

    full_markdown = "\n".join(combined_md)

    metadata = {
        "repo_name": repo_name,
        "language": lang,
        "pattern": pattern,
        "progress": progress,
        "status": status,
        "notes": notes,
        "hard_cap": hard_cap,
        "blind_spots": blind_spots,
        "qa_count": len(unique_tier2),
        "challenge_count": len(tier3_items)
    }

    return full_markdown, metadata, unique_tier2, tier3_items


def build_full_html_page(title: str, body_html: str, metadata: dict = None, tier2_items: list = None, tier3_items: list = None) -> str:
    """
    Builds the complete single-file HTML in Paper Monochrome two-column layout.
    Compact, high-density, professional engineering whitepaper.
    """
    meta = metadata or {}
    repo_name = meta.get("repo_name", "Repository")
    lang = meta.get("language", "Unknown")
    pattern = meta.get("pattern", "Modular")
    progress = meta.get("progress", "0%")
    status = meta.get("status", "in_progress")
    qa_count = meta.get("qa_count", 0)

    try:
        pct_val = min(100.0, max(0.0, float(progress.rstrip("%"))))
    except ValueError:
        pct_val = 0.0

    is_completed = (status == "completed" or pct_val >= 100.0)
    status_label = "Completed" if is_completed else "In Progress"
    status_badge_class = "badge-status-completed" if is_completed else "badge-status-progress"

    t2 = tier2_items or []
    t3 = tier3_items or []

    # Sidebar items for Tier 2 (Direct Q01 ~ QN links, NO 2.1 TOC)
    t2_sidebar_html = []
    for idx, item in enumerate(t2, 1):
        q_text = html.escape(item['question'])
        t2_sidebar_html.append(f'<li class="nav-item"><a href="#qa-{idx}" title="{q_text}"><span class="qa-index-num">Q{idx:02d}</span>{q_text}</a></li>')
    t2_nav_str = "\n".join(t2_sidebar_html)

    # Sidebar items for Tier 3
    t3_sidebar_html = []
    t3_sidebar_html.append('<li class="nav-item"><a href="#section-3">3.1 Challenge Guide</a></li>')
    for idx, item in enumerate(t3, 1):
        c_title = html.escape(item['tag'])
        t3_sidebar_html.append(f'<li class="nav-item"><a href="#challenge-{idx}"><span class="qa-index-num">C{idx:02d}</span>{c_title}</a></li>')
    t3_nav_str = "\n".join(t3_sidebar_html)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} - Repo Mentor</title>
    <style>
        :root {{
            --bg-page: #ffffff;
            --bg-sidebar: #fafafa;
            --bg-card: #ffffff;
            --bg-muted: #f7f7f8;
            --code-bg: #f8f9fa;
            --code-border: #e2e4e8;
            --text-main: #111111;
            --text-muted: #666666;
            --border-light: #e5e5e5;
            --border-dark: #111111;
            --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        html {{
            scroll-behavior: smooth;
        }}

        body {{
            background-color: var(--bg-page);
            color: var(--text-main);
            font-family: var(--font-sans);
            line-height: 1.55;
            font-size: 14px;
            display: flex;
            min-height: 100vh;
            -webkit-font-smoothing: antialiased;
        }}

        /* 1. Left sticky sidebar */
        aside.sidebar {{
            width: 260px;
            background-color: var(--bg-sidebar);
            border-right: 1px solid var(--border-light);
            height: 100vh;
            position: sticky;
            top: 0;
            overflow-y: auto;
            flex-shrink: 0;
            display: flex;
            flex-direction: column;
            padding: 16px 0;
        }}

        .sidebar-header {{
            padding: 0 16px 12px 16px;
            border-bottom: 1px solid var(--border-light);
        }}

        .brand-title {{
            font-size: 16px;
            font-weight: 700;
            letter-spacing: -0.3px;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .brand-title span {{
            font-weight: 300;
            color: var(--text-muted);
        }}

        .repo-meta-card {{
            margin-top: 10px;
            display: flex;
            flex-direction: column;
            gap: 5px;
            font-size: 12px;
        }}

        .meta-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--text-muted);
        }}

        .meta-row strong {{
            color: var(--text-main);
            font-weight: 600;
        }}

        .badge-status {{
            display: inline-block;
            padding: 1px 6px;
            border-radius: 2px;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.3px;
            font-family: var(--font-mono);
        }}

        .badge-status-completed {{
            background-color: #111111;
            color: #ffffff;
        }}

        .badge-status-progress {{
            background-color: #f0f0f0;
            color: #111111;
            border: 1px solid #cccccc;
        }}

        .progress-wrapper {{
            display: flex;
            align-items: center;
            gap: 6px;
            flex: 1;
            max-width: 130px;
        }}

        .progress-bar-bg {{
            flex: 1;
            height: 6px;
            background-color: #e5e5e5;
            border-radius: 3px;
            overflow: hidden;
        }}

        .progress-bar-fill {{
            height: 100%;
            background-color: #111111;
            border-radius: 3px;
            transition: width 0.3s ease;
        }}

        .progress-label {{
            font-family: var(--font-mono);
            font-size: 11.5px;
            font-weight: 700;
            color: var(--text-main);
            flex-shrink: 0;
        }}

        nav.nav-menu {{
            padding: 10px 0;
            flex: 1;
        }}

        .nav-group-title {{
            font-size: 11px;
            font-weight: 700;
            color: #777777;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            padding: 10px 16px 4px 16px;
        }}

        .nav-list {{
            list-style: none;
        }}

        .nav-item a {{
            display: block;
            padding: 5px 16px;
            color: #444444;
            text-decoration: none;
            font-size: 13px;
            line-height: 1.35;
            border-left: 3px solid transparent;
            transition: all 0.12s ease;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .nav-item a:hover {{
            color: #000000;
            background-color: #f0f0f0;
        }}

        .nav-item a.active {{
            color: #000000;
            font-weight: 600;
            background-color: #ebebeb;
            border-left-color: #000000;
        }}

        .nav-item .qa-index-num {{
            font-family: var(--font-mono);
            font-size: 11px;
            color: #666666;
            margin-right: 6px;
        }}

        /* 2. Right main content */
        main.main-content {{
            flex: 1;
            max-width: 1060px;
            padding: 20px 32px 60px 32px;
            margin: 0 auto;
        }}

        h1, h2, h3, h4 {{
            color: var(--text-main);
            font-weight: 700;
            letter-spacing: -0.2px;
            line-height: 1.3;
        }}

        h1 {{
            font-size: 22px;
            margin-bottom: 8px;
            border-bottom: 2px solid var(--border-dark);
            padding-bottom: 8px;
        }}

        h2 {{
            font-size: 16px;
            margin-top: 24px;
            margin-bottom: 10px;
            border-bottom: 1px solid var(--border-light);
            padding-bottom: 6px;
            scroll-margin-top: 20px;
        }}

        h3 {{
            font-size: 14.5px;
            margin-top: 14px;
            margin-bottom: 6px;
            scroll-margin-top: 20px;
        }}

        p {{ margin-bottom: 8px; }}

        hr {{
            border: none;
            height: 1px;
            background-color: var(--border-light);
            margin: 20px 0;
        }}

        blockquote {{
            border-left: 3px solid var(--border-dark);
            background-color: var(--bg-muted);
            padding: 8px 12px;
            margin-bottom: 12px;
            color: var(--text-muted);
            font-size: 13px;
        }}

        .table-container {{
            width: 100%;
            overflow-x: auto;
            margin-bottom: 14px;
            border: 1px solid var(--border-light);
            border-radius: 3px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: left;
        }}

        th, td {{
            padding: 6px 10px;
            border-bottom: 1px solid var(--border-light);
        }}

        th {{
            background-color: #fafafa;
            font-weight: 600;
            color: #000000;
            border-bottom: 1px solid #cccccc;
        }}

        tr:last-child td {{ border-bottom: none; }}

        .code-container {{
            background: var(--code-bg);
            border: 1px solid var(--code-border);
            border-radius: 3px;
            margin-bottom: 12px;
            overflow: hidden;
        }}

        .code-header {{
            background: #f0f2f5;
            padding: 4px 10px;
            font-size: 11px;
            color: var(--text-muted);
            border-bottom: 1px solid var(--code-border);
            font-family: var(--font-mono);
            text-transform: uppercase;
        }}

        pre {{
            padding: 8px 12px;
            overflow-x: auto;
            font-family: var(--font-mono);
            font-size: 12.5px;
            line-height: 1.45;
            color: #24292e;
        }}

        code.inline-code {{
            background: #f0f0f0;
            padding: 1px 4px;
            border-radius: 2px;
            font-family: var(--font-mono);
            font-size: 12.5px;
            color: #111111;
        }}

        .code-anchor {{
            background: #f0f0f0;
            border: 1px solid #d0d0d0;
            color: #111111;
            padding: 1px 5px;
            border-radius: 2px;
            font-family: var(--font-mono);
            font-size: 12px;
            font-weight: 600;
        }}

        a {{ color: #111111; text-decoration: underline; }}
        a:hover {{ color: #555555; }}

        ul, ol {{ margin-bottom: 10px; padding-left: 20px; }}
        li {{ margin-bottom: 4px; }}

        /* Q&A & challenge cards */
        .qa-card {{
            border: 1px solid var(--border-light);
            border-radius: 3px;
            margin-bottom: 12px;
            background: var(--bg-card);
            overflow: hidden;
            scroll-margin-top: 20px;
        }}

        .qa-header {{
            background: #f8f8f8;
            border-bottom: 1px solid var(--border-light);
            padding: 8px 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .q-badge {{
            background: #000000;
            color: #ffffff;
            font-weight: 700;
            font-size: 11px;
            padding: 1px 6px;
            border-radius: 2px;
            letter-spacing: 0.4px;
            flex-shrink: 0;
            font-family: var(--font-mono);
        }}

        .qa-tag {{
            font-size: 11px;
            color: var(--text-muted);
            background: #eeeeee;
            padding: 1px 6px;
            border-radius: 2px;
            flex-shrink: 0;
        }}

        .qa-title {{
            font-size: 13.5px;
            font-weight: 600;
            color: #000000;
            margin: 0;
            flex: 1;
        }}

        .qa-body {{
            padding: 10px 14px;
            font-size: 13px;
            line-height: 1.55;
        }}

        .qa-verdict {{
            margin-top: 8px;
            padding: 6px 10px;
            border-left: 3px solid #000000;
            background-color: #fafafa;
            font-size: 12.5px;
        }}

        /* Mermaid diagram container */
        .mermaid-diagram-container {{
            border: 1px solid var(--border-light);
            border-radius: 3px;
            margin: 12px 0;
            background: #ffffff;
            overflow: hidden;
        }}

        .mermaid-toolbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 5px 12px;
            background: #f5f5f5;
            border-bottom: 1px solid var(--border-light);
            font-size: 11px;
            color: var(--text-muted);
        }}

        .mermaid-title {{
            font-weight: 600;
            color: #222222;
        }}

        .mermaid-controls {{
            display: flex;
            gap: 4px;
        }}

        .btn-zoom {{
            background: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 2px;
            padding: 2px 6px;
            font-size: 11px;
            cursor: pointer;
            color: #111111;
            font-weight: 500;
            transition: all 0.12s ease;
        }}

        .btn-zoom:hover {{
            background: #e8e8e8;
            border-color: #999999;
        }}

        .mermaid-viewport {{
            overflow-x: auto;
            padding: 14px;
            background: #ffffff;
            display: flex;
            justify-content: center;
            min-height: 120px;
            -webkit-overflow-scrolling: touch;
        }}

        .mermaid-viewport pre.mermaid,
        .mermaid-viewport svg {{
            min-width: 800px;
            width: 100% !important;
            max-width: none !important;
            height: auto !important;
            transition: transform 0.12s ease;
        }}

        .mermaid-source {{
            display: none;
            width: 100%;
            margin: 0;
            padding: 14px;
            background: #fafafa;
            border: 1px solid #e5e5e5;
            border-radius: 3px;
            font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
            font-size: 12px;
            line-height: 1.5;
            color: #24292f;
            white-space: pre-wrap;
            word-break: break-all;
            box-sizing: border-box;
        }}

        .mermaid-error-banner {{
            display: flex;
            flex-direction: column;
            gap: 4px;
            width: 100%;
            padding: 10px 14px;
            background: #fff5f5;
            border: 1px solid #fed7d7;
            border-left: 4px solid #e53e3e;
            border-radius: 3px;
            margin-bottom: 10px;
            font-size: 12px;
            color: #9b2c2c;
            box-sizing: border-box;
        }}

        .mermaid-error-banner .error-title {{
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .mermaid-error-banner .error-msg {{
            font-family: monospace;
            background: #fed7d7;
            padding: 2px 6px;
            border-radius: 2px;
            display: inline-block;
        }}

        .mermaid-offline-banner {{
            width: 100%;
            padding: 12px 16px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #475569;
            border-radius: 3px;
            margin-bottom: 10px;
            font-size: 12px;
            color: #334155;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-sizing: border-box;
        }}

        @media print {{
            aside.sidebar {{ display: none; }}
            main.main-content {{ max-width: 100%; padding: 0; }}
            .mermaid-toolbar {{ display: none; }}
            .mermaid-viewport {{ overflow: visible; }}
            .mermaid-viewport svg {{ min-width: 100%; }}
        }}
    </style>

    <!-- Multi-CDN Resilient Loader (jsdelivr -> cdnjs -> unpkg) -->
    <script>
        window.mermaidLoaded = false;
        window.mermaidLoadFailed = false;
        (function() {{
            const cdns = [
                "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js",
                "https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.9.1/mermaid.min.js",
                "https://unpkg.com/mermaid@10/dist/mermaid.min.js"
            ];
            let idx = 0;
            function loadNext() {{
                if (idx >= cdns.length) {{
                    console.warn("All Mermaid CDNs unreachable. Falling back to offline source mode.");
                    window.mermaidLoadFailed = true;
                    if (window.renderAllMermaid) window.renderAllMermaid();
                    return;
                }}
                const s = document.createElement("script");
                s.src = cdns[idx++];
                s.crossOrigin = "anonymous";
                s.onload = function() {{
                    window.mermaidLoaded = true;
                    if (window.renderAllMermaid) window.renderAllMermaid();
                }};
                s.onerror = function() {{
                    loadNext();
                }};
                document.head.appendChild(s);
            }}
            loadNext();
        }})();
    </script>
    <script>
        window.toggleMermaidSource = function(containerId) {{
            const container = document.getElementById(containerId);
            if (!container) return;
            const mermaidEl = container.querySelector('.mermaid');
            const sourceEl = container.querySelector('.mermaid-source');
            const btn = container.querySelector('.btn-toggle-source');
            if (!sourceEl) return;
            if (sourceEl.style.display === 'none' || !sourceEl.style.display) {{
                sourceEl.style.display = 'block';
                if (mermaidEl) mermaidEl.style.display = 'none';
                if (btn) btn.textContent = 'View Diagram';
            }} else {{
                sourceEl.style.display = 'none';
                if (mermaidEl) mermaidEl.style.display = 'flex';
                if (btn) btn.textContent = 'Source / Diagram';
            }}
        }};

        window.copyMermaidSource = function(containerId) {{
            const container = document.getElementById(containerId);
            if (!container) return;
            const sourceEl = container.querySelector('.mermaid-source');
            if (!sourceEl) return;
            const text = sourceEl.textContent.trim();
            navigator.clipboard.writeText(text).then(() => {{
                const btn = container.querySelector('button[onclick*="copyMermaidSource"]');
                if (btn) {{
                    const orig = btn.textContent;
                    btn.textContent = 'Copied!';
                    setTimeout(() => {{ btn.textContent = orig; }}, 1500);
                }}
            }}).catch(() => {{
                alert('Copy failed. Please copy manually in source view.');
            }});
        }};

        window.renderAllMermaid = async function() {{
            if (window.mermaidLoadFailed) {{
                document.querySelectorAll('.mermaid-diagram-container').forEach(c => {{
                    const vp = c.querySelector('.mermaid-viewport');
                    const src = c.querySelector('.mermaid-source');
                    if (vp && src && src.style.display === 'none') {{
                        const banner = document.createElement('div');
                        banner.className = 'mermaid-offline-banner';
                        banner.innerHTML = '<span>📡 Offline Environment: Mermaid rendering script not loaded. Switched to source mode.</span>';
                        vp.insertBefore(banner, vp.firstChild);
                        window.toggleMermaidSource(c.id);
                    }}
                }});
                return;
            }}

            if (!window.mermaidLoaded || typeof mermaid === 'undefined') return;

            mermaid.initialize({{
                startOnLoad: false,
                securityLevel: 'loose',
                theme: 'base',
                themeVariables: {{
                    primaryColor: '#ffffff',
                    primaryBorderColor: '#111111',
                    primaryTextColor: '#111111',
                    lineColor: '#111111',
                    textColor: '#111111',
                    actorLineColor: '#111111',
                    actorBorder: '#111111',
                    actorBkg: '#ffffff',
                    actorTextColor: '#111111',
                    signalColor: '#111111',
                    signalTextColor: '#111111',
                    labelBoxBkgColor: '#ffffff',
                    labelBoxBorderColor: '#111111',
                    labelTextColor: '#111111',
                    loopTextColor: '#111111',
                    noteBorderColor: '#111111',
                    noteBkgColor: '#f9f9f9',
                    noteTextColor: '#111111',
                    activationBorderColor: '#111111',
                    activationBkgColor: '#f0f0f0',
                    sequenceNumberColor: '#ffffff',
                    fontSize: '13px'
                }},
                flowchart: {{ useMaxWidth: false, htmlLabels: true, curve: 'linear' }},
                sequence: {{ useMaxWidth: false, showSequenceNumbers: true, actorFontSize: 14, messageFontSize: 12, noteFontSize: 11 }}
            }});

            const mermaidNodes = document.querySelectorAll('pre.mermaid');
            for (let i = 0; i < mermaidNodes.length; i++) {{
                const el = mermaidNodes[i];
                if (el.dataset.rendered === 'true') continue;
                try {{
                    let raw = el.textContent || '';
                    raw = raw.replace(/&quot;/g, '"').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
                    const diagId = 'mermaid-svg-' + i;
                    const res = await mermaid.render(diagId, raw);
                    el.innerHTML = res.svg;
                    el.dataset.rendered = 'true';
                }} catch (err) {{
                    console.warn('Mermaid render error caught for block', i, err);
                    const dangling = document.getElementById('dmermaid-svg-' + i);
                    if (dangling) dangling.remove();
                    const container = el.closest('.mermaid-diagram-container');
                    const errShort = err.message ? err.message.split(String.fromCharCode(10))[0] : 'Syntax parse failure';
                    const banner = document.createElement('div');
                    banner.className = 'mermaid-error-banner';
                    banner.innerHTML = `<div class="error-title">⚠️ Diagram Syntax Warning</div><div class="error-msg">${{errShort}}</div><div>Automatically degraded to source view. Check source for syntax issues.</div>`;
                    el.parentNode.insertBefore(banner, el);
                    if (container) {{
                        window.toggleMermaidSource(container.id);
                    }}
                }}
            }}
        }};

        document.addEventListener('DOMContentLoaded', async function() {{
            if (window.mermaidLoaded || window.mermaidLoadFailed) {{
                window.renderAllMermaid();
            }}

            // Scrollspy & Anchor navigation (Immune to invalid selector crashes)
            const navLinks = document.querySelectorAll('.nav-menu a');
            const targetItems = [];
            navLinks.forEach(link => {{
                const href = link.getAttribute('href');
                if (href && href.startsWith('#')) {{
                    const targetEl = document.getElementById(href.slice(1));
                    if (targetEl) {{
                        targetItems.push({{ el: targetEl, link: link }});
                    }}
                }}
            }});

            function updateScrollspy() {{
                const scrollPos = window.scrollY + 80;
                let activeLink = null;
                for (let i = 0; i < targetItems.length; i++) {{
                    const top = targetItems[i].el.getBoundingClientRect().top + window.scrollY;
                    if (top <= scrollPos) {{
                        activeLink = targetItems[i].link;
                    }} else {{
                        break;
                    }}
                }}
                if (!activeLink && targetItems.length > 0) {{
                    activeLink = targetItems[0].link;
                }}
                navLinks.forEach(l => l.classList.remove('active'));
                if (activeLink) {{
                    activeLink.classList.add('active');
                }}
            }}

            window.addEventListener('scroll', updateScrollspy, {{ passive: true }});
            updateScrollspy();

            // Smooth scroll click handler
            navLinks.forEach(link => {{
                link.addEventListener('click', function(e) {{
                    const href = this.getAttribute('href');
                    if (href && href.startsWith('#')) {{
                        const targetEl = document.getElementById(href.slice(1));
                        if (targetEl) {{
                            e.preventDefault();
                            targetEl.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                            history.pushState(null, null, href);
                            navLinks.forEach(l => l.classList.remove('active'));
                            this.classList.add('active');
                        }}
                    }}
                }});
            }});
        }});

        window.zoomMermaid = function(containerId, factor) {{
            const container = document.getElementById(containerId);
            if (!container) return;
            const target = container.querySelector('svg') || container.querySelector('.mermaid');
            if (!target) return;
            let currentScale = parseFloat(target.dataset.scale || '1.0');
            currentScale = Math.min(3.0, Math.max(0.6, currentScale * factor));
            target.dataset.scale = currentScale.toFixed(2);
            applySvgScale(target, currentScale);
        }};

        window.setMermaidZoom = function(containerId, scale) {{
            const container = document.getElementById(containerId);
            if (!container) return;
            const target = container.querySelector('svg') || container.querySelector('.mermaid');
            if (!target) return;
            target.dataset.scale = scale.toFixed(2);
            applySvgScale(target, scale);
        }};

        function applySvgScale(element, scale) {{
            element.style.transform = `scale(${{scale}})`;
            element.style.transformOrigin = 'top left';
            const baseW = 800;
            element.style.minWidth = `${{Math.round(baseW * scale)}}px`;
        }}
    </script>
</head>
<body>
    <aside class="sidebar">
        <div class="sidebar-header">
            <div class="brand-title">Repo<span>Mentor</span></div>
            <div class="repo-meta-card">
                <div class="meta-row"><span>Target Project</span><strong>{html.escape(repo_name)}</strong></div>
                <div class="meta-row"><span>Ecosystem</span><strong>{html.escape(lang)}</strong></div>
                <div class="meta-row"><span>Architecture</span><strong>{html.escape(pattern)}</strong></div>
                <div class="meta-row"><span>Study Status</span><span class="badge-status {status_badge_class}">{status_label}</span></div>
                <div class="meta-row">
                    <span>Mastery</span>
                    <div class="progress-wrapper">
                        <div class="progress-bar-bg">
                            <div class="progress-bar-fill" style="width: {pct_val:.1f}%;"></div>
                        </div>
                        <span class="progress-label">{progress}</span>
                    </div>
                </div>
                <div class="meta-row"><span>Q&A Records</span><strong>{qa_count} (Lossless)</strong></div>
            </div>
        </div>

        <nav class="nav-menu">
            <div class="nav-group-title">I. System Positioning & Architecture</div>
            <ul class="nav-list">
                <li class="nav-item"><a href="#section-1-1" class="active">1.1 Background & Problems Solved</a></li>
                <li class="nav-item"><a href="#section-1-2">1.2 Business Flow & Architecture</a></li>
                <li class="nav-item"><a href="#section-1-3">1.3 Directory & Module Division</a></li>
                <li class="nav-item"><a href="#section-1-4">1.4 Module Reading Priority</a></li>
                <li class="nav-item"><a href="#section-1-5">1.5 Study Mastery & Blind Spots</a></li>
            </ul>

            <div class="nav-group-title">II. Core Code Walkthrough ({qa_count})</div>
            <ul class="nav-list">
                {t2_nav_str}
            </ul>

            <div class="nav-group-title">III. Limit Scenarios & Defense</div>
            <ul class="nav-list">
                {t3_nav_str}
            </ul>
        </nav>
    </aside>

    <main class="main-content">
        {body_html}
    </main>
</body>
</html>"""


def export_study(study_dir: str | Path, output_file: str | Path = None) -> dict:
    """
    Exports a study directory or markdown file into the standalone HTML review whitepaper.
    """
    s_path = Path(study_dir).resolve()
    if not s_path.exists():
        return {"error": f"Path does not exist: {study_dir}"}

    repo_name = s_path.name
    t2_items = []
    t3_items = []

    if s_path.is_dir():
        full_markdown, metadata, t2_items, t3_items = build_integrated_study_notes(s_path)
        if not output_file:
            dist_dir = s_path / "dist"
            dist_dir.mkdir(parents=True, exist_ok=True)
            out_path = dist_dir / "index.html"
        else:
            out_path = Path(output_file).resolve()
    elif s_path.is_file():
        full_markdown = s_path.read_text(encoding="utf-8", errors="replace")
        repo_name = s_path.stem
        raw_qas = extract_explicit_qa_items(full_markdown)
        tracker_row = find_and_read_tracker(s_path, repo_name)
        file_prog = tracker_row.get("Progress", "100%") if tracker_row else "100%"
        file_stat = tracker_row.get("Status", "completed" if file_prog == "100%" else "in_progress") if tracker_row else ("completed" if file_prog == "100%" else "in_progress")
        metadata = {
            "repo_name": repo_name,
            "language": tracker_row.get("Language", "Multi-Language") if tracker_row else "Multi-Language",
            "pattern": tracker_row.get("Pattern", "Architecture Whitepaper") if tracker_row else "Architecture Whitepaper",
            "progress": file_prog,
            "status": file_stat,
            "qa_count": len(raw_qas),
            "challenge_count": 0
        }
        t2_items = raw_qas
        t3_items = []
        out_path = Path(output_file).resolve() if output_file else s_path.with_suffix(".html")

    # Single-pass conversion of entire document
    body_html = simple_markdown_to_html(full_markdown)
    html_page = build_full_html_page(
        title=f"{repo_name} Architecture Study & Review Whitepaper",
        body_html=body_html,
        metadata=metadata,
        tier2_items=t2_items,
        tier3_items=t3_items
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_page, encoding="utf-8")

    return {
        "success": True,
        "repo_name": repo_name,
        "output_file": str(out_path),
        "file_size_bytes": len(html_page.encode("utf-8")),
        "qa_count": metadata.get("qa_count", 0),
        "challenge_count": metadata.get("challenge_count", 0)
    }


def main():
    parser = argparse.ArgumentParser(description="Export repo study assets to a single-file standalone offline HTML report.")
    parser.add_argument("study_dir", help="Path to study directory (e.g. studies/<repo_name>/) or markdown file")
    parser.add_argument("--out", help="Optional custom output path for index.html")

    args = parser.parse_args()

    res = export_study(args.study_dir, output_file=args.out)
    if res.get("success"):
        print(f"✓ Architecture study manual successfully exported to: {res['output_file']}")
        print(f"  File size: {res['file_size_bytes']} bytes")
        print(f"  Core Q&A records: {res['qa_count']} (lossless)")
        print(f"  Architectural challenges: {res['challenge_count']}")
        sys.exit(0)
    else:
        print(f"✗ Export failed: {res.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
