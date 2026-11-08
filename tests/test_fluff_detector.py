"""tests.test_fluff_detector: Comprehensive Test Suite for Anti-AI Fluff Linter.

Tests:
- 52-term banned buzzwords scanner across Chinese and English terms
- Cliche structural boilerplates (总的来说, 综上所述, in conclusion)
- Ungrounded prose paragraphs (>60 chars without backticks/anchors/file paths)
- Properly grounded paragraphs (with backticks/anchors) are NOT flagged
- Trade-offs section presence vs absence penalty
- Fluff-Free Index (FFI) mathematical penalty formulation
"""

import pytest

from repo_mentor.verification.fluff_detector import detect_fluff


def test_detect_chinese_banned_buzzwords():
    content = """
    # 架构说明
    本项目采用了非常优雅的设计，整体结构功能强大且灵活。
    作者的代码功底非常深厚，实现了业界领先的架构。
    通过无缝集成各个组件，体现了作者的巧妙权衡。
    ### 架构设计权衡 (Trade-offs)
    这里分析了权衡。
    """
    res = detect_fluff(content)
    categories = [v.category for v in res.violations]
    matched = [v.matched_text for v in res.violations]

    assert "banned_buzzword" in categories
    assert res.banned_buzzword_count >= 4
    assert res.fluff_free_index < 90.0


def test_detect_english_banned_buzzwords():
    content = """
    # Architecture Overview
    This repository is a robust and scalable solution with cutting-edge capabilities.
    It seamlessly integrates with third-party libraries and provides a state-of-the-art framework.
    Truly a game-changer built with a comprehensive suite of tools.
    ### Architecture Trade-offs
    Discussion of latency vs memory.
    """
    res = detect_fluff(content)
    assert res.banned_buzzword_count >= 4
    assert res.fluff_free_index < 90.0


def test_detect_cliche_structures():
    content = """
    # Summary
    值得注意的是，系统会自动执行重试。
    总的来说，该模块协调各部分工作。
    综上所述，毋庸置疑这是核心逻辑。
    In conclusion, we can dive deep into the implementation.
    ### Trade-offs
    Details.
    """
    res = detect_fluff(content)
    assert res.cliche_structure_count >= 4


def test_ungrounded_paragraph_detection():
    # Long paragraph (>60 chars) with NO backticks, NO file paths, NO line numbers
    ungrounded_text = (
        "This is an entirely abstract paragraph explaining how the high level "
        "orchestration system dispatches user events across the internal subsystems "
        "without any single reference to files or functions or line numbers whatsoever."
    )
    doc = f"# Title\n\n{ungrounded_text}\n\n### Trade-offs\nDetails.\n"
    res = detect_fluff(doc)
    assert res.ungrounded_paragraph_count == 1
    assert any(v.category == "ungrounded_paragraph" for v in res.violations)


def test_grounded_paragraph_is_not_penalized():
    # Long paragraph (>60 chars) containing backticked symbol and path anchor
    grounded_text = (
        "The ingress subsystem in `mem0/memory/main.py#L760` processes messages "
        "via `Memory.add()` before delegating to the persistence layer."
    )
    doc = f"# Title\n\n{grounded_text}\n\n### Trade-offs\nMemory vs latency.\n"
    res = detect_fluff(doc)
    assert res.ungrounded_paragraph_count == 0


def test_missing_tradeoffs_penalty():
    doc_without_tradeoffs = """
    # Title
    A concise grounded document referencing `engine.py#L10`.
    """
    res = detect_fluff(doc_without_tradeoffs)
    assert res.missing_tradeoffs is True
    assert any(v.category == "missing_tradeoffs" for v in res.violations)
    # 10 points penalty for missing trade-offs
    assert res.penalty_score >= 10.0
    assert res.fluff_free_index <= 90.0


def test_fluff_free_perfect_document():
    doc = """
    # Architecture
    The core engine `Engine.ServeHTTP` in [`gin.go#L691-L708`] delegates to
    `allocateContext()` in `gin.go#L266` before routing via `tree.go#L418`.

    ### Architecture Trade-offs & Failure Modes
    - [Verified Fact] Prefix radix tree routing trades dynamic regex flexibility for O(k) zero-alloc performance.
    """
    res = detect_fluff(doc)
    assert res.banned_buzzword_count == 0
    assert res.ungrounded_paragraph_count == 0
    assert res.cliche_structure_count == 0
    assert res.missing_tradeoffs is False
    assert res.penalty_score == 0.0
    assert res.fluff_free_index == 100.0
