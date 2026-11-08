<div align="center">

# Repo Mentor

### Universal Open-Source Codebase Deep-Reading & Architectural Analysis Assistant

<p align="center">
  <a href="README.md"><b>English</b></a> •
  <a href="README_zh.md"><b>简体中文</b></a>
</p>

[![CI](https://github.com/Asstar-X/repo-mentor/actions/workflows/ci.yml/badge.svg)](https://github.com/Asstar-X/repo-mentor/actions)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: Ruff](https://img.shields.io/badge/Code%20Style-Ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Typing: Mypy](https://img.shields.io/badge/Typing-Mypy-blue.svg)](https://mypy-lang.org/)
[![Agent Skill Ready](https://img.shields.io/badge/Agent%20Skill-Claude%20%7C%20Antigravity%20%7C%20Cursor%20%7C%20Codex-orange.svg)](SKILL.md)
[![Security Policy](https://img.shields.io/badge/Security-Untrusted%20Repo%20Hardened-red.svg)](SECURITY.md)

<p align="center">
  <b>Turn complex, unfamiliar codebases into crystal-clear, verified architectural blueprints.</b><br/>
  AST-grounded fact citations • Zero "AI-flavor" fluff • Golden path execution tracing • 100-point rubric verification.
</p>

[Quickstart](#quickstart) •
[Why Generic LLM Summaries Fail](#the-problem-why-generic-llm-code-summaries-fail) •
[Architecture](#dual-mode-architecture) •
[CLI Commands](#cli-command-reference) •
[Agent Skill](#agent-skill-interface) •
[Anti-AI Methodology](#anti-ai-reading-methodology--100-point-rubric) •
[Benchmarks](#multi-sample-benchmark-preview)

</div>

---

## The Problem: Why Generic LLM Code Summaries Fail

When developers ask standard LLMs or AI assistants to explain a 50,000-line unfamiliar repository, the results almost always disappoint. Standard AI chats suffer from four fatal failure modes:

<div align="center">
  <img src="assets/en1.png" alt="Reading Legacy Code: Common Pain Points" width="900" />
</div>

| Dimension | Generic LLM Summaries & Chatbots | Repo Mentor Engineering Engine |
| :--- | :--- | :--- |
| **Fact Grounding** | Fabricated line numbers, hallucinated API names, and superficial bullet points. | **AST-grounded citations**: exact file paths, line ranges, and verified symbol signatures (`path/to/file.py:42-88`). |
| **Tone & Style** | Heavy "AI-flavor": empty praise, buzzwords ("seamlessly integrates", "cutting-edge architecture"). | **Zero-fluff engineering prose**: Banned buzzword linting, factual constraints, and concrete counterexamples. |
| **Execution Flow** | Isolated file summaries; loses the dynamic data flow across boundaries. | **Golden path execution tracing**: end-to-end request lifecycle from entrypoint to storage with sequence DAGs. |
| **Architectural Depth** | Describes *what* the code does line-by-line without explaining *why*. | **Trade-offs & Failure modes**: concurrency races, memory footprints, consistency guarantees, and failure domains. |
| **Mastery Verification** | Dunning-Kruger trap: asking 3 easy questions gives a false sense of 100% mastery. | **100-Point Quantitative Rubric**: automated judge auditing grounding rate, hallucination rate, and domain coverage caps. |

---

## Dual-Mode Architecture

`repo-mentor` provides a unified engine designed for two primary operating modes:
1. **Interactive Terminal CLI** (`repo-mentor`): For human engineers needing local analysis, Git hotspot archaeology, dependency graphing, and whitepaper compilation.
2. **Autonomous Agent Skill** (`SKILL.md`): For AI coding agents (Claude Code, Google Antigravity, Cursor, OpenAI Codex), delegating deterministic extraction, AST indexing, and verification to the CLI.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Dual User / Agent Interface                          │
│   Human Developer (CLI: repo-mentor)  │  AI Agent (SKILL.md / Prompts) │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
                    ▼                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      repo_mentor Core Engine                           │
│  ├── CLI Entrypoint (repo_mentor.cli via Typer & Rich)                 │
│  ├── Core Analysis (Scanner, AST Parser, Dependency DAG, Git Hotspots) │
│  ├── Verification Engine (Symbol Anchors, Anti-AI Fluff, Path Check)   │
│  └── Exporter (Dynamic HTML Whitepaper Compiler, Markdown Synthesizer) │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
                    ▼                                ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────┐
│       Anti-AI Methodology & Norms    │  │  Objective Benchmark Suite   │
│  ├── 8 Negative Anti-Patterns (N1-N8)│  │  ├── Python: mem0 (~25k LOC) │
│  ├── 5 Positive Engineering Standards│  │  ├── Go: gin-gonic/gin (~24k)│
│  └── 100-Point Quantitative Rubric   │  │  └── Automated Judge Report  │
└──────────────────────────────────────┘  └──────────────────────────────┘
```

---

## Quickstart

### Installation

Install via `pip`:
```bash
pip install repo-mentor
```

Or run directly without installation via `pipx`:
```bash
pipx run repo-mentor scan .
```

For development and AST multi-language parsing support:
```bash
git clone https://github.com/Asstar-X/repo-mentor.git
cd repo-mentor
pip install -e ".[dev,ast]"
```

### 3-Step Walkthrough

```bash
# 1. Scan codebase topology, entrypoints, and test setups
repo-mentor scan /path/to/target-repo

# 2. Map internal module dependencies into a visual Mermaid DAG
repo-mentor map /path/to/target-repo --mermaid

# 3. Analyze Git churn hotspots to locate architectural gravity
repo-mentor hotspots /path/to/target-repo --top 10
```

---

## CLI Command Reference

The `repo-mentor` CLI provides 8 core subcommands covering the complete codebase analysis lifecycle:

| Subcommand | Syntax | Description |
| :--- | :--- | :--- |
| `scan` | `repo-mentor scan <path>` | Detect languages, frameworks, manifests, entrypoint files, and test harnesses. |
| `map` | `repo-mentor map <path> [--mermaid]` | Extract internal intra-repo module import dependencies and generate topological DAGs. |
| `hotspots` | `repo-mentor hotspots <path> [--top N]` | Compute Git churn revision frequency to isolate architectural gravity centers and debt hotspots. |
| `ast` | `repo-mentor ast <path> [--symbol S]` | Tiered AST parser extracting classes, functions, signatures, and call flows across Python, Go, TS, and Rust. |
| `init` | `repo-mentor init <path>` | Scaffold structured study directories, domain coverage tracking tables, and report templates. |
| `verify` | `repo-mentor verify [repo] [notes] [--fix] [--strict]` | Deterministically audit file paths and line number bounds cited in analysis notes against physical disk files (with optional auto-repair). |
| `eval` | `repo-mentor eval [repo] <report> [--format rich\|json] [--strict]` | 100-point quantitative rubric evaluation judge auditing grounding rate, hallucination count, and fluff score. |
| `export` | `repo-mentor export <study-dir> [--out file.html]` | Compile notes, sequence flows, and Mermaid diagrams into a self-contained, interactive single-file HTML whitepaper. |

---

## Modular Agent Skills Suite

`repo-mentor` implements the universal **Agent Skills** specification following **Andrej Karpathy's minimalist engineering principles**. The suite is structured as **1 Master Orchestrator + 5 Modular Domain Skills**, enforcing strict single-responsibility boundaries and zero information redundancy:

```
repo-mentor/
├── SKILL.md                          # [Master Entry] Orchestrates 5-level cognitive zooming and sub-skills
├── skills/                           # [Modular Skills Suite] 5 dedicated, single-responsibility skills
│   ├── repo-recon/SKILL.md           # Module 1: Macro architecture reconnaissance & cast modeling (Level 1-2)
│   ├── repo-trace/SKILL.md           # Module 2: Concrete data journey & golden path call tracing (Level 3)
│   ├── repo-deepdive/SKILL.md        # Module 3: Keystone FSM, load-bearing code & What-If limit drills (Level 4-5)
│   ├── repo-verify/SKILL.md          # Module 4: Code anchor audit, Mermaid self-healing & anti-fluff gate
│   └── repo-export/SKILL.md          # Module 5: Study synthesis & single-file offline HTML compiler
```

### 5 Dedicated Skill Modules & Slash Command Mapping

| Modular Skill | Primary Command | Zooming Level | Core Responsibility & Boundary |
| :--- | :--- | :--- | :--- |
| **[`repo-recon`](skills/repo-recon/SKILL.md)** | `/overview`, `/guide` | **Level 1 & 2** (Macro) | Real-world agony, first-principles tension, 5-archetype classification, cast of 3~5 characters, Git hotspots. **Zero microscopic code lines**. |
| **[`repo-trace`](skills/repo-trace/SKILL.md)** | `/trace` | **Level 3** (Data Journey) | Single concrete living input walkthrough, station-by-station payload diff, 5-phase golden path sequence, sync/async hops. |
| **[`repo-deepdive`](skills/repo-deepdive/SKILL.md)** | `/deep-dive`, `/core`, `/drill` | **Level 4 & 5** (Hardcore & Tradeoffs) | Keystone entity structs, lifecycle state machine (`stateDiagram-v2`), 3~8 load-bearing code lines, destructive What-If disaster drills, trade-offs. |
| **[`repo-verify`](skills/repo-verify/SKILL.md)** | `/verify` | **Quality Gate** (Grounding) | Deterministic static audit of cited physical file paths, line bounds within EOF, Mermaid syntax auto-healing, and 52 banned buzzwords filter. |
| **[`repo-export`](skills/repo-export/SKILL.md)** | `/export` | **Deliverable** (Whitepaper) | Multi-slice knowledge deduplication and synthesis into a single-file, zero-CDN offline interactive HTML whitepaper. |
| *Progress Dashboard* | `/tracker` | *Coverage* | Clean binary domain checklist (Explored vs. Blind Spot). |

### Agent Installation

#### Claude Code
```bash
# Global installation:
mkdir -p ~/.claude/skills
git clone https://github.com/Asstar-X/repo-mentor.git ~/.claude/skills/repo-mentor
```

#### Google Antigravity
```bash
mkdir -p ~/.gemini/config/skills
git clone https://github.com/Asstar-X/repo-mentor.git ~/.gemini/config/skills/repo-mentor
```

#### Cursor & Windsurf
```bash
mkdir -p .cursor/skills
git clone https://github.com/Asstar-X/repo-mentor.git .cursor/skills/repo-mentor
```

---

## Anti-AI Reading Methodology & 100-Point Rubric

### 5 Positive Engineering Standards
1. **Fact Grounding (P1)**: Every assertion must reference physical file paths and exact line spans (`mem0/memory/main.py:120-145`).
2. **System Invariants (P2)**: Explicitly identify state constraints, locking semantics, and consistency guarantees.
3. **Golden Path (P3)**: Unpack the primary operational sequence from external entrypoint down to low-level persistence.
4. **Architectural Trade-offs (P4)**: Document explicit engineering compromises (throughput vs. latency, memory vs. simplicity).
5. **Failure Modes & Edge Cases (P5)**: Audit error boundaries, reconnect strategies, rate-limiting, and crash recovery.

### 8 Negative Anti-Patterns (N1-N8)
- **N1 (Superficial File Listing)**: Reciting directory trees without explaining inter-module data contracts.
- **N2 (Hallucinated Line Numbers)**: Inventing or guessing line spans that do not match physical disk files.
- **N3 (Boilerplate Fixation)**: Slogging through configuration parsing and logger initialization instead of core business logic.
- **N4 (Uncritical Buzzword Fluff)**: Using empty superlative adjectives ("seamless", "ultra-fast", "robust", "state-of-the-art").
- **N5 (Missing Trade-off Analysis)**: Presenting architectural decisions as flawless without discussing downsides.
- **N6 (Isolated Component Silos)**: Analyzing classes in isolation without mapping end-to-end cross-module call flows.
- **N7 (Ignored Error & Failure Paths)**: Assuming happy-path execution and ignoring panic recovery or retry bounds.
- **N8 (Dunning-Kruger Blind Spots)**: Claiming full mastery after inspecting only entrypoint wrappers.

### 100-Point Quantitative Rubric

When evaluating reading reports (`repo-mentor eval <repo> <report>`), the automated judge computes an objective score:

$$\text{Final Score} = S_{\text{grounding}} + S_{\text{execution}} + S_{\text{fluff}} + S_{\text{tradeoffs}} - P_{\text{hallucination}}$$

| Metric | Max Points | Measurement Method |
| :--- | :---: | :--- |
| **Fact Grounding Rate** | 30 | Percentage of assertions backed by valid, verifiable file path and line anchors. |
| **Execution Flow Completeness** | 25 | Continuity of sequence hops from entrypoint through intermediate handlers to storage. |
| **Fluff-Free Index** | 25 | Inverse density of banned buzzwords, filler transitions, and ungrounded paragraphs. |
| **Architectural Trade-off Depth** | 20 | Explicit presence of trade-off evaluations, concurrency constraints, and failure modes. |
| **Hallucination Penalty** | -10 per hit | Deterministic penalty for non-existent files, invalid line spans, or phantom symbols. |

- **Grade A (High-Star Standard)**: $\ge 85$ points and $0$ hallucinations.
- **Grade B (Acceptable)**: $70 - 84$ points.
- **Fail**: $< 70$ points or $\ge 2$ hallucinations.

---

## Multi-Sample Benchmark Preview

`repo-mentor` is validated against multi-language, production-grade open-source repositories to guarantee cross-ecosystem objectivity:

```
benchmarks/
├── mem0/             # Python (~25,000 LOC): Multi-vector memory layer for LLMs
└── gin-gonic/gin/    # Go (~24,000 LOC): High-performance Radix-tree HTTP web engine
```

### Benchmark Scorecard (Representative Run)

| Target Repository | Ecosystem | Fact Grounding | Hallucination Count | Fluff-Free Index | Total Rubric Score | Grade |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`mem0ai/mem0`** | Python | 96.4% | **0** | 94.2 / 100 | **92.5 / 100** | **Grade A** |
| **`gin-gonic/gin`** | Go | 95.1% | **0** | 93.8 / 100 | **91.0 / 100** | **Grade A** |
| *Generic AI Chat Baseline* | Python / Go | 38.2% | 14 | 41.0 / 100 | 28.5 / 100 | **Fail** |

---

## Security & Untrusted Code Hardening

When analyzing external repositories, safety is non-negotiable:
- **Untrusted Input Ingestion**: All files, commit messages, and docstrings inside target repositories are treated strictly as **untrusted data**. Prompt injection attempts embedded in code comments are completely ignored.
- **Read-Only Static Analysis**: Analysis engines perform passive inspection. They never invoke build hooks (`npm postinstall`, `setup.py`, `Makefile`, arbitrary shell scripts).
- **Anti-Traversal Protection**: All path anchors enforce strict repository root containment (`Path.resolve()`), preventing `../../` directory traversal attacks.
- **Data Confinement**: Study whitepapers and local notes in `studies/` are excluded by `.gitignore` by default to prevent proprietary code leakage.

See [SECURITY.md](SECURITY.md) for our complete security model.

---

## Contributing

Contributions are welcome! Please review [CONTRIBUTING.md](CONTRIBUTING.md) for code style (Ruff, Mypy), test guidelines, and our anti-AI engineering standards.

---

## License

This project is licensed under the [MIT License](LICENSE).
