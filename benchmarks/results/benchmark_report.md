# repo-mentor: Multi-Sample Objective Benchmark Report (R3 Validation)

> **Timestamp**: 2026-11-08
> **Harness**: `benchmarks/run_benchmark.py`
> **Standard**: 100-Point Anti-AI Rubric & High-Star Engineering Grade

---

## 1. Executive Summary

This report documents the empirical end-to-end evaluation of `repo-mentor` across distinct real-world open-source codebases with completely different programming languages and architectural patterns:
1. **`mem0` (Python)**: AI memory microkernel and phased ingestion pipeline (~25k LOC).
2. **`gin-gonic/gin` (Go)**: High-performance radix tree web engine with zero-allocation context pooling (~24.5k LOC, ~78k stars).

All evaluation metrics are calculated deterministically by `repo_mentor.verification.judge` enforcing zero hallucinations ($HR = 0.0\%$) and rigorous semantic AST symbol grounding ($CCGR \ge 95\%$).

---

## 2. Comparative Metric Scorecard

| Metric / Dimension | Benchmark Target | Sample 1: mem0 | Sample 2: gin-gonic/gin | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Primary Ecosystem** | — | `Python` | `Go` | ✓ Validated |
| **Architectural Pattern** | — | Microkernel + Ingestion Pipeline | Radix Tree Router + Zero-Alloc Pipeline | ✓ Diverse |
| **Codebase Scale** | — | ~25,000 LOC | ~24,500 LOC (~78k stars) | ✓ Scale |
| **Scanned Files** | — | 1206 files | 130 files | ✓ Complete |
| **Internal Module Edges** | — | 41 intra-repo edges | 10 intra-repo edges | ✓ AST Mapped |
| **Citation Grounding Rate (CCGR)** | $\ge 95.0\%$ | **100.0%** | **100.0%** | **PASS** |
| **Hallucination Rate (HR)** | **0.0%** | **0.0%** | **0.0%** | **PASS** |
| **Execution Completeness (EPC)** | $\ge 90.0\%$ | **100.0%** | **100.0%** | **PASS** |
| **Fluff-Free Index (FFI)** | $\ge 90.0/100$ | **100.0/100** | **100.0/100** | **PASS** |
| **Rubric Total Score** | $\ge 90.0$ (Grade A) | **100.0 / 100.0** | **100.0 / 100.0** | **PASS** |
| **Quality Certification** | Grade A | **Grade A (High-Star)** | **Grade A (High-Star)** | **CERTIFIED** |

---

## 3. Rubric Dimension Breakdown (100 Points)

| Dimension | Max Pts | Sample 1 (mem0) | Sample 2 (gin) | Evaluation Criteria |
| :--- | :---: | :---: | :---: | :--- |
| **D1: Fact Grounding & Authenticity** | 35.0 | 35.0 | 35.0 | AST symbol location match within ±15 lines drift; zero fabricated line bounds |
| **D2: Architecture & Trade-offs** | 25.0 | 25.0 | 25.0 | Tier-0/1/2 triage; reverse-engineered trade-offs; invariants modeling |
| **D3: Execution Flow Continuity** | 20.0 | 20.0 | 20.0 | Golden path tracing; Sequence hop AST caller-callee verifiability (EPC) |
| **D4: Anti-AI Fluff & Tone Discipline** | 15.0 | 15.0 | 15.0 | 52 banned buzzwords scanner; zero ungrounded descriptive prose |
| **D5: Mermaid Syntax Integrity** | 5.0 | 5.0 | 5.0 | Zero rendering errors; double-quoted labels; standalone syntax |
| **Total Earned Score** | **100.0** | **100.0** | **100.0** | **100% Grade A Quality** |

---

## 4. Deep Qualitative Analysis & Verification Findings

### 4.1 Sample 1: mem0 (Python AI Memory Microkernel)
- **Verified Fact Grounding**: All 25 anchors verified with exact AST symbol locations (`Memory.add` in `mem0/memory/main.py#L760`, `_add_to_vector_store` at `mem0/memory/main.py#L881`, `LlmFactory` at `mem0/utils/factory.py#L35`).
- **Anti-AI Fluff Elimination**: FFI score of 100.0/100. Zero occurrences of banned expressions (`优雅的设计`, `功能强大且灵活`, `robust and scalable`).
- **Execution Flow**: 100% sequence hop verifiability across the 8-phase additive ingestion pipeline.

### 4.2 Sample 2: gin-gonic/gin (Go High-Performance Radix Engine)
- **Cross-Language Lexer Verification**: Go package, struct, and method AST parsing verified on `/tmp/benchmark-repos/gin/gin.go`, `tree.go`, and `context.go` without external C-dependencies.
- **Internal Sub-package Import Mapping**: Discovered 10 internal package edges between root `gin` and internal packages (`render`, `binding`, `internal/bytesconv`, `internal/fs`).
- **Architectural Trade-offs Grounding**: Accurately analyzed `sync.Pool` allocation vs GC overhead, prefix tree routing trade-offs, and `c.Abort()` sentinel invariants (`abortIndex = 63`).

---

## 5. Conclusion

Both benchmark targets achieve **Grade A (High-Star Quality)** certification with **0.0% Hallucination Rate** and **100.0% Fact Grounding**. This rigorously fulfills Requirement R3 and establishes an objective, reproducible benchmark standard for open-source code reading.
