<div align="center">

# Repo Mentor

### Codebase deep-reading assistant with machine-audited facts

<p align="center">
  <a href="README.md"><b>English</b></a> •
  <a href="README_zh.md"><b>简体中文</b></a>
</p>

[![CI](https://github.com/Asstar-X/repo-mentor/actions/workflows/ci.yml/badge.svg)](https://github.com/Asstar-X/repo-mentor/actions)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: Ruff](https://img.shields.io/badge/Code%20Style-Ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Typing: Mypy](https://img.shields.io/badge/Typing-Mypy-blue.svg)](https://mypy-lang.org/)
[![Agent Skill Ready](https://img.shields.io/badge/Agent%20Skill-SKILL.md-orange.svg)](SKILL.md)
[![Security Policy](https://img.shields.io/badge/Security-Untrusted%20Repo%20Hardened-red.svg)](SECURITY.md)

<p align="center">
  <b>Read unfamiliar codebases in plain language. Every citation is checked against the physical files on disk.</b>
</p>

[Quickstart](#quickstart) •
[Demo](#demo) •
[CLI Commands](#cli-command-reference) •
[Agent Skills](#agent-skills-suite) •
[Methodology](#reading-methodology) •
[Scoring](#100-point-rubric) •
[Security](#security)

</div>

---

## Demo

A real whitepaper compiled from [this repository's own study notes](examples/repo-mentor-self/) — 100% citation grounding, 0 hallucinations, Grade A. The HTML is fully self-contained: open it with the network disabled and every diagram still renders.

![Repo Mentor whitepaper demo](assets/whitepaper-demo.png)

## The Problem

Asking a general-purpose LLM to explain a 50,000-line repository usually produces four kinds of disappointment:

| Dimension | Generic LLM summary | Repo Mentor |
| :--- | :--- | :--- |
| **Fact grounding** | Invented line numbers and API names. | Every citation is audited against disk: file exists, lines in bounds, symbol present (`path/to/file.py#L42-L88`). |
| **Tone** | Empty praise and buzzwords. | A buzzword linter and an ungrounded-paragraph detector penalize filler; plain engineering prose is enforced. |
| **Execution flow** | Isolated file summaries. | Traces follow one concrete data sample from external trigger through core logic to output. |
| **Depth** | Recites *what* line by line. | Requires *why*: trade-offs, state invariants, failure modes, and recovery paths. |
| **Mastery check** | Three easy questions create false confidence. | Socratic drills on design intent and breaking points, plus a 100-point rubric with hallucination penalties. |

## Architecture

One engine, two interfaces: a terminal CLI for humans, and an Agent Skills suite for AI coding agents. The agent delegates deterministic work (scanning, AST indexing, verification, compilation) to the CLI.

```
┌────────────────────────────────────────────────────────────┐
│  Human (CLI: repo-mentor)   │   AI Agent (SKILL.md suite)  │
└──────────────┬───────────────────────────┬─────────────────┘
               ▼                           ▼
┌────────────────────────────────────────────────────────────┐
│                    repo_mentor engine                      │
│  core/          scanner · AST parser · dependency DAG ·    │
│                 Git churn hotspots                         │
│  verification/  anchor gates · Mermaid lint/repair ·       │
│                 fluff detector · 100-point judge           │
│  export/        study scaffolding · offline HTML compiler  │
└────────────────────────────────────────────────────────────┘
               ▲                           ▲
┌──────────────┴───────────┐  ┌────────────┴─────────────────┐
│  skills/ (1 + 6 suite)   │  │  methodology/ (4 guides)     │
│  templates/ (3 formats)  │  │  repo_mentor/ (CLI engine)   │
└──────────────────────────┘  └──────────────────────────────┘
```

## Quickstart

### Installation

```bash
# From source (PyPI release pending):
pip install git+https://github.com/Asstar-X/repo-mentor.git

# For development, with multi-language AST support:
git clone https://github.com/Asstar-X/repo-mentor.git
cd repo-mentor
pip install -e ".[dev,ast]"
```

### 3-Step Walkthrough

```bash
# 1. Scan languages, entrypoints, and test layout
repo-mentor scan /path/to/target-repo

# 2. Map internal module dependencies as a Mermaid DAG
repo-mentor map /path/to/target-repo --mermaid

# 3. Find the most-churned files — where the architecture actually lives
repo-mentor hotspots /path/to/target-repo --top 10
```

Then scaffold a study workspace, write notes, and gate them:

```bash
repo-mentor init studies/target-repo --repo /path/to/target-repo
repo-mentor verify /path/to/target-repo studies/target-repo --fix
repo-mentor export studies/target-repo
```

## CLI Command Reference

| Subcommand | Syntax | Description |
| :--- | :--- | :--- |
| `scan` | `repo-mentor scan <path> [--depth N] [--format rich\|json]` | Detect languages, frameworks, manifests, entrypoints, and test harnesses. |
| `map` | `repo-mentor map <path> [--mermaid] [--internal-only] [--out FILE]` | Extract intra-repo import dependencies and generate a topological DAG. |
| `hotspots` | `repo-mentor hotspots <path> [--commits N] [--top N]` | Rank files by Git churn to locate architectural gravity centers. |
| `ast` | `repo-mentor ast <repo> <file-or-dir> [--symbols/--no-symbols] [--calls]` | Extract classes, functions, signatures, and call invocations (Python, Go, TS, Rust). |
| `init` | `repo-mentor init <study-dir> --repo <repo> [--force]` | Scaffold a study workspace pre-filled with live scan, DAG, and hotspot data. |
| `verify` | `repo-mentor verify <repo> <notes> [--fix] [--strict]` | Audit cited file paths, line bounds, and symbols; lint and auto-repair Mermaid. |
| `eval` | `repo-mentor eval <repo> <report> [--format rich\|json] [--strict]` | Score a study report with the 100-point rubric. |
| `export` | `repo-mentor export <study-dir> [--out FILE]` | Compile notes into a self-contained offline HTML whitepaper. |

## Agent Skills Suite

The suite follows the Agent Skills specification: one orchestrator plus six single-responsibility skills. **The skill name is the command name.**

| Skill (command) | Perspective | Mission |
| :--- | :--- | :--- |
| [`repo-recon`](skills/repo-recon/SKILL.md) (`/repo-recon`) | System global | What the project does, how to run it, directory roles, reading roadmap. |
| [`repo-core`](skills/repo-core/SKILL.md) (`/repo-core <target>`) | Looking inward | Purpose, internal steps, load-bearing code, boundary defenses. |
| [`repo-trace`](skills/repo-trace/SKILL.md) (`/repo-trace <target>`) | Looking outward | Real trigger scenarios, upstream/downstream, a sample data journey, error propagation. |
| [`repo-drill`](skills/repo-drill/SKILL.md) (`/repo-drill [target]`) | Peer quiz | 2–3 sharp questions on intent, flow, and breaking points; objective review. |
| [`repo-brainstorm`](skills/repo-brainstorm/SKILL.md) (`/repo-brainstorm [target]`) | Ideation & Expansion | Extend underlying systems knowledge, architectural alternatives, and future evolution. |
| [`repo-export`](skills/repo-export/SKILL.md) (`/repo-export`) | Deliverable | Deduplicate study notes and compile the offline whitepaper. |

### Installation by platform

```bash
# Claude Code (personal skills):
git clone https://github.com/Asstar-X/repo-mentor.git ~/.claude/skills/repo-mentor

# Qoder (project-level skills): clone into your project's skills directory,
# or install user-level under ~/.qoder/skills/repo-mentor
```

Skill discovery differs across agents: some register only the root `SKILL.md`, others register every `skills/*/SKILL.md`. Both work — the root skill links to all six sub-skills and loads them on demand. Commands (`/repo-recon`, `/repo-core`, …) can be triggered directly in chat.

## Reading Methodology

Four guides in [`methodology/`](methodology/) drive the skills. They are loaded on demand, not upfront:

| Guide | Topic |
| :--- | :--- |
| [01](methodology/01-recon-and-hotspots.md) | Project reconnaissance and Git evolution hotspots |
| [02](methodology/02-core-analysis.md) | Core implementation, 80/20 filtering, and state invariant modeling |
| [03](methodology/03-tracing-and-drill.md) | Dynamic call tracing (Payload Diff) and comprehension drills |
| [04](methodology/04-brainstorm.md) | Technical brainstorming and architectural imagination |

## 100-Point Rubric

`repo-mentor eval` scores a study report across five dimensions (implemented in [`judge.py`](repo_mentor/verification/judge.py)):

| Dimension | Max | How it is measured |
| :--- | :---: | :--- |
| **D1 — Fact grounding** | 35 | Citation grounding rate × 30, plus 5 for zero hallucinations; hallucination rate deducts up to 1.5× its percentage. |
| **D2 — Architecture & trade-offs** | 25 | Module triage (10), explicit trade-offs (10), state invariants (5). |
| **D3 — Execution flow** | 20 | Golden-path narrative (10) + verified sequence-diagram hops (10). |
| **D4 — Tone discipline** | 15 | No banned buzzwords (5), no ungrounded paragraphs (5), Fluff-Free Index × 5. |
| **D5 — Mermaid integrity** | 5 | Share of diagrams passing syntax lint. |

The Fluff-Free Index starts at 100 and deducts: 5 per banned buzzword, 8 per ungrounded paragraph, 4 per cliché structure, 10 for a missing trade-offs section.

- **Grade A**: score ≥ 90, zero hallucinations, grounding ≥ 95%, FFI ≥ 90.
- **Grade B**: score ≥ 80, zero hallucinations, grounding ≥ 90%.
- **Fail**: anything else. `--strict` passes only Grade A.

D2/D3 use keyword heuristics — treat the score as a lint signal, not proof of understanding. The deterministic gates (D1, D5) carry the factual burden.

## Security

Analyzing external repositories is treated as handling untrusted input:

- **Read-only static analysis**: engines never execute target-repo code or build hooks (`npm postinstall`, `setup.py`, Makefiles). `git log` is the only subprocess.
- **Prompt-injection resistance**: file contents, commit messages, and docstrings are data, never instructions.
- **Path containment**: anchors resolve inside the repository root; `../../` traversal is rejected.
- **Data confinement**: `studies/` is gitignored by default so proprietary notes never leak into commits.

See [SECURITY.md](SECURITY.md) for the full model.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, code style (Ruff, Mypy), and test guidelines. The docs themselves are gated: `tests/test_docs_smoke.py` executes every documented CLI example against the real command tree.

## License

[MIT](LICENSE). Bundled third-party software (Mermaid.js) is listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).