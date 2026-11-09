"""repo_mentor.verification.fluff_detector: Anti-AI Fluff Linter & Fluff-Free Index Engine.

Scans Markdown documents against the 52-term Banned Buzzwords Blacklist (Chinese & English),
detects ungrounded descriptive paragraphs (>60 chars without code tokens, paths, or anchors),
detects cliche structural boilerplate, checks for required trade-offs analysis, and
calculates the Fluff-Free Index (FFI >= 90/100).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Tuple

# 52-Term Banned Buzzwords & Vacuous Phrases Blacklist (Chinese & English)
BANNED_BUZZWORDS: List[Tuple[str, str, str]] = [
    # Chinese Banned Terms (1-26)
    (r'优雅的?(?:设计|实现|架构)|设计极其精妙|非常优雅', "banned_buzzword", "Vacuous flattery: '优雅的设计/非常优雅' (N8)"),
    (r'功能强大且灵活|功能强大', "banned_buzzword", "Empty marketing buzzword: '功能强大且灵活' (N2)"),
    (r'无缝(?:集成|融合|衔接)', "banned_buzzword", "Vague marketing buzzword: '无缝集成' (N2)"),
    (r'极具扩展性|具备极高的灵活性|极高的灵活性', "banned_buzzword", "Ungrounded extensibility claim: '极具扩展性/极高的灵活性' (N2)"),
    (r'业界领先|行业领先', "banned_buzzword", "Unsubstantiated hyperbole: '业界领先' (N2)"),
    (r'浑然一体', "banned_buzzword", "Literary fluff: '浑然一体' (N2)"),
    (r'不言而喻', "banned_buzzword", "Hand-waving filler: '不言而喻' (N2)"),
    (r'应运而生', "banned_buzzword", "Cliche narrative fluff: '应运而生' (N2)"),
    (r'举足轻重', "banned_buzzword", "Unsubstantiated praise: '举足轻重' (N2)"),
    (r'高内聚低耦合|高内聚|低耦合', "banned_buzzword", "Generic engineering cliché: '高内聚低耦合' (N2)"),
    (r'企业级(?:设计|架构|标准)', "banned_buzzword", "Vague corporate cliché: '企业级设计' (N2)"),
    (r'健壮的异常处理', "banned_buzzword", "Unverified resilience assertion: '健壮的异常处理' (N2)"),
    (r'代码功底非常深厚|作者功底', "banned_buzzword", "Flattery towards authors: '代码功底非常深厚' (N8)"),
    (r'总的来说', "cliche_structure", "Cliche student intro/outro: '总的来说' (N2)"),
    (r'综上所述', "cliche_structure", "Mechanical boilerplate summary: '综上所述' (N2)"),
    (r'值得注意的是', "cliche_structure", "Lazy transition filler: '值得注意的是' (N2)"),
    (r'毋庸置疑', "cliche_structure", "Unsupported assertion filler: '毋庸置疑' (N2)"),
    (r'不仅如此而且|不仅如此，而且', "cliche_structure", "Verbose filler conjunction: '不仅如此而且' (N2)"),
    (r'今天我们来一起学习|一起学习', "cliche_structure", "Tutorial/Student tone: '今天我们来一起学习' (N2)"),
    (r'首先[，,].*其次[，,].*再次[，,]', "cliche_structure", "Mechanical student enumeration (N2)"),
    (r'开箱即用', "banned_buzzword", "Sales buzzword: '开箱即用' (N2)"),
    (r'卓越的性能', "banned_buzzword", "Unbenchmarked performance claim: '卓越的性能' (N2)"),
    (r'不可或缺', "banned_buzzword", "Dramatic hyperbole: '不可或缺' (N2)"),
    (r'显而易见', "banned_buzzword", "Presumptuous dismissive filler: '显而易见' (N2)"),
    (r'众所周知', "banned_buzzword", "Presumptive filler: '众所周知' (N2)"),
    (r'巧妙权衡', "banned_buzzword", "Whitewashing potential architectural debt: '巧妙权衡' (N8)"),

    # English Banned Terms (27-52)
    (r'\brobust and scalable\b', "banned_buzzword", "Generic buzzword pair: 'robust and scalable' (N2)"),
    (r'\bcutting-edge\b', "banned_buzzword", "Marketing hype: 'cutting-edge' (N2)"),
    (
        r'\bseamlessly (?:blends|integrates?|combines?)\b|\bseamless integration\b',
        "banned_buzzword",
        "Unsubstantiated marketing claim: 'seamlessly integrates' (N2)"
    ),
    (r'\bstate-of-the-art\b', "banned_buzzword", "Hyperbolic claim: 'state-of-the-art' (N2)"),
    (r'\bcomprehensive suite\b', "banned_buzzword", "Corporate sales jargon: 'comprehensive suite' (N2)"),
    (r'\bcarefully (?:engineered|crafted)\b', "banned_buzzword", "Flattery filler: 'carefully engineered' (N8)"),
    (r'\bgame-changer\b', "banned_buzzword", "Sensationalism: 'game-changer' (N2)"),
    (r'\bout of the box\b', "banned_buzzword", "Cliché filler: 'out of the box' (N2)"),
    (r'\bindustry-leading\b', "banned_buzzword", "Commercial hype: 'industry-leading' (N2)"),
    (r'\bhighly modular and extensible\b', "banned_buzzword", "Unsubstantiated architectural assertion (N2)"),
    (r'\belegantly designed\b|\belegant design\b', "banned_buzzword", "Subjective flattery: 'elegantly designed' (N8)"),
    (r'\bblazing(?:ly)? fast\b', "banned_buzzword", "Unverified performance claim: 'blazingly fast' (N2)"),
    (r'\bcrystal clear\b', "banned_buzzword", "Colloquial cliché: 'crystal clear' (N2)"),
    (r'\bwithout a doubt\b', "cliche_structure", "Filler assertion: 'without a doubt' (N2)"),
    (r'\bin conclusion\b|\ball in all\b|\bto sum up\b', "cliche_structure", "Mechanical conclusion template (N2)"),
    (r'\bdive deep into\b|\bdeep dive\b', "cliche_structure", "Overused AI colloquialism: 'deep dive' (N2)"),
    (r'\bit goes without saying\b', "cliche_structure", "Vacuous filler phrase: 'it goes without saying' (N2)"),
    (r'\bleverage best practices\b', "banned_buzzword", "Corporate buzzword stack: 'leverage best practices' (N2)"),
    (r'\bfuture-proof\b', "banned_buzzword", "Speculative claim: 'future-proof' (N2)"),
    (r'\bswiss army knife\b', "banned_buzzword", "Journalistic cliché: 'swiss army knife' (N2)"),
    (r'\bsilver bullet\b', "banned_buzzword", "Cliché expression: 'silver bullet' (N2)"),
    (r'\brock solid\b', "banned_buzzword", "Informal hyperbole: 'rock solid' (N2)"),
    (r'\bbattle-tested\b', "banned_buzzword", "Unverified claim: 'battle-tested' without production metrics (N2)"),
    (r'\bholistic approach\b', "banned_buzzword", "Vague consulting buzzword: 'holistic approach' (N2)"),
    (r'\bgroundbreaking\b', "banned_buzzword", "Sensationalism: 'groundbreaking' (N2)"),
    (r'\btestament to\b', "banned_buzzword", "Flowery essay flattery: 'testament to' (N8)"),
]

COMPILED_BANNED = [(re.compile(p, re.IGNORECASE), cat, expl) for p, cat, expl in BANNED_BUZZWORDS]

# Trade-offs / Failure Modes / Design Considerations Section Pattern
TRADEOFFS_HEADING_RE = re.compile(
    r'###?.*(?:Trade-offs?|架构设计权衡|权衡|决策反思|Technical Debt|技术债|Failure Modes?|异常冒泡|故障防御|Limit Scenarios?|设计考量|设计取舍|边界处理|边界考量|踩坑点|注意事项|Design Considerations?|Edge Cases?|Failure Scenarios?)',
    re.IGNORECASE
)


@dataclass
class FluffViolation:
    """Represents a specific anti-AI fluff violation found in the document."""
    category: str  # 'banned_buzzword' | 'ungrounded_paragraph' | 'cliche_structure' | 'missing_tradeoffs'
    line_number: int
    matched_text: str
    explanation: str


@dataclass
class FluffAuditResult:
    """Aggregate result of anti-AI fluff auditing."""
    fluff_free_index: float  # 0.0 to 100.0
    penalty_score: float
    violations: List[FluffViolation] = field(default_factory=list)
    banned_buzzword_count: int = 0
    ungrounded_paragraph_count: int = 0
    cliche_structure_count: int = 0
    missing_tradeoffs: bool = False


def _is_ungrounded_paragraph(paragraph: str) -> bool:
    """
    Checks if a descriptive prose paragraph (>60 chars) contains zero code grounding:
    no inline backticks (`code`), no brackets ([path]), no file extension tokens.
    Excludes markdown headings, tables, blockquotes, and lists.
    """
    p = paragraph.strip()
    if len(p) <= 60:
        return False
    # Skip markdown structural blocks
    if p.startswith("#") or p.startswith("|") or p.startswith(">") or p.startswith("```"):
        return False
    if p.startswith("- ") or p.startswith("* ") or re.match(r'^\d+\.\s', p):
        return False

    # Check for code tokens, file paths, line anchors, or brackets
    has_backtick = "`" in p
    has_anchor = bool(re.search(r'\[[a-zA-Z0-9_\-\./\\]+(?:#L\d+)?\]', p))
    has_file_ext = bool(re.search(r'\b[a-zA-Z0-9_\-]+\.(?:py|go|rs|ts|js|c|cpp|h|md|json|yaml|toml)\b', p))
    has_func_call = bool(re.search(r'\b[a-zA-Z0-9_]+\([^\)]*\)', p))

    if not (has_backtick or has_anchor or has_file_ext or has_func_call):
        return True

    return False


def detect_fluff(text: str) -> FluffAuditResult:
    """
    Scans a Markdown document text for AI fluff violations and computes the Fluff-Free Index (FFI).
    Formula:
        Penalty = 5 * BannedBuzzwords + 8 * UngroundedParagraphs + 4 * ClicheStructures + (10 if MissingTradeoffs else 0)
        FFI = max(0.0, 100.0 - Penalty)
    """
    violations: List[FluffViolation] = []
    lines = text.splitlines()

    banned_count = 0
    cliche_count = 0
    ungrounded_count = 0

    # 1. Scan line-by-line for banned buzzwords & clichés
    in_code_block = False
    for line_idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        for regex, cat, expl in COMPILED_BANNED:
            for match in regex.finditer(line):
                matched_str = match.group(0)
                violations.append(FluffViolation(
                    category=cat,
                    line_number=line_idx,
                    matched_text=matched_str,
                    explanation=expl
                ))
                if cat == "banned_buzzword":
                    banned_count += 1
                elif cat == "cliche_structure":
                    cliche_count += 1

    # 2. Scan paragraphs for ungrounded prose blocks
    paragraphs = text.split("\n\n")
    for para in paragraphs:
        if _is_ungrounded_paragraph(para):
            # Locate approximate line number
            first_line = para.strip().splitlines()[0]
            line_no = 1
            for l_idx, l in enumerate(lines, start=1):
                if first_line in l:
                    line_no = l_idx
                    break
            snippet = para.strip()[:60] + "..."
            violations.append(FluffViolation(
                category="ungrounded_paragraph",
                line_number=line_no,
                matched_text=snippet,
                explanation="Descriptive paragraph (>60 chars) contains zero code anchors, backticks, or file paths (N2/N6)"
            ))
            ungrounded_count += 1

    # 3. Check for mandatory Trade-offs & Failure Modes
    has_tradeoffs = bool(TRADEOFFS_HEADING_RE.search(text))
    missing_tradeoffs = not has_tradeoffs

    if missing_tradeoffs:
        violations.append(FluffViolation(
            category="missing_tradeoffs",
            line_number=1,
            matched_text="Document Root",
            explanation="Missing mandatory 'Architecture Trade-offs' or 'Failure Modes & Defenses' section (N8)"
        ))

    # 4. Compute penalty and Fluff-Free Index (FFI)
    penalty = (5.0 * banned_count) + (8.0 * ungrounded_count) + (4.0 * cliche_count) + (10.0 if missing_tradeoffs else 0.0)
    ffi = max(0.0, round(100.0 - penalty, 1))

    return FluffAuditResult(
        fluff_free_index=ffi,
        penalty_score=round(penalty, 1),
        violations=violations,
        banned_buzzword_count=banned_count,
        ungrounded_paragraph_count=ungrounded_count,
        cliche_structure_count=cliche_count,
        missing_tradeoffs=missing_tradeoffs
    )
