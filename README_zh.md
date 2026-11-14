# Repo Mentor

> **Reconstruct the author's mental model, never recite their syntax.**  
> 重建作者的心智模型，绝不复述代码语法。

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Agent Skill](https://img.shields.io/badge/Agent_Skill-SKILL.md-FF6F00.svg)](SKILL.md)

[English](README.md) • [简体中文](README_zh.md)

---

`repo-mentor` 是面向开发者与 AI 编程助手的代码库精读引擎。

当面对几万行完全陌生的复杂项目时，无论是人还是通用大模型，最常见的困境就是**扎进几百行微观代码细节里，却始终搞不清楚系统整体到底在干什么**。

`repo-mentor` 扮演你工位旁的资深技术搭档：**用平实自然的大白话讲清技术原由与设计取舍，杜绝营销黑话与 AI 八股文**。向内看透单点承重实现，向外追踪端到端链路场景，并提供确定性的静态分析 CLI 与离线交互式白皮书导出。

---

## 核心工作流与命令

命令名即技能名。在支持 Agent Skills 的对话窗口中，直接输入以下指令即可调起：

| 命令 | 视角 | 一句话说明 |
| :--- | :---: | :--- |
| **`/repo-recon`** | 全局侦察 | **项目是干啥的、怎么跑起来**：核心解决什么痛点、开箱验证命令、主要目录职责、推荐切入站点。 |
| **`/repo-core <目标>`** | 向内剖析 | **这块东西自己是干啥的、怎么实现的**：用日常大白话讲透职责、主线逻辑、承重代码与边界防线。 |
| **`/repo-trace <目标>`** | 向外追踪 | **它在真实场景中怎么用的**：谁在什么场景调它、结果给谁、带着具体数据样本走读、出错了如何扩散。 |
| **`/repo-drill [目标]`** | 掌握度抽查 | **搭档抽查答辩**：抛出 2~3 个最接地气、直击设计意图与崩溃边界的硬核问题，客观复盘。 |
| **`/repo-brainstorm [目标]`** | 知识延伸 | **知识延伸与头脑风暴**：延伸底层原理、碰撞业界替代方案、迁移跨界业务场景、拓宽架构思路。 |
| **`/repo-export`** | 资产交付 | **整理导出离线白皮书**：将研读笔记去重整合，一键编译为无需外部网络的单文件离线交互式 HTML。 |

---

## 快速上手

### 1. 安装 CLI 引擎

本地 CLI 工具负责执行扫描、Git 热点分析、AST 解析及 HTML 离线编译等确定性任务：

```bash
# 从源码安装
git clone https://github.com/Asstar-X/repo-mentor.git
cd repo-mentor
pip install -e .

# 如需多语言 AST 支持（Tree-sitter）
pip install -e ".[ast]"
```

### 2. 作为 Agent Skill 使用

将本仓库克隆至你的 Agent Skills 目录即可全局或项目级生效：

```bash
# Claude Code 个人技能目录：
git clone https://github.com/Asstar-X/repo-mentor.git ~/.claude/skills/repo-mentor

# Antigravity / Cursor / Qoder 等环境：
# 放置于项目根目录的 skills/repo-mentor，或在配置中指定路径指向本仓库根目录的 SKILL.md
```

在对话中输入 `/repo-recon` 即可开始对目标代码库的精读。

---

## CLI 工具一览

除了作为 Agent 技能交互，`repo-mentor` 也提供了独立的终端命令行工具：

```bash
# 1. 扫描项目技术栈、主入口与单测布局
repo-mentor scan /path/to/target-repo

# 2. 提取包依赖拓扑，生成 Mermaid DAG
repo-mentor map /path/to/target-repo --mermaid

# 3. 分析 Git Churn 变更热点，定位架构核心重心
repo-mentor hotspots /path/to/target-repo --commits 300 --top 10

# 4. 提取核心符号与函数调用链（支持 Python, Go, TypeScript, Rust）
repo-mentor ast /path/to/target-repo src/core/engine.py --calls

# 5. 初始化结构化研读工作区
repo-mentor init studies/target-repo --repo /path/to/target-repo

# 6. 编译生成单文件离线交互式 HTML 架构白皮书
repo-mentor export studies/target-repo --out whitepaper.html
```

---

## 研读思维工具

[`methodology/`](methodology/) 目录下提供了 4 篇聚焦的方法论指南，供 Agent 和开发者在深度剖析时按需查阅：

- [01. 项目侦察与演进热点指南](methodology/01-recon-and-hotspots.md)：30 秒建立全局心智，借助“30 行脚本”检验法与 Git 幂律热点直击系统原罪与重心。
- [02. 核心实现与状态模型剖析指南](methodology/02-core-analysis.md)：80/20 过滤法剥离外围胶水代码，针对系统状态不变式与生命周期进行严密建模。
- [03. 链路追踪与掌握度抽查指南](methodology/03-tracing-and-drill.md)：Payload Diff 动态形态差分追踪，结合意图、流转与失效三维考题检验真实掌握度。
- [04. 知识延伸与头脑风暴指南](methodology/04-brainstorm.md)：跳出单一实现的局限，探索底层运行机制、替代范式取舍与跨界场景迁移。

---

## 许可证

[MIT License](LICENSE)
