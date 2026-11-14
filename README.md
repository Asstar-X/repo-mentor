# Repo Mentor

> **Reconstruct the author's mental model, never recite their syntax.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Agent Skill](https://img.shields.io/badge/Agent_Skill-SKILL.md-FF6F00.svg)](SKILL.md)

[English](README.md) • [简体中文](README_zh.md)

---

`repo-mentor` is a codebase deep-reading engine designed for developers and AI coding agents.

When navigating an unfamiliar repository with tens of thousands of lines of code, engineers and generic LLMs alike often get lost in granular implementation details while missing the overarching system mental model.

`repo-mentor` acts like a senior colleague sitting right next to you: **plain-language explanations, grounded causal logic, explicit design trade-offs, and zero marketing buzzwords or AI fluff.** It separates looking inward at load-bearing implementations from looking outward at end-to-end call paths, backed by deterministic static-analysis CLI tools and offline interactive HTML whitepaper exports.

---

## Core Skills & Command Matrix

Skill names correspond directly to slash commands. Use them directly within any Agent Skills-compatible chat interface:

| Command | Perspective | Purpose |
| :--- | :---: | :--- |
| **`/repo-recon`** | System Overview | **What the project does & how to run it**: real-world pain points, minimal run commands, directory triage, and recommended reading entrypoints. |
| **`/repo-core <target>`** | Looking Inward | **How this component works under the hood**: plain-language responsibility, internal stages, load-bearing code snippets, and boundary defenses. |
| **`/repo-trace <target>`** | Looking Outward | **How it behaves in living runtime scenarios**: triggers, upstream/downstream flow, a concrete data sample walkthrough, and error propagation. |
| **`/repo-drill [target]`** | Mastery Check | **Peer drill & review**: 2–3 sharp questions on design intent, data journeys, and breaking points, followed by objective review. |
| **`/repo-brainstorm [target]`** | Ideation & Expansion | **Knowledge extension & brainstorming**: dive into underlying system mechanisms, architectural alternatives, cross-domain applications, and future evolution. |
| **`/repo-export`** | Deliverable | **Compile offline architecture whitepaper**: synthesize study notes into a fully self-contained single-file interactive HTML manual (zero CDN dependencies). |

---

## Quickstart

### 1. Install CLI Engine

The local CLI handles deterministic tasks such as repository scanning, Git churn analysis, AST indexing, and offline whitepaper compilation:

```bash
# Clone and install
git clone https://github.com/Asstar-X/repo-mentor.git
cd repo-mentor
pip install -e .

# Optional: with multi-language AST support (Tree-sitter)
pip install -e ".[ast]"
```

### 2. Using as an Agent Skill

Clone this repository into your agent's skills directory to enable it globally or per-project:

```bash
# Claude Code (personal skills directory):
git clone https://github.com/Asstar-X/repo-mentor.git ~/.claude/skills/repo-mentor

# Antigravity / Cursor / Qoder environments:
# Place under your workspace's skills/repo-mentor, or point configuration to the root SKILL.md
```

Type `/repo-recon` in chat to begin reading unfamiliar repositories.

---

## CLI Reference

In addition to conversational Agent Skills, `repo-mentor` provides a fast terminal CLI:

```bash
# 1. Scan ecosystem, entrypoints, and test layout
repo-mentor scan /path/to/target-repo

# 2. Extract package dependency topology and generate a Mermaid DAG
repo-mentor map /path/to/target-repo --mermaid

# 3. Analyze Git churn to locate architectural gravity centers
repo-mentor hotspots /path/to/target-repo --commits 300 --top 10

# 4. Extract symbols and call invocations (Python, Go, TypeScript, Rust)
repo-mentor ast /path/to/target-repo src/core/engine.py --calls

# 5. Scaffold a structured study workspace
repo-mentor init studies/target-repo --repo /path/to/target-repo

# 6. Compile into a single-file offline interactive HTML whitepaper
repo-mentor export studies/target-repo --out whitepaper.html
```

---

## Reading Methodology

Four focused guides under [`methodology/`](methodology/) serve as on-demand thinking tools for both agents and human developers:

- [01. Project Reconnaissance & Evolution Hotspots](methodology/01-recon-and-hotspots.md): Build mental models in minutes using the "30-line script test", genesis commits archaeology, and Git power-law churn hotspots.
- [02. Core Implementation & State Invariant Analysis](methodology/02-core-analysis.md): Filter out the 80% glue code to focus on the 20% load-bearing logic, state machine invariants, and boundary defenses.
- [03. Call Tracing & Mastery Comprehension Drills](methodology/03-tracing-and-drill.md): Track data changes across steps via Payload Diff, combined with Why/Journey/What-If drill questioning.
- [04. Knowledge Extension & Tech Brainstorming](methodology/04-brainstorm.md): Venture beyond current code to explore underlying runtime principles, alternative architectural trade-offs, and cross-domain transfer.

---

## License

[MIT License](LICENSE)
