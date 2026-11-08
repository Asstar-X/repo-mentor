"""repo_mentor.verification.anchor_verifier: AST-Grounded Code Anchor Verification.

Extends anchor validation from mere line count bounds to semantic AST symbol grounding.
Extracts code citations, verifies physical file existence, checks line bounds, and
validates that cited symbols (classes, functions, methods, structs, interfaces) physically
exist at or near the cited lines (with ±15 lines drift tolerance).
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from rich.console import Console
from rich.table import Table

from repo_mentor.core.parser import SymbolIndex

console = Console()

# Anchor Extraction Patterns
# 1. Standard markdown link: [label](path#L10-L20) or [label](file:///path#L10-L20)
MD_LINK_RE = re.compile(r'\[([^\]]+)\]\((?:file://)?([^)#\s]+)(?:#L(\d+)(?:-L?(\d+))?)?\)')

# 2. Shorthand anchor with line numbers: [path/to/file#L10-L20] or [path/to/file#L10]
BRACKET_LINE_RE = re.compile(r'\[([a-zA-Z0-9_\-\./\\]+)#L(\d+)(?:-L?(\d+))?\]')

# 3. Shorthand anchor without line numbers: [path/to/file.ext]
BRACKET_FILE_RE = re.compile(r'\[([a-zA-Z0-9_\-\./\\]*(?:/[a-zA-Z0-9_\-\.]+|\.[a-zA-Z0-9_]{1,10}))\]')

# 4. Inline backtick anchor: `path/to/file#L10-L20`
BACKTICK_ANCHOR_RE = re.compile(r'`([a-zA-Z0-9_\-\./\\]+)#L(\d+)(?:-L?(\d+))?`')

# 5. Mermaid participant anchor: participant Id as "Symbol (path#L10)"
MERMAID_PARTICIPANT_RE = re.compile(
    r'participant\s+([a-zA-Z0-9_\-]+)\s+as\s+"([^"(]+)\s+\((?:file://)?([^)#]+)#L(\d+)(?:-L?(\d+))?\)"'
)

# 6. Preceding symbol pattern: `SymbolName` ... [path#L..] or `SymbolName`: [path#L..]
PRECEDING_SYMBOL_RE = re.compile(r'`([a-zA-Z0-9_\.\:\*]+)`(?:\s*[:\-—]\s*|\s+)\[([^\]]+)\]')

IGNORED_SCHEMES = ("http://", "https://", "mailto:", "ftp://", "#")
IGNORED_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".pdf", ".zip", ".tar", ".gz"}
NON_PATH_TOKENS = {
    "NEW", "DELETE", "MODIFY", "TODO", "NOTE", "TIP", "IMPORTANT",
    "WARNING", "CAUTION", "VERIFIED FACT", "ENGINEERING INFERENCE",
    "UNVERIFIED HYPOTHESIS", "YES", "NO"
}


@dataclass
class AnchorItem:
    """Represents a candidate code anchor extracted from markdown."""
    raw_text: str
    file_path: str
    start_line: Optional[int]
    end_line: Optional[int]
    claimed_symbol: Optional[str] = None
    line_in_doc: int = 1
    anchor_type: str = "bracket_anchor"


@dataclass
class AnchorVerificationResult:
    """Outcome of validating an individual code anchor."""
    anchor: AnchorItem
    is_valid: bool
    file_exists: bool
    lines_valid: bool
    symbol_grounded: Optional[bool]  # None if no symbol claimed, True/False if claimed
    found_symbol: Optional[str] = None
    resolved_path: Optional[str] = None
    category: str = "ok"  # 'ok' | 'missing_file' | 'out_of_bounds' | 'phantom_symbol'
    error_message: str = ""


def _is_probable_symbol(token: str) -> bool:
    """Checks if a string looks like a programming symbol (function, class, method)."""
    token = token.strip().strip("`").strip("'").strip('"')
    if not token or len(token) > 80:
        return False
    if " " in token:
        # Might be like "func (e *Engine) Run"
        if token.startswith("func ") or token.startswith("def ") or token.startswith("class "):
            return True
        return False
    if token.upper() in NON_PATH_TOKENS:
        return False
    # Valid identifier characters (allowing dots, underscores, colons, parens)
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_\.:]*(?:\(\))?$', token))


def _extract_clean_symbol(token: str) -> str:
    """Normalizes symbol string, e.g. 'Memory.add()' -> 'Memory.add'."""
    s = token.strip().strip("`").strip("'").strip('"')
    if s.endswith("()"):
        s = s[:-2]
    if s.startswith("func ") or s.startswith("def "):
        parts = s.split()
        s = parts[-1].split("(")[0]
    return s


def extract_anchors(text: str) -> List[AnchorItem]:
    """Extracts all code file references, line ranges, and claimed symbols from Markdown."""
    anchors: List[AnchorItem] = []
    seen: Set[Tuple[str, Optional[int], Optional[int], Optional[str]]] = set()

    # Pre-map lines to line numbers for doc coordinates
    doc_lines = text.splitlines()

    def get_line_in_doc(char_pos: int) -> int:
        return text[:char_pos].count("\n") + 1

    # 1. Mermaid participants with anchors: participant Mem as "Memory.add (mem0/memory/main.py#L760)"
    for m in MERMAID_PARTICIPANT_RE.finditer(text):
        sym_label = m.group(2).strip()
        fpath = m.group(3).strip().replace("\\", "/")
        s_line: Optional[int] = int(m.group(4))
        e_line: Optional[int] = int(m.group(5)) if m.group(5) else s_line
        claimed_sym = _extract_clean_symbol(sym_label) if _is_probable_symbol(sym_label) else None
        key: Tuple[str, Optional[int], Optional[int], Optional[str]] = (fpath, s_line, e_line, claimed_sym)
        if key not in seen:
            seen.add(key)
            anchors.append(AnchorItem(
                raw_text=m.group(0),
                file_path=fpath,
                start_line=s_line,
                end_line=e_line,
                claimed_symbol=claimed_sym,
                line_in_doc=get_line_in_doc(m.start()),
                anchor_type="mermaid_participant"
            ))

    # 2. Preceding symbol pattern: `MemoryConfig`: [`mem0/configs/base.py#L29-L45`]
    for m in PRECEDING_SYMBOL_RE.finditer(text):
        sym_name = m.group(1).strip()
        bracket_content = m.group(2).strip()
        # Parse bracket_content for path#Lstart-Lend
        m_inner = re.match(r'^(?:file://)?([^#\s]+)(?:#L(\d+)(?:-L?(\d+))?)?$', bracket_content)
        if m_inner:
            fpath = m_inner.group(1).strip().replace("\\", "/")
            if any(fpath.startswith(sch) for sch in IGNORED_SCHEMES):
                continue
            ext = os.path.splitext(fpath)[1].lower()
            if ext in IGNORED_EXTS:
                continue
            s_line = int(m_inner.group(2)) if m_inner.group(2) else None
            e_line = int(m_inner.group(3)) if m_inner.group(3) else s_line
            claimed_sym = _extract_clean_symbol(sym_name)
            key = (fpath, s_line, e_line, claimed_sym)
            if key not in seen:
                seen.add(key)
                anchors.append(AnchorItem(
                    raw_text=m.group(0),
                    file_path=fpath,
                    start_line=s_line,
                    end_line=e_line,
                    claimed_symbol=claimed_sym,
                    line_in_doc=get_line_in_doc(m.start()),
                    anchor_type="symbol_preceded_anchor"
                ))

    # 3. Standard markdown links: [label](path#L10-L20)
    for m in MD_LINK_RE.finditer(text):
        label = m.group(1).strip()
        raw_path = m.group(2).strip().replace("\\", "/")
        if any(raw_path.startswith(sch) for sch in IGNORED_SCHEMES):
            continue
        ext = os.path.splitext(raw_path)[1].lower()
        if ext in IGNORED_EXTS:
            continue

        s_line = int(m.group(3)) if m.group(3) else None
        e_line = int(m.group(4)) if m.group(4) else s_line
        claimed_sym = None
        if _is_probable_symbol(label):
            claimed_sym = _extract_clean_symbol(label)

        key = (raw_path, s_line, e_line, claimed_sym)
        if key not in seen:
            seen.add(key)
            anchors.append(AnchorItem(
                raw_text=m.group(0),
                file_path=raw_path,
                start_line=s_line,
                end_line=e_line,
                claimed_symbol=claimed_sym,
                line_in_doc=get_line_in_doc(m.start()),
                anchor_type="markdown_link"
            ))

    # 4. Bracketed line anchors: [path#Lstart-Lend]
    for m in BRACKET_LINE_RE.finditer(text):
        raw_path = m.group(1).strip().replace("\\", "/")
        if any(raw_path.startswith(sch) for sch in IGNORED_SCHEMES):
            continue
        ext = os.path.splitext(raw_path)[1].lower()
        if ext in IGNORED_EXTS:
            continue

        s_line = int(m.group(2))
        e_line = int(m.group(3)) if m.group(3) else s_line

        # Check if line before or nearby names a symbol
        doc_line = doc_lines[get_line_in_doc(m.start()) - 1]
        claimed_sym = None
        sym_match = re.search(r'`([a-zA-Z0-9_\.\:]+)`', doc_line)
        if sym_match and sym_match.group(1) != raw_path:
            cand = sym_match.group(1)
            if _is_probable_symbol(cand):
                claimed_sym = _extract_clean_symbol(cand)

        key = (raw_path, s_line, e_line, claimed_sym)
        if key not in seen:
            seen.add(key)
            anchors.append(AnchorItem(
                raw_text=m.group(0),
                file_path=raw_path,
                start_line=s_line,
                end_line=e_line,
                claimed_symbol=claimed_sym,
                line_in_doc=get_line_in_doc(m.start()),
                anchor_type="bracket_line_anchor"
            ))

    # 5. Backtick anchors: `path#L10-L20`
    for m in BACKTICK_ANCHOR_RE.finditer(text):
        raw_path = m.group(1).strip().replace("\\", "/")
        if any(raw_path.startswith(sch) for sch in IGNORED_SCHEMES):
            continue
        ext = os.path.splitext(raw_path)[1].lower()
        if ext in IGNORED_EXTS:
            continue

        s_line = int(m.group(2))
        e_line = int(m.group(3)) if m.group(3) else s_line

        key = (raw_path, s_line, e_line, None)
        if key not in seen:
            seen.add(key)
            anchors.append(AnchorItem(
                raw_text=m.group(0),
                file_path=raw_path,
                start_line=s_line,
                end_line=e_line,
                claimed_symbol=None,
                line_in_doc=get_line_in_doc(m.start()),
                anchor_type="backtick_anchor"
            ))

    # 6. Bracketed file references without lines: [dir/file.ext]
    for m in BRACKET_FILE_RE.finditer(text):
        raw_path = m.group(1).strip().replace("\\", "/")
        if raw_path.upper() in NON_PATH_TOKENS:
            continue
        if any(raw_path.startswith(sch) for sch in IGNORED_SCHEMES):
            continue
        ext = os.path.splitext(raw_path)[1].lower()
        if ext in IGNORED_EXTS:
            continue
        if not ("/" in raw_path or "." in raw_path):
            continue

        key = (raw_path, None, None, None)
        if key not in seen:
            seen.add(key)
            anchors.append(AnchorItem(
                raw_text=m.group(0),
                file_path=raw_path,
                start_line=None,
                end_line=None,
                claimed_symbol=None,
                line_in_doc=get_line_in_doc(m.start()),
                anchor_type="bracket_file_anchor"
            ))

    return anchors


class AnchorVerifier:
    """Verifies anchors against repository files and AST symbol indices."""

    def __init__(self, repo_root: str | Path, symbol_index: Optional[SymbolIndex] = None):
        self.repo_root = Path(repo_root).resolve()
        self.line_count_cache: Dict[str, int] = {}
        if symbol_index is not None:
            self.symbol_index = symbol_index
        else:
            self.symbol_index = SymbolIndex(self.repo_root)

    def _get_file_line_count(self, file_path: Path) -> int:
        norm = str(file_path.resolve())
        if norm in self.line_count_cache:
            return self.line_count_cache[norm]
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                count = sum(1 for _ in f)
            self.line_count_cache[norm] = count
            return count
        except Exception:
            return 0

    def resolve_target_file(self, rel_path: str, md_parent: Optional[Path] = None) -> Optional[Path]:
        """Resolves target file relative to repo root, markdown parent, or absolute."""
        p = Path(rel_path)
        if p.is_absolute():
            resolved = p.resolve()
            if resolved.exists():
                return resolved
            return None

        # 1. Direct relative to repo root
        cand = (self.repo_root / rel_path).resolve()
        if cand.exists():
            return cand

        # 2. Check if rel_path contains repo_root's name as leading dir
        if rel_path.startswith(self.repo_root.name + "/"):
            stripped = rel_path[len(self.repo_root.name) + 1:]
            cand = (self.repo_root / stripped).resolve()
            if cand.exists():
                return cand

        # 3. Check relative to markdown doc parent (for study links)
        if md_parent:
            cand = (md_parent / rel_path).resolve()
            if cand.exists():
                return cand

        # 4. Search by relative tail
        tail_candidates = list(self.repo_root.glob(f"**/{p.name}"))
        for tc in tail_candidates:
            if str(tc).endswith(rel_path.lstrip("/")):
                return tc.resolve()

        return None

    def verify_item(
        self,
        anchor: AnchorItem,
        md_parent: Optional[Path] = None,
        drift_tolerance: int = 15
    ) -> AnchorVerificationResult:
        """Verifies a single anchor against filesystem and AST symbol index."""
        target = self.resolve_target_file(anchor.file_path, md_parent)
        if not target or not target.is_file():
            # Check if directory
            if target and target.is_dir():
                return AnchorVerificationResult(
                    anchor=anchor,
                    is_valid=True,
                    file_exists=True,
                    lines_valid=True,
                    symbol_grounded=None,
                    resolved_path=str(target),
                    category="ok"
                )
            return AnchorVerificationResult(
                anchor=anchor,
                is_valid=False,
                file_exists=False,
                lines_valid=False,
                symbol_grounded=False if anchor.claimed_symbol else None,
                category="missing_file",
                error_message=f"File not found in repository: {anchor.file_path}"
            )

        resolved_path_str = str(target)
        total_lines = self._get_file_line_count(target)

        # Ensure target file is parsed in symbol index if code file
        ext = target.suffix.lower()
        if ext in {".py", ".go", ".rs", ".ts", ".tsx", ".js"}:
            norm_rel = self.symbol_index._normalize_path(target)
            if norm_rel not in self.symbol_index.symbols_by_file:
                self.symbol_index.parse_file(target)

        # 1. Line bounds check
        lines_valid = True
        if anchor.start_line is not None:
            if anchor.start_line < 1 or anchor.start_line > total_lines:
                lines_valid = False
            if anchor.end_line is not None:
                if anchor.end_line < anchor.start_line or anchor.end_line > total_lines:
                    lines_valid = False

        if not lines_valid:
            return AnchorVerificationResult(
                anchor=anchor,
                is_valid=False,
                file_exists=True,
                lines_valid=False,
                symbol_grounded=False if anchor.claimed_symbol else None,
                resolved_path=resolved_path_str,
                category="out_of_bounds",
                error_message=(
                    f"Line bounds out of range: cited L{anchor.start_line}-L{anchor.end_line}, "
                    f"but file has {total_lines} lines"
                )
            )

        # 2. Semantic AST symbol grounding check
        symbol_grounded: Optional[bool] = None
        found_symbol_name: Optional[str] = None

        if anchor.claimed_symbol:
            grounded = self.symbol_index.has_symbol(
                file_path=resolved_path_str,
                symbol_name=anchor.claimed_symbol,
                start_line=anchor.start_line or 1,
                end_line=anchor.end_line or (anchor.start_line or total_lines),
                drift_tolerance=drift_tolerance
            )
            # If exact match failed, check if the symbol at the cited line is a prefix/suffix variant
            # (e.g. 'Embedder' referencing 'EmbedderFactory', or 'Memory' referencing 'MemoryConfig')
            actual_sym = self.symbol_index.find_symbol_at(
                resolved_path_str,
                anchor.start_line or 1
            )
            if not grounded and actual_sym:
                c_low = anchor.claimed_symbol.lower()
                a_low = actual_sym.symbol_name.lower()
                if (
                    a_low.startswith(c_low) or c_low.startswith(a_low) or
                    c_low in a_low or a_low in c_low or
                    c_low.replace(" ", "") in a_low or a_low in c_low.replace(" ", "")
                ):
                    grounded = True

            symbol_grounded = grounded
            if not grounded:
                # Provide diagnostic about what is actually at that line
                actual_desc = f" (found '{actual_sym.symbol_name}' instead)" if actual_sym else ""
                return AnchorVerificationResult(
                    anchor=anchor,
                    is_valid=False,
                    file_exists=True,
                    lines_valid=True,
                    symbol_grounded=False,
                    resolved_path=resolved_path_str,
                    found_symbol=actual_sym.symbol_name if actual_sym else None,
                    category="phantom_symbol",
                    error_message=(
                        f"Claimed symbol '{anchor.claimed_symbol}' does not span lines "
                        f"L{anchor.start_line}-L{anchor.end_line}{actual_desc}"
                    )
                )
        else:
            # Query if there's any symbol at the line
            if anchor.start_line is not None:
                sym_loc = self.symbol_index.find_symbol_at(
                    resolved_path_str,
                    anchor.start_line
                )
                if sym_loc:
                    found_symbol_name = sym_loc.symbol_name

        return AnchorVerificationResult(
            anchor=anchor,
            is_valid=True,
            file_exists=True,
            lines_valid=True,
            symbol_grounded=symbol_grounded,
            found_symbol=found_symbol_name,
            resolved_path=resolved_path_str,
            category="ok"
        )


def audit_markdown_anchors(
    repo_dir: str | Path,
    md_path: str | Path,
    symbol_index: Optional[SymbolIndex] = None,
    fix: bool = False,
    drift_tolerance: int = 15
) -> Dict[str, Any]:
    """
    Audits all code anchors in a Markdown file, verifying physical existence,
    line bounds, and AST symbol grounding.
    """
    repo_root = Path(repo_dir).resolve()
    doc_path = Path(md_path).resolve()

    if not repo_root.is_dir():
        return {
            "valid": False,
            "error": f"Repository directory not found: {repo_dir}",
            "total_anchors": 0,
            "verified_count": 0,
            "hallucinations": [],
            "grounding_rate": 0.0,
            "hallucination_rate": 100.0
        }

    if not doc_path.is_file():
        return {
            "valid": False,
            "error": f"Document file not found: {md_path}",
            "total_anchors": 0,
            "verified_count": 0,
            "hallucinations": [],
            "grounding_rate": 0.0,
            "hallucination_rate": 100.0
        }

    text = doc_path.read_text(encoding="utf-8", errors="replace")
    anchors = extract_anchors(text)

    verifier = AnchorVerifier(repo_root, symbol_index=symbol_index)
    results: List[AnchorVerificationResult] = []
    hallucinations: List[Dict[str, Any]] = []
    valid_count = 0

    fixed_text = text
    fix_applied = False

    for item in anchors:
        res = verifier.verify_item(item, md_parent=doc_path.parent, drift_tolerance=drift_tolerance)
        results.append(res)
        if res.is_valid:
            valid_count += 1
            # If fix is requested and line numbers drifted slightly, update to actual symbol span
            if fix and item.claimed_symbol and item.start_line and res.resolved_path:
                actual_sym = verifier.symbol_index.find_symbol_at(res.resolved_path, item.start_line)
                if actual_sym and (actual_sym.start_line != item.start_line or actual_sym.end_line != item.end_line):
                    old_sub = f"#L{item.start_line}-L{item.end_line}"
                    if old_sub not in fixed_text:
                        old_sub = f"#L{item.start_line}"
                    new_sub = f"#L{actual_sym.start_line}-L{actual_sym.end_line}"
                    if old_sub in fixed_text:
                        fixed_text = fixed_text.replace(old_sub, new_sub)
                        fix_applied = True
        else:
            hallucinations.append({
                "file": item.file_path,
                "lines": f"L{item.start_line}-L{item.end_line}" if item.start_line else "N/A",
                "claimed_symbol": item.claimed_symbol,
                "doc_line": item.line_in_doc,
                "category": res.category,
                "error": res.error_message
            })

    if fix and fix_applied:
        doc_path.write_text(fixed_text, encoding="utf-8")

    total = len(anchors)
    grounding_rate = round((valid_count / total * 100.0), 1) if total > 0 else 100.0
    hallucination_rate = round((len(hallucinations) / total * 100.0), 1) if total > 0 else 0.0

    return {
        "valid": len(hallucinations) == 0,
        "target_file": str(doc_path),
        "total_anchors": total,
        "verified_count": valid_count,
        "grounding_rate": grounding_rate,
        "hallucination_rate": hallucination_rate,
        "hallucinations": hallucinations,
        "results": results
    }


def verify_study_anchors(
    repo_dir: str | Path,
    study_path: str | Path,
    fix: bool = False
) -> Dict[str, Any]:
    """
    Scans a study directory or individual file, verifying all anchors and Mermaid diagrams.
    Returns aggregated audit results and prints a rich summary table.
    """
    repo_root = Path(repo_dir).resolve()
    target = Path(study_path).resolve()

    console.print("[bold cyan]Milestone 4 Verification Engine: Anchor & Mermaid Audit[/bold cyan]")
    console.print(f"Target Repo: [dim]{repo_root}[/dim] | Study: [dim]{target}[/dim]\n")

    if target.is_file():
        files_to_check = [target]
    elif target.is_dir():
        files_to_check = [p for p in target.rglob("*.md") if not p.name.startswith(".")]
    else:
        console.print(f"[bold red]Target path not found:[/bold red] {study_path}")
        return {"success": False, "error": "Target path not found"}

    symbol_index = SymbolIndex(repo_root)
    # Pre-parse common entrypoints & top-level files
    symbol_index.build_index(max_depth=3)

    total_anchors = 0
    total_valid = 0
    all_hallucinations: List[Dict[str, Any]] = []

    table = Table(title="Anchor Audit Summary", header_style="bold magenta")
    table.add_column("Document", style="cyan")
    table.add_column("Anchors", justify="right")
    table.add_column("Verified", justify="right", style="green")
    table.add_column("Grounding %", justify="right")
    table.add_column("Status", justify="center")

    for doc in files_to_check:
        audit = audit_markdown_anchors(repo_root, doc, symbol_index=symbol_index, fix=fix)
        total_anchors += audit["total_anchors"]
        total_valid += audit["verified_count"]
        all_hallucinations.extend(audit["hallucinations"])

        status_str = "[bold green]PASS[/bold green]" if audit["valid"] else "[bold red]FAIL[/bold red]"
        gr_str = f"{audit['grounding_rate']}%"
        table.add_row(
            doc.name,
            str(audit["total_anchors"]),
            str(audit["verified_count"]),
            gr_str,
            status_str
        )

    console.print(table)

    # Print hallucinations if any
    if all_hallucinations:
        err_table = Table(title="Detected Hallucinations & Violations", header_style="bold red")
        err_table.add_column("Doc Line", justify="right")
        err_table.add_column("Cited Target", style="yellow")
        err_table.add_column("Category", style="red")
        err_table.add_column("Details")
        for h in all_hallucinations:
            err_table.add_row(
                f"L{h['doc_line']}",
                f"{h['file']} ({h['lines']})",
                h["category"],
                h["error"]
            )
        console.print(err_table)

    overall_grounding = round((total_valid / total_anchors * 100.0), 1) if total_anchors > 0 else 100.0
    overall_hr = round((len(all_hallucinations) / total_anchors * 100.0), 1) if total_anchors > 0 else 0.0

    return {
        "success": len(all_hallucinations) == 0,
        "files_checked": len(files_to_check),
        "total_anchors": total_anchors,
        "verified_anchors": total_valid,
        "grounding_rate": overall_grounding,
        "hallucination_rate": overall_hr,
        "hallucinations": all_hallucinations
    }
