"""tests.test_adversarial_challenger_1: Adversarial Stress Tests for Verification Engines.

Empirical verification suite designed by Challenger 1 (Adversarial Fluff & Anchor Challenger).
Stress-tests:
1. Anti-AI Fluff Detector:
   - Exhaustive coverage of all 52 banned terms (Chinese & English)
   - Obfuscated markdown formatting (bold, italics, punctuation, mixed casing)
   - Code block immunity (fenced code containing buzzwords is not penalized)
   - Ungrounded paragraph detection boundary (60 vs 61 characters) and grounding exceptions
   - Zero false-positives on dense, complex engineering whitepaper text
   - Mandatory trade-offs section variations and absence penalties
2. Semantic Anchor Verifier:
   - Out-of-bounds line ranges (past EOF, inverted lines, line 0)
   - Phantom symbol detection in AST with diagnostic reporting
   - Shifted symbol citations outside +-15 lines drift tolerance
   - Minor drift handling and in-place line range auto-repair (--fix)
   - Missing files, empty files, and directory references
3. Mermaid Diagram Verifier:
   - Detection of unclosed quotes, unquoted parens, reserved :: in state transitions, and reserved 'end'
   - Automated syntax repair and round-trip re-verification
"""

from __future__ import annotations

from pathlib import Path

import pytest

from repo_mentor.verification.anchor_verifier import (
    AnchorItem,
    AnchorVerifier,
    audit_markdown_anchors,
)
from repo_mentor.verification.fluff_detector import (
    BANNED_BUZZWORDS,
    detect_fluff,
)
from repo_mentor.verification.mermaid_verifier import (
    lint_mermaid_code,
    repair_mermaid_code,
    verify_study_mermaid,
)

# ==============================================================================
# Domain 1: Adversarial Anti-AI Fluff Linter Tests
# ==============================================================================


