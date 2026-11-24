---
name: repo-export
description: >-
  通用项目深度阅读报告合成与离线 HTML 导出技能。汇总全会话的 recon/core/trace/drill 研读对话与追问复盘，按重要性主次重排并剔除黑话，以第一视角合成带 Mermaid 流程图与单栏长文排版的离线 HTML 阅读报告。Synthesize full-session repo-mentor study dialogues (recon, core, trace, drill) into a plain-language, priority-ordered, single-column offline HTML reading report with Mermaid flowcharts via repo-mentor export.
license: MIT
---

# Repo Export — 第一视角项目阅读报告合成与离线导出

> **核心职责**: **Distill live understanding into a plain-language reading guide, prioritized from core engine to periphery.**

`repo-export` 用于在项目研读收官时，将整个学习过程中碰撞出的认知（包括架构扫描、模块 `core` 拆解、`trace` 场景走读、以及 `drill` 中的卡壳追问与复盘），**按重要性从主到次梳理，写成一篇第一视角“说人话”的深度阅读报告，并编译为单栏公众号风的离线单文件 HTML**。

**取舍 (Tradeoff):** 追求“让没看过源码的同行也能一口气读懂”的高信噪比长文体验，优先把最核心的发动机与底线逻辑放在聚光灯下，不堆砌黑话，不罗列流水账。  
**人设 (Personality):** 刚带着大家啃完硬核源码的资深技术搭档——口吻自然真实、轻重分明、直击本质。

---

## 执行流程

### 1. 回溯全会话研读脉络与素材
在动笔前，**不要只盯着硬盘上零散的笔记文件**，必须完整回溯本轮学习中的所有关键输入：
1. **检索对话历程**：回顾会话中所有 `/repo-recon`、`/repo-core`、`/repo-trace`、`/repo-drill` 交互轮次；如果早期的对话因上下文窗口发生过截断，**主动查阅系统保存的对话转录日志（如 `transcript.jsonl`）**，把每一轮用户真正卡壳追问过的问题和通俗比喻找回来。
2. **盘点已有研读文件**：检查 `studies/<repo_name>/` 下的 `ARCHITECTURE.md`、`DEBUG_NOTES.md`、`traces/*.md` 及真实仓库代码行号锚点。如尚未初始化，可先执行：
   ```bash
   repo-mentor init studies/<repo_name>/ --repo <repo_path>
   ```
3. **盘点客观统计**：若缺少仓库规模或热点数据，补跑 `repo-mentor scan <repo_path>` 与 `repo-mentor hotspots <repo_path>`，用真实文件数、代码行数定调。

---

### 2. 按模板撰写 `REPORT.md`（主次分明 + 说人话准则）
严格参考 [模板：REPORT.md](../../templates/REPORT.md) 在 `studies/<repo_name>/REPORT.md` 撰写第一视角项目阅读报告：

1. **固定三大主干章节**：
   - **1. 项目背景、解决的问题、行业现状**：先用大白话点透同类方案普遍卡在哪里，再用一句话说清这个项目解决什么、不解决什么。
   - **2. 项目特色**：提炼 3~4 条最反常识或最实用的工程硬招。
   - **3. 核心功能**：把研读过的核心模块按 `3.1`、`3.2` ... 依次展开；每个子功能必须齐备：**核心设计意图（Core） + 1 张结构清晰的 Mermaid 示例流程图 + 真实场景走读（Trace） + 追问排雷复盘（Drill）**。
2. **主次防偏与去模板化铁律（极其重要）**：
   - **结构一致，话术千人千面**：固定三大主标题（`1. 项目背景、解决的问题、行业现状`、`2. 项目特色`、`3. 核心功能`）即可，**严禁每份报告机械复制相同的开场白、口头禅和小标题**（比如每节都写一模一样的固定过渡语）。请像技术博主根据不同项目的性格现写长文一样自然行文。
   - **越底层核心的放最前面、给足篇幅**：开篇导语、第 1 节痛点、第 2 节特色以及 `3.1` / `3.2` 必须把聚光灯打在最核心的状态机、主循环、数据结构和防崩溃底线上；
   - **外围体验优化绝不喧宾夺主**：缓存省钱、UI 手感、热插拔、扩展体系等细节放在中后段或作为特色末条收拢，保持轻重有度。
