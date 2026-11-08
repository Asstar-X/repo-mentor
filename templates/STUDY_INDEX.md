# [项目名称] — 架构研读索引与领域覆盖度看板

> **研读状态**: `[进行中 (in_progress) / 已完成 (completed)]`  
> **目标语言生态**: `[Go / Rust / Python / TypeScript / Java / C++]`  
> **认知变焦模型**: 5 级变焦闭环 (Why 现实原罪 ➔ Strategy 剧本角色 ➔ Example 具象案例 ➔ Deep-Dive 硬核源码 ➔ Takeaway 架构权衡)  
> **质量规范**: 反 AI 虚夸词标准 & AST 源码事实强锚定

---

## 1. 研读资产索引目录

- **[架构全景白皮书 (ARCHITECTURE.md)](ARCHITECTURE.md)**: Level 1 (现实原罪与第一性矛盾) + Level 2 (生活隐喻与剧本角色表) + Level 4 (核心实体与算法) + Level 5 (架构得失权衡)。
- **[源码走读与调试手记 (DEBUG_NOTES.md)](DEBUG_NOTES.md)**: 本地编译与冒烟单测命令、黄金断点调用栈、反事实推演手记。
- **领域调用链与深度切片 (`traces/`)**:
  - [领域 1 数据旅程切片 (traces/domain_1_trace.md)](traces/domain_1_trace.md): Level 3 具象用例数据旅程 + 时序图。
  - [领域 1 核心算法与极限切片 (traces/domain_1_core.md)](traces/domain_1_core.md): Level 4 状态机与承重算法。

---

## 2. 核心功能领域二元看板 (已探索 vs 未探索盲区)

真实的技术掌握度应当以关键链路领域是否被端到端彻底打通来衡量：

| 核心功能领域 (Tier-0) | 映射的核心模块 / 目录 | 核心实现 (`/core`) | 调用脉络 (`/trace`) | 探索状态 |
| :--- | :--- | :---: | :---: | :--- |
| **1. [领域 1 名称]** | `[src/module1/]` | [x] 已完成 | [x] 已完成 | 已探索 (Explored) |
| **2. [领域 2 名称]** | `[src/module2/]` | [ ] 待剖析 | [ ] 待追踪 | ⚠️ 未探索盲区 (Blind Spot) |
| **3. [领域 3 名称]** | `[src/module3/]` | [ ] 待剖析 | [ ] 待追踪 | ⚠️ 未探索盲区 (Blind Spot) |

---

## 3. 下一步研读决策建议

1. **消灭盲区**: 针对未勾选的 Tier-0 领域运行 `/trace <domain>` 穿透数据旅程；
2. **硬核下钻**: 针对复杂状态机运行 `/deep-dive <domain>` 提取代码锚点与 What-If 推演；
3. **闭环质检**: 运行 `repo-mentor verify . ARCHITECTURE.md` 验证事实真实性，最后执行 `repo-mentor export .` 导出单文件 HTML 白皮书。