class TestAdversarialFluff:
    """Adversarial stress-tests for repo_mentor.verification.fluff_detector."""

    ALL_52_SAMPLE_PHRASES = [
        # Chinese terms (26)
        ("非常优雅的设计", "优雅的设计/非常优雅"),
        ("功能强大且灵活", "功能强大且灵活"),
        ("无缝集成到下游管道", "无缝集成"),
        ("该模块极具扩展性", "极具扩展性"),
        ("达到了业界领先的技术水准", "业界领先"),
        ("各组件浑然一体", "浑然一体"),
        ("其重要性不言而喻", "不言而喻"),
        ("该工具应运而生", "应运而生"),
        ("在整体架构中举足轻重", "举足轻重"),
        ("系统遵循高内聚低耦合原则", "高内聚低耦合"),
        ("采用企业级设计方案", "企业级设计"),
        ("具备健壮的异常处理逻辑", "健壮的异常处理"),
        ("作者的代码功底非常深厚", "代码功底非常深厚"),
        ("总的来说这是一个好方案", "总的来说"),
        ("综上所述系统已就绪", "综上所述"),
        ("值得注意的是必须配置密钥", "值得注意的是"),
        ("毋庸置疑这是核心机制", "毋庸置疑"),
        ("不仅如此，而且支持异步", "不仅如此而且"),
        ("今天我们来一起学习其架构", "今天我们来一起学习"),
        ("首先，加载配置，其次，初始化，再次，启动", "机械枚举"),
        ("提供开箱即用的体验", "开箱即用"),
        ("展现出卓越的性能", "卓越的性能"),
        ("是不可或缺的组件", "不可或缺"),
        ("显而易见设计很直观", "显而易见"),
        ("众所周知这是通用模式", "众所周知"),
        ("体现了架构师的巧妙权衡", "巧妙权衡"),
        # English terms (26)
        ("a robust and scalable architecture", "robust and scalable"),
        ("cutting-edge capabilities", "cutting-edge"),
        ("seamlessly integrates with backends", "seamlessly integrates"),
        ("state-of-the-art memory layout", "state-of-the-art"),
        ("a comprehensive suite of tools", "comprehensive suite"),
        ("carefully engineered structures", "carefully engineered"),
        ("a true game-changer in this domain", "game-changer"),
        ("works out of the box with zero config", "out of the box"),
        ("industry-leading performance benchmarks", "industry-leading"),
        ("highly modular and extensible core", "highly modular and extensible"),
        ("elegantly designed protocol interfaces", "elegantly designed"),
        ("blazingly fast binary decoding", "blazingly fast"),
        ("crystal clear code comments", "crystal clear"),
        ("without a doubt the most reliable", "without a doubt"),
        ("in conclusion the design satisfies R1", "in conclusion"),
        ("let us dive deep into the dispatcher", "dive deep into"),
        ("it goes without saying that safety comes first", "it goes without saying"),
        ("leverage best practices across all modules", "leverage best practices"),
        ("a future-proof abstraction", "future-proof"),
        ("the swiss army knife of parsers", "swiss army knife"),
        ("there is no silver bullet here", "silver bullet"),
        ("a rock solid connection pool", "rock solid"),
        ("a battle-tested concurrency primitive", "battle-tested"),
        ("a holistic approach to lifecycle management", "holistic approach"),
        ("groundbreaking storage mechanism", "groundbreaking"),
        ("a testament to clean software craftsmanship", "testament to"),
    ]

    def test_all_52_banned_buzzwords_detected_individually(self):
        """Stress-test: Verify that every single term in the 52-term blacklist is actively detected."""
        assert len(self.ALL_52_SAMPLE_PHRASES) == 52
        assert len(BANNED_BUZZWORDS) == 52

        undetected = []
        for phrase, label in self.ALL_52_SAMPLE_PHRASES:
            doc = (
                f"# Component Overview\n\n"
                f"The system demonstrates {phrase} within `core/engine.py#L10`.\n\n"
                f"### Architecture Trade-offs\n"
                f"Memory vs throughput details.\n"
            )
            res = detect_fluff(doc)
            has_violation = any(
                v.category in ("banned_buzzword", "cliche_structure") for v in res.violations
            )
            if not has_violation:
                undetected.append((phrase, label))

        assert not undetected, f"Failed to detect banned buzzword terms: {undetected}"

    def test_obfuscated_and_formatted_buzzwords(self):
        """Stress-test: Banned buzzwords wrapped in Markdown styling or mixed casing."""
        doc = """
        # Architecture Specification
        - Bold: **非常优雅的设计**
        - Italic: *功能强大且灵活*
        - Mixed casing: A RoBuSt AnD ScAlAbLe solution with CUTTING-EDGE features.
        - Trailing punctuation: 这套方案真正实现了无缝集成！
        - Punctuation wrapping: 「业界领先」的技术规范。

        ### Architecture Trade-offs & Failure Modes
        Analysis of memory footprint.
        """
        res = detect_fluff(doc)
        assert res.banned_buzzword_count >= 5
        assert res.fluff_free_index < 80.0

    def test_code_block_buzzwords_not_penalized(self):
        """Adversarial test: Code blocks containing blacklisted terms must NOT trigger false positives."""
        doc = """
        # Source Inspection

        ```python
        # 非常优雅的设计
        class Optimizer:
            \"\"\"A robust and scalable optimizer.\"\"\"
            def run(self):
                print("功能强大且灵活")
        ```

        ### Architecture Trade-offs
        Grounded discussion in `optimizer.py#L10-L20`.
        """
        res = detect_fluff(doc)
        assert res.banned_buzzword_count == 0
        assert res.cliche_structure_count == 0
        assert res.penalty_score == 0.0
        assert res.fluff_free_index == 100.0

    def test_ungrounded_paragraph_thresholds(self):
        """Stress-test: Verify strict length threshold (>60 chars) and penalty formulation (8.0 pts)."""
        # 60 chars without grounding: NOT flagged
        p60 = "x" * 60
        doc60 = f"# Title\n\n{p60}\n\n### Trade-offs\n`file.py#L1`\n"
        res60 = detect_fluff(doc60)
        assert res60.ungrounded_paragraph_count == 0

        # 61 chars without grounding: MUST be flagged with 8.0 penalty
        p61 = "x" * 61
        doc61 = f"# Title\n\n{p61}\n\n### Trade-offs\n`file.py#L1`\n"
        res61 = detect_fluff(doc61)
        assert res61.ungrounded_paragraph_count == 1
        assert res61.penalty_score == 8.0
        assert res61.fluff_free_index == 92.0

    def test_ungrounded_paragraph_grounding_exceptions(self):
        """Ensure prose with backticks, file extensions, or function calls is recognized as grounded."""
        grounded_cases = [
            "The cluster controller dispatches tasks to `worker_pool.py` according to node CPU utilization.",
            "Configurations are dynamically reloaded from settings.toml whenever a SIGHUP signal is trapped.",
            "The event loop calls handlePacket() upon polling an incoming frame from the socket buffer.",
            "Detailed bounds are enforced by the storage layer [storage/disk.go#L45-L60] before flushing.",
        ]
        for p in grounded_cases:
            assert len(p) > 60
            doc = f"# Title\n\n{p}\n\n### Trade-offs\nDetails.\n"
            res = detect_fluff(doc)
            assert res.ungrounded_paragraph_count == 0, f"False positive ungrounded paragraph: {p}"

    def test_dense_engineering_prose_zero_false_positives(self):
        """Stress-test: Multi-section engineering report with zero buzzwords achieves 100/100 FFI."""
        engineering_report = """
        # Radix Prefix Tree Routing Engine

        ## 1. Primary Ingress Dispatch
        Incoming requests are accepted by `Engine.ServeHTTP` in [`gin.go#L691-L708`].
        The method retrieves a pooled `Context` instance via `allocateContext()` in `gin.go#L266`,
        initializing request parameters before delegating to `Engine.handleHTTPRequest()`.

        ## 2. Path Matching Traversal
        Route lookup traverses the prefix radix tree rooted in [`tree.go#L418-L450`].
        The walker matches the incoming path segment byte-by-byte:
        - Exact prefix match advances down `node.children`.
        - Parameter wildcards `:param` assign tokens to `c.Params` without heap reallocation.
        - Catch-all wildcards `*filepath` bind the remaining path tail.

        ## 3. Handler Chain Abort Semantics
        Middleware execution proceeds sequentially via `c.Next()`. If any handler calls
        `c.AbortWithStatus(http.StatusUnauthorized)`, `c.index` is immediately set to
        `abortIndex = math.MaxInt8 / 2`, stopping further execution.

        ### Architecture Trade-offs & Failure Modes
        - [Trade-off] Radix Tree vs Hash Table: Radix trees provide O(k) path lookup and prefix compression,
          avoiding memory allocations during requests, at the expense of non-trivial insertion complexity.
        - [Failure Mode] Unbounded Body Reads: Handlers reading large payloads must configure `http.MaxBytesReader`
          to prevent socket exhaustion under high concurrency.
        """
        res = detect_fluff(engineering_report)
        assert res.banned_buzzword_count == 0
        assert res.ungrounded_paragraph_count == 0
        assert res.cliche_structure_count == 0
        assert res.missing_tradeoffs is False
        assert res.penalty_score == 0.0
        assert res.fluff_free_index == 100.0

    def test_missing_tradeoffs_variations_and_penalty(self):
        """Verify that absence of trade-offs section adds 10 pts penalty, while supported headings pass."""
        # Missing
        doc_no = "# Title\n\nReferencing `core.py#L10`."
        res_no = detect_fluff(doc_no)
        assert res_no.missing_tradeoffs is True
        assert res_no.penalty_score == 10.0

        # Valid English heading
        doc_en = "# Title\n\nReferencing `core.py#L10`.\n\n### Architecture Trade-offs\nDiscussion."
        assert detect_fluff(doc_en).missing_tradeoffs is False

        # Valid Chinese heading
        doc_zh = (
            "# Title\n\nReferencing `core.py#L10`.\n\n### 架构设计权衡 (Trade-offs)\nDiscussion."
        )
        assert detect_fluff(doc_zh).missing_tradeoffs is False

        # Valid Failure Modes heading
        doc_fm = "# Title\n\nReferencing `core.py#L10`.\n\n### Failure Modes & Limit Scenarios\nDiscussion."
        assert detect_fluff(doc_fm).missing_tradeoffs is False