3. **排版统一与公众号兼容规范**：
   - **第一视角说人话**：全篇以“我”带着大家看代码的方式行文，严禁出现“高内聚低耦合、赋能底座、优雅架构”等空洞黑话；把真实对话中用户的疑惑自然编织进各节的问题复盘有序列表里。
   - **流程图必须适配单栏与公众号复制**：每个核心功能配 1 张 Mermaid 图，**统一优先采用 `flowchart TD` 竖向布局并适当 `\n` 折行**（禁止画超长 `LR` 横图导致手机端和公众号压缩变扁）；`--mode report` 会自动屏蔽多余按钮文字并将纯原生 SVG 光栅化为 2x 高清 PNG 图片，可直接从浏览器 `Ctrl+A` 全选复制粘贴到微信公众号编辑器（彻底避免 SVG 被微信清洗成纯黑块）。
   - **格式统一**：问答复盘统一用规范的 Markdown 有序列表（`1. **问题**` + 缩进解析段落），不要把长串数字列表硬塞在同一个引用块里；`>` 引用块仅用于单句高亮结论。
   - **避免渲染乱码**：复杂公式/复杂度统一用等宽代码（如 `` `O(N)` ``），禁止在 Markdown 中使用浏览器离线模板未加载数学引擎的 `$` LaTeX 语法；禁止留存未完成的占位符标记。
   - **未探索领域诚实说明**：若存在尚未覆盖的模块，如实标出边界，绝不编造未读源码的细节。

---

### 3. 锚点严格核验与单栏离线导出

1. **代码锚点与 Mermaid 语法校验**：
   确保报告中引用的每一处文件路径、行号范围和符号名称在目标源码中真实存在，且流程图语法无括号/引号冲突：
   ```bash
   repo-mentor verify <repo_path> studies/<repo_name>/ --strict
   ```
2. **编译为单栏离线 HTML 报告**：
   使用 `--mode report` 模式（去掉侧边栏，采用类似技术公众号的居中单栏长文排版，自动内联离线 Mermaid 与字体对齐样式）：
   ```bash
   # 编译为单栏第一视角离线阅读报告
   repo-mentor export studies/<repo_name>/ --mode report --out studies/<repo_name>/dist/<repo_name>-report.html
   ```
   > 如需传统双栏多卡技术白皮书，可指定 `--mode whitepaper`。

---

### 4. 验证产出并交付
- 确认 CLI 返回 `0` 且输出了 `.html` 产出路径与文件大小；
- 检查产出为自包含单文件 HTML（无外部 CDN 引用、纯单栏、全部流程图可正常离线缩放查看）；
- `/repo-export` 为终态操作，回复用户时**无需**再输出掌握度仪表盘与下一步引导，直接附上可读链接说明产物位置与核心核验结果即可。

---

## 交流规范

- **第一视角主编心态**：既要懂底层的硬核因果，更要站在读者立场挑重点、砍废话。
- **纯净技术交付**：严禁在回复或报告正文中输出任何内部自检清单、打勾项、置信度标签或虚构进度。

---

## 参考资源（按需加载）

- [模板：REPORT.md（第一视角项目阅读报告模板）](../../templates/REPORT.md)
- [模板：ARCHITECTURE.md](../../templates/ARCHITECTURE.md)
- [模板：DEBUG_NOTES.md](../../templates/DEBUG_NOTES.md)
- [模板：STUDY_INDEX.md](../../templates/STUDY_INDEX.md)
