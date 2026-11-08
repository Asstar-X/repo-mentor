# [项目名称] — 架构研读索引与掌握度看板

> **研读状态**: `[进行中 (in_progress) / 已完成 (completed)]`  
> **目标语言生态**: `[Go / Rust / Python / TypeScript / Java / C++]`  
> **质量规范**: 基于源码事实强锚定与客观推演

---

## 1. 研读资产索引目录

- **[架构全景白皮书 (ARCHITECTURE.md)](ARCHITECTURE.md)**: 项目现实痛点、开箱验证方案、宏观代码组织、架构流向图与切入路线。
- **[深度走读与调试手记 (DEBUG_NOTES.md)](DEBUG_NOTES.md)**: 本地构建与定向单测命令、关键调试断点、核心实现与 What-If 极限推演。
- **业务场景与数据链路切片 (`traces/`)**:
  - [场景 1 数据流切片 (traces/scenario_1_trace.md)](traces/scenario_1_trace.md): 业务触发、上下游协作拓扑与端到端数据流。
  - [场景 2 数据流切片 (traces/scenario_2_trace.md)](traces/scenario_2_trace.md): 异常流转与分支处理。

---

## 2. 核心功能领域掌握度看板 (已掌握 vs 待攻克盲区)

通过端到端的代码掌握与考核检验真实理解深度：

| 核心功能领域 | 映射的核心模块 / 目录 | 自身实现 (`/core`) | 调用链路 (`/trace`) | 考核答辩 (`/drill`) | 掌握状态 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **1. [领域 1 名称]** | `[src/module1/]` | [x] 已剖析 | [x] 已追踪 | [x] 已答辩 | 已掌握 (Mastered) |
| **2. [领域 2 名称]** | `[src/module2/]` | [ ] 待剖析 | [ ] 待追踪 | [ ] 待考核 | ⚠️ 待攻克盲区 (Blind Spot) |
| **3. [领域 3 名称]** | `[src/module3/]` | [ ] 待剖析 | [ ] 待追踪 | [ ] 待考核 | ⚠️ 待攻克盲区 (Blind Spot) |

---

## 3. 下一步研读决策建议

1. **剖析核心实现**: 运行 `/core <target>` 搞清模块自身在干什么、主线如何推进、边界如何防护；
2. **追踪使用场景**: 运行 `/trace <target>` 搞清它在什么场景下被使用、最上游触发源与数据流转；
3. **名师考核答辩**: 运行 `/drill [target]` 进行灵魂考题抽查答辩，破除虚假掌握感；
4. **质检与交付**: 运行 `repo-mentor verify . ARCHITECTURE.md` 核验事实真实性，最后执行 `repo-mentor export .` 导出单文件 HTML 架构白皮书。