# ==============================================================================
# Domain 2: Adversarial Semantic Anchor Verifier Tests
# ==============================================================================


class TestAdversarialCodeAnchor:
    """Adversarial stress-tests for repo_mentor.verification.anchor_verifier."""

    @pytest.fixture
    def test_environment(self, tmp_path: Path):
        """Sets up a fixture repository with Python source files."""
        repo = tmp_path / "target_repo"
        repo.mkdir()

        py_content = (
            '"""Dispatcher module."""\n'
            "import time\n"
            "\n"
            "class TaskDispatcher:\n"
            '    """Dispatches asynchronous tasks."""\n'
            "    def __init__(self, workers: int):\n"
            "        self.workers = workers\n"
            "\n"
            "    def dispatch(self, task_id: str) -> bool:\n"
            "        return True\n"
            "\n"
            "def calculate_checksum(data: bytes) -> int:\n"
            "    return sum(data) % 256\n"
            "\n"
        ) + "\n".join(f"def helper_fn_{i}(): pass" for i in range(1, 50))

        (repo / "dispatcher.py").write_text(py_content, encoding="utf-8")
        return repo

    def test_out_of_bounds_lines_past_eof(self, test_environment: Path):
        """Adversarial test: Valid file path, but line range past EOF."""
        verifier = AnchorVerifier(test_environment)
        # dispatcher.py has ~65 lines; citation requests lines 800-850
        item = AnchorItem(
            raw_text="[dispatcher.py#L800-L850]",
            file_path="dispatcher.py",
            start_line=800,
            end_line=850,
        )
        res = verifier.verify_item(item)
        assert res.is_valid is False
        assert res.file_exists is True
        assert res.lines_valid is False
        assert res.category == "out_of_bounds"
        assert "Line bounds out of range" in res.error_message

    def test_out_of_bounds_inverted_and_zero_lines(self, test_environment: Path):
        """Adversarial test: Inverted line range (L30-L10) and non-positive line (L0)."""
        verifier = AnchorVerifier(test_environment)

        # Inverted line range
        item_inv = AnchorItem(
            raw_text="[dispatcher.py#L30-L10]",
            file_path="dispatcher.py",
            start_line=30,
            end_line=10,
        )
        res_inv = verifier.verify_item(item_inv)
        assert res_inv.is_valid is False
        assert res_inv.category == "out_of_bounds"

        # Line 0 (1-indexed violation)
        item_zero = AnchorItem(
            raw_text="[dispatcher.py#L0-L5]", file_path="dispatcher.py", start_line=0, end_line=5
        )
        res_zero = verifier.verify_item(item_zero)
        assert res_zero.is_valid is False
        assert res_zero.category == "out_of_bounds"

    def test_phantom_symbol_detection(self, test_environment: Path):
        """Adversarial test: Valid file and valid line range, but phantom symbol name."""
        verifier = AnchorVerifier(test_environment)

        # Lines 4-10 contain TaskDispatcher, but citation claims PhantomBroker
        item = AnchorItem(
            raw_text="[dispatcher.py#L4-L10]",
            file_path="dispatcher.py",
            start_line=4,
            end_line=10,
            claimed_symbol="PhantomBroker",
        )
        res = verifier.verify_item(item)
        assert res.is_valid is False
        assert res.file_exists is True
        assert res.lines_valid is True
        assert res.symbol_grounded is False
        assert res.category == "phantom_symbol"
        assert "Claimed symbol 'PhantomBroker' does not span" in res.error_message
        # Should identify that 'TaskDispatcher' was actually found at those lines
        assert "found 'TaskDispatcher' instead" in res.error_message

    def test_symbol_drift_beyond_tolerance(self, test_environment: Path):
        """Adversarial test: Valid symbol in file, but cited 35 lines away (outside +-15 tolerance)."""
        verifier = AnchorVerifier(test_environment)

        # calculate_checksum is defined at line 12.
        # Citing line 50 represents a drift of 38 lines (> 15).
        item = AnchorItem(
            raw_text="[dispatcher.py#L50-L52]",
            file_path="dispatcher.py",
            start_line=50,
            end_line=52,
            claimed_symbol="calculate_checksum",
        )
        res = verifier.verify_item(item, drift_tolerance=15)
        assert res.is_valid is False
        assert res.symbol_grounded is False
        assert res.category == "phantom_symbol"

    def test_minor_drift_and_auto_repair(self, test_environment: Path, tmp_path: Path):
        """Verify that an anchor pointing inside a symbol's span is repaired to the canonical span."""
        # calculate_checksum is defined at lines 12-13 in test_environment.
        # Markdown points to line 12-12 (partial range notation).
        doc = tmp_path / "study_report.md"
        doc.write_text(
            "# Study\n\n- Helper: `calculate_checksum`: [dispatcher.py#L12-L12]\n", encoding="utf-8"
        )

        audit_before = audit_markdown_anchors(test_environment, doc, fix=False)
        assert audit_before["valid"] is True

        # Perform auto-fix
        audit_fixed = audit_markdown_anchors(test_environment, doc, fix=True)
        assert audit_fixed["valid"] is True

        updated_text = doc.read_text(encoding="utf-8")
        assert "[dispatcher.py#L12-L13]" in updated_text

    def test_empty_file_and_missing_file_handling(self, test_environment: Path):
        """Boundary test: Handling anchors referencing empty files or missing files."""
        empty_path = test_environment / "empty.py"
        empty_path.write_text("", encoding="utf-8")

        verifier = AnchorVerifier(test_environment)

        # Empty file citation
        res_empty = verifier.verify_item(
            AnchorItem(raw_text="[empty.py#L1]", file_path="empty.py", start_line=1, end_line=1)
        )
        assert res_empty.is_valid is False
        assert res_empty.category == "out_of_bounds"

        # Missing file citation
        res_missing = verifier.verify_item(
            AnchorItem(
                raw_text="[non_existent.py#L1]",
                file_path="non_existent.py",
                start_line=1,
                end_line=1,
            )
        )
        assert res_missing.is_valid is False
        assert res_missing.category == "missing_file"


