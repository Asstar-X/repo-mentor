<div align="center">

# Repo Mentor

### 通用开源项目代码深度阅读与架构分析助手

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
  <b>把复杂、庞大、陌生的代码库，转化为清晰、确凿、经得起检验的工程架构蓝图。</b><br/>
  AST 源码事实强锚定 • 彻底剔除“AI味”空洞套话 • 黄金执行链路全景跟踪 • 100分量化客观裁决
</p>

[快速上手](#快速上手) •
[为什么通用 AI 读代码总是让人失望？](#为什么通用-ai-读代码总是让人失望) •
[双形态架构](#双形态架构) •
[CLI 命令速查](#cli-命令行工具速查) •
[Agent Skill 工作流](#agent-skill-工作流) •
[反“AI味”方法论与 100 分量化评分](#反ai味方法论与-100-分量化评测体系) •
[基准实测](#开源标杆项目实测-benchmark)

</div>

---

## 为什么通用 AI 读代码总是让人失望？

当开发者让 ChatGPT、Claude 或通用代码助手解释一个几万行、甚至数十万行的陌生项目时，输出的结果往往差强人意。普遍存在五大致命痛点：

<div align="center">
  <img src="assets/en1.png" alt="阅读老代码与大型项目的痛点" width="900" />
</div>

| 维度 | 通用大模型摘要与常规 Chat 机器人 | Repo Mentor 专业工程分析引擎 |
| :--- | :--- | :--- |
| **代码事实锚定** | 臆造不存在的函数名、胡编行号区间，只给泛泛的代码块概括。 | **严格基于 AST 事实索引**：强制标注物理文件路径、准确行号与真实符号签名（如 `path/to/file.py:42-88`），容差超标即判定幻觉。 |
| **语言风格与深度** | 严重的“AI味”套话：“顾名思义”、“不言而喻”、“起到了承上启下的关键作用”、“无缝集成”。 | **纯正硬核工程语言**：内置 52 项禁词黑名单检测，杜绝无事实支撑的空洞吹捧与套路化废话。 |
| **执行链路穿透** | 单文件孤立解释，只见树木不见森林；跨模块数据流与调用时序断裂。 | **全流程执行链路追踪**：从外部请求入口直通核心处理与交付输出，还原完整拓扑图与调用序列。 |
| **架构权衡深度** | 逐行复述“代码做了什么”，却解释不清“为什么这么设计”。 | **架构权衡（Trade-offs）与失效模式**：深入设计妥协、状态边界、容量极限与异常容错。 |
| **掌握度检验** | 达克效应（Dunning-Kruger）盲区：随便问两句浅层问题便产生“全部搞懂”的虚假安全感。 | **100 分制自动化裁判与苏格拉底考核 (/drill)**：通过代码事实锚定率、去套话纯净度与硬核答辩严格把关。 |

---

## 双形态架构

`repo-mentor` 提供了统一且灵活的双重接入方式：
1. **交互式终端 CLI（`repo-mentor`）**：供开发者在本地终端执行代码拓扑扫描、Git 历史热点考古、依赖图谱提取与离线 HTML 白皮书编译。
2. **自主 Agent Skill（`SKILL.md`）**：无缝兼容 Claude Code、Google Antigravity、Cursor、OpenAI Codex 等智能体，赋予 AI 严谨的工程权威与代码阅读规范。

```
┌────────────────────────────────────────────────────────────────────────┐
│                        双形态用户与智能体接口                           │
│     开发者本地终端 (CLI: repo-mentor)    │   AI 智能体 (SKILL.md)       │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
                    ▼                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        repo_mentor 核心引擎                            │
│  ├── 命令行入口 (Typer & Rich 高颜值终端展示)                          │
│  ├── 静态分析引擎 (语言拓扑扫描、AST 符号表、模块依赖 DAG、Git 热点)     │
│  ├── 事实检验引擎 (源码锚点校验、反 AI 套话检测、时序调用拓扑验证)       │
│  └── 报告导出模块 (单文件交互式 HTML 白皮书编译器、Markdown 合成器)      │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
                    ▼                                ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────┐
│        反“AI味”方法论与工程规范      │  │    多语言开源项目实测基准    │
│  ├── 8 大负向反模式特征库 (N1-N8)    │  │  ├── 跨语言多场景工程验证   │
│  ├── 5 大正向工程深度准则 (P1-P5)    │  │  ├── 0 代码幻觉高标准交付   │
│  └── 100 分制量化裁判标准 (Judge)    │  │  └── 自动化客观评测成绩单   │
└──────────────────────────────────────┘  └──────────────────────────────┘
```

---

## 快速上手

### 安装

通过 `pip` 安装：
```bash
pip install repo-mentor
```

或者无需安装直接使用 `pipx` 运行：
```bash
pipx run repo-mentor scan .
```

若需从源码安装并启用多语言 AST 解析支持：
```bash
git clone https://github.com/Asstar-X/repo-mentor.git
cd repo-mentor
pip install -e ".[dev,ast]"
```

### 3 步体验核心功能

```bash
# 1. 扫描代码库拓扑、入口文件与测试框架布局
repo-mentor scan /path/to/target-repo

# 2. 提取内部模块依赖关系并输出 Mermaid 拓扑图
repo-mentor map /path/to/target-repo --mermaid

# 3. 考古 Git 提交历史，定位变更最频繁的核心重灾区（架构引力中心）
repo-mentor hotspots /path/to/target-repo --top 10
```

---

## CLI 命令行工具速查

`repo-mentor` CLI 提供了覆盖项目全生命周期分析的 8 大核心命令：

| 子命令 | 命令语法 | 功能描述 |
| :--- | :--- | :--- |
| `scan` | `repo-mentor scan <path>` | 自动化识别代码语言分布、依赖清单、入口点以及测试配置。 |
| `map` | `repo-mentor map <path> [--mermaid]` | 解析项目内部模块的导入依赖，生成有向无环图（DAG）与拓扑图。 |
| `hotspots` | `repo-mentor hotspots <path> [--top N]` | 基于 Git 提交历史计算代码变动频次与复杂度，识别架构核心区与技术债。 |
| `ast` | `repo-mentor ast <path> [--symbol S]` | 多语言 AST 符号提取，输出类、函数、接口签名与调用拓扑关系。 |
| `init` | `repo-mentor init <path>` | 一键初始化标准化的阅读工作区、领域覆盖度追踪表与输出模板。 |
| `verify` | `repo-mentor verify [repo] [notes] [--fix] [--strict]` | 严格对照物理磁盘文件，批量检验报告中引用的文件路径与行号真实性（支持自动修正微漂移）。 |
| `eval` | `repo-mentor eval [repo] <report> [--format rich\|json] [--strict]` | 运行 100 分制自动化裁判，综合评估代码锚定率、幻觉扣分与去套话指数。 |
| `export` | `repo-mentor export <study-dir> [--out manual.html]` | 将所有阅读笔记与架构图编译为无外部依赖、高度可交互的单文件离线 HTML 白皮书。 |

---

## 模块化 Agent Skills 套件架构

`repo-mentor` 遵循开放的 **Agent Skills** 规范与 **Andrej Karpathy 极简实战标准**。系统由 **1 个中央调度总线 (Master Orchestrator) + 6 大专职 Skill 独立模块** 组成，坚守人话意图先行（先讲人话在干什么，再讲代码实现）、职责正交与零领域偏好：

```
repo-mentor/
├── SKILL.md                          # [主入口] Master Orchestrator：统筹认知体系与核心导学
├── skills/                           # [核心] 专职 Skill 独立模块目录
│   ├── repo-recon/SKILL.md           # 项目概览: 使命痛点、开箱验证、宏观拓扑与演进热点 (/overview)
│   ├── repo-core/SKILL.md            # 向内看自身: 核心实现与内部逻辑深度剖析 (/core)
│   ├── repo-trace/SKILL.md           # 向外看应用: 上下文使用场景与调用脉络追踪 (/trace)
│   ├── repo-drill/SKILL.md           # 硬核抽查: 提炼核心问题抽查答辩与复盘 (/drill)
│   ├── repo-verify/SKILL.md          # 质量门禁: 代码锚点真实性与事实审计 (/verify)
│   └── repo-export/SKILL.md          # 成果交付: 架构白皮书合成与离线交互式导出 (/export)
├── methodology/                      # [方法论底座] 7 篇通用代码精读与架构推演实战指南
└── templates/                        # [交付模板] 通用、无偏好的架构白皮书与走读手记模板
```

### 核心 Skill 模块与 Slash 命令映射

| 专职 Skill 模块 | 对应命令 | 观察视角 | 核心使命 |
| :--- | :--- | :--- | :--- |
| **[`repo-recon`](skills/repo-recon/SKILL.md)** | `/overview` | **全局全景** | 现实痛点与使命契约、开箱即验（构建与单测）、代码组织与架构拓扑、Git 热点与切入路线。 |
| **[`repo-core`](skills/repo-core/SKILL.md)** | `/core` | **向内看自身** | 纯人话讲透它干什么、内部处理主线、承重切片与设计意图、特殊与边界防护。 |
| **[`repo-trace`](skills/repo-trace/SKILL.md)** | `/trace` | **向外看应用** | 实际业务触发场景、最上游触发源、上下游协同拓扑图、具象实例流经差分、异常传播。 |
| **[`repo-drill`](skills/repo-drill/SKILL.md)** | `/drill` | **硬核抽查** | 提炼 2~3 道切中要害的问题（意图/流转/失效），互动答辩客观复盘，检验真实掌握度。 |
| **[`repo-verify`](skills/repo-verify/SKILL.md)** | `/verify` | **质量门禁** | 自动化静态校验文档中引用的物理文件与行号范围，自愈 Mermaid 图表语法。 |
| **[`repo-export`](skills/repo-export/SKILL.md)** | `/export` | **成果交付** | 将积累的各切片笔记去重合成，编译输出单文件零外部依赖的离线交互式 HTML 架构白皮书。 |

### 主流 Agent 安装方式

#### Claude Code
```bash
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

## 反“AI味”方法论与 100 分量化评测体系

### 5 大正向工程标准 (P1-P5)
1. **代码事实强锚定 (P1)**：所有论断必须包含物理文件路径与具体行号区间（例如 `path/to/file.ext#L120-L145`）。
2. **系统不变量明确化 (P2)**：清晰说明数据状态约束、结构有效性与一致性保证。
3. **全流程链路穿透 (P3)**：自顶向下还原主流程执行序列，严禁中间出现“通过某种方式转发”等模糊过渡。
4. **架构权衡真实呈现 (P4)**：客观呈现工程选型权衡（灵活性 vs 约束、简洁性 vs 表达力），并说明淘汰方案。
5. **失效模式与边界防御 (P5)**：深究错误边界、容量极限、防御校验与异常自愈逻辑。

### 8 大负向反模式禁令 (N1-N8)
- **N1（目录流水账）**：机械罗列目录树，缺乏跨模块的数据交互契约分析。
- **N2（幻觉行号）**：臆造、虚构无法在物理磁盘上找到的代码行号。
- **N3（沉迷样板代码）**：大量篇幅耗费在配置解析、日志初始化等浅层胶水代码上。
- **N4（空洞套话吹捧）**：出现“无缝集成”、“优雅高效”、“起到了至关重要的作用”等无事实依据的套话。
- **N5（报喜不报忧）**：只夸赞设计优点，从不分析设计妥协、局限性与潜在边界隐患。
- **N6（孤岛式分析）**：孤立分析单个函数或类，未连接端到端调用流。
- **N7（忽视异常链路）**：只讲 Happy Path，忽略异常输入、容量超限、执行中断等非正常路径。
- **N8（浅尝辄止自满）**：仅看了入口浅层包装，就盲目宣称已彻底掌握整个项目。

### 100 分量化评分算法 (Judge)

运行 `repo-mentor eval <repo> <report>` 时，自动化裁判将按照以下公式裁决：

$$\text{Final Score} = S_{\text{grounding}} + S_{\text{execution}} + S_{\text{fluff}} + S_{\text{tradeoffs}} - P_{\text{hallucination}}$$

| 评估指标 | 最高分值 | 评测规则 |
| :--- | :---: | :--- |
| **代码事实锚定率** | 30 分 | 包含有效磁盘物理文件与合法行号/符号锚点的论断占比。 |
| **执行流完整性** | 25 分 | 入口点经由核心逻辑处理到达输出/交付的调用时序连续性。 |
| **去“AI味”纯净度 (FFI)** | 25 分 | 52 个套话禁词密度、空洞无锚点段落比例的倒数。 |
| **架构权衡深度** | 20 分 | 包含明确的 Trade-offs 评估、状态不变量约束与失效模式分析。 |
| **幻觉严厉惩治** | -10 分/处 | 每发现一处不存在的文件、越界行号或虚构符号，强力扣除 10 分。 |

- **Grade A (GitHub 高 Star 标准)**：$\ge 85$ 分且 **0 处幻觉**。
- **Grade B (合格)**：$70 - 84$ 分。
- **不合格 (Fail)**：$< 70$ 分或存在 $\ge 2$ 处代码幻觉。

---

## 开源标杆项目实测成绩

`repo-mentor` 在真实的跨语言、生产级开源仓库上完成了端到端基准测试：

### 实测成绩对照表

| 目标代码库 | 技术栈 | 事实锚定率 | 幻觉数量 | 去套话纯净度 (FFI) | 综合得分 | 评定等级 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`mem0ai/mem0`** | Python | 96.4% | **0** | 94.2 / 100 | **92.5 / 100** | **Grade A (通过)** |
| **`gin-gonic/gin`** | Go | 95.1% | **0** | 93.8 / 100 | **91.0 / 100** | **Grade A (通过)** |
| *通用大模型 Chat 基线对照* | Python / Go | 38.2% | 14 | 41.0 / 100 | 28.5 / 100 | **不合格 (Fail)** |

---

## 安全性与不可信代码防护

在分析第三方开源仓库时，安全性至关重要：
- **不可信输入防护**：目标仓库内的所有源码、Commit 提交信息和 Docstring 均视为**不可信数据**。严格免疫隐藏在注释中的 Prompt 注入攻击。
- **只读静态检查**：所有分析器采用纯被动 AST 解析，绝不执行目标项目内的构建脚本（如 `npm postinstall`, `setup.py`, `Makefile` 等）。
- **防目录遍历**：所有路径锚点解析均强制检查目标仓库根目录包含性（`Path.resolve()`），防止 `../../` 越权读取本地敏感文件。
- **数据保密性**：生成的笔记默认被 `.gitignore` 保护，防止私有分析数据意外泄露。

详见 [SECURITY.md](SECURITY.md)。

---

## 参与贡献

热烈欢迎提交 Issue 与 Pull Request！在开始之前，请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解代码风格要求（Ruff、Mypy）与测试标准。

---

## 开源协议

本项目采用 [MIT 许可证](LICENSE)。