# ==============================================================================
# Domain 3: Adversarial Mermaid Diagram Verifier Tests
# ==============================================================================


class TestAdversarialMermaid:
    """Adversarial stress-tests for repo_mentor.verification.mermaid_verifier."""

    def test_broken_diagram_unclosed_quotes(self):
        """Adversarial test: Detect unclosed quotes in diagram nodes."""
        broken = """graph TD
            A["Unclosed quote node] --> B["Valid Node"]
        """
        issues = lint_mermaid_code(broken)
        assert any(i.rule == "unclosed_quotes" for i in issues)

    def test_broken_diagram_state_transition_colons(self):
        """Adversarial test: Detect reserved '::' scope operators in state transitions."""
        broken = """stateDiagram-v2
            [*] --> Idle
            Idle --> Processing: pipeline::start_event
            Processing --> [*]
        """
        issues = lint_mermaid_code(broken)
        assert any(i.rule == "state_transition_colons" for i in issues)

        repaired = repair_mermaid_code(broken)
        assert "pipeline.start_event" in repaired
        assert not lint_mermaid_code(repaired)

    def test_broken_diagram_unquoted_flowchart_parens(self):
        """Adversarial test: Flowchart nodes with unquoted parentheses and colons."""
        broken = """graph LR
            Client[Browser (HTTPS Client)] --> Proxy[NGINX Gateway:8080]
            Proxy --> Server[Core Service (v2.1)]
        """
        issues = lint_mermaid_code(broken)
        assert any(i.rule == "unquoted_flowchart_label" for i in issues)

        repaired = repair_mermaid_code(broken)
        repaired_issues = lint_mermaid_code(repaired)
        assert not repaired_issues, f"Repaired diagram still has issues: {repaired_issues}"
        assert 'Client["Browser (HTTPS Client)"]' in repaired
        assert 'Server["Core Service (v2.1)"]' in repaired

    def test_broken_diagram_unquoted_sequence_alias(self):
        """Adversarial test: Unquoted participant aliases in sequence diagrams."""
        broken = """sequenceDiagram
            participant S as Storage Backend Cluster
            participant C as Client Ingress Gateway
            C->>S: read()
        """
        issues = lint_mermaid_code(broken)
        assert any(i.rule == "unquoted_participant_alias" for i in issues)

        repaired = repair_mermaid_code(broken)
        assert 'participant S as "Storage Backend Cluster"' in repaired
        assert 'participant C as "Client Ingress Gateway"' in repaired
        assert not lint_mermaid_code(repaired)

    def test_broken_diagram_reserved_keyword_end(self):
        """Adversarial test: Target node ID collision with Mermaid reserved keyword 'end'."""
        broken = """graph TD
            StepA --> StepB
            StepB --> end
        """
        issues = lint_mermaid_code(broken)
        assert any(i.rule == "reserved_node_id" for i in issues)

        repaired = repair_mermaid_code(broken)
        assert '_end_node["End"]' in repaired
        assert not lint_mermaid_code(repaired)

    def test_verify_study_mermaid_directory_and_fix(self, tmp_path: Path):
        """End-to-end test: Scan markdown files on disk, flag errors, and apply automatic repair."""
        doc = tmp_path / "architecture.md"
        doc.write_text(
            "# Architecture\n\n"
            "```mermaid\n"
            "graph TD\n"
            "    Init[Initialize (Config)] --> Run[Run (Loop)]\n"
            "    Run --> end\n"
            "```\n",
            encoding="utf-8",
        )

        # Audit without fix: should fail with detected issues
        res_audit = verify_study_mermaid(doc, fix=False)
        assert res_audit["success"] is False
        assert res_audit["issues_count"] >= 2

        # Audit with fix: should repair file
        res_fix = verify_study_mermaid(doc, fix=True)
        assert res_fix["fixed_files"] == 1

        # Re-audit should succeed with 0 issues
        res_verify = verify_study_mermaid(doc, fix=False)
        assert res_verify["success"] is True
        assert res_verify["issues_count"] == 0
