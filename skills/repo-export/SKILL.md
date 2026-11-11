---
name: repo-export
description: >-
  研读资产知识合成与单文件离线交互式 HTML 白皮书编译技能。用于将零散的架构拓扑、调用链数据流、状态机不变式与极限防御笔记，去重合成并编译为完全自包含、可在无网络机房离线查阅的单文件 HTML 架构白皮书。Compile scattered study notes (architecture, traces, invariants, failure drills) into a fully self-contained single-file interactive HTML whitepaper that works offline with zero CDN dependencies.
license: MIT
---

# Repo Export — 研读资产合成与单文件离线 HTML 白皮书编译

> **核心职责**: **Distill the essence into courseware, never dump raw notes.**  
> （把精华萃取成精品课件，绝不交杂乱草稿。）

`repo-export` 是代码库研读旅程的终局交付引擎。它的使命是帮助开发者**将零散记录在各个切片中的宏观拓扑、调用链数据流、状态机不变式与极限防御笔记，编译为一份完全自包含、可在断网机房随时离线查阅的交互式单文件 HTML 架构白皮书**。

**核心目标:** 高信噪比的信息蒸馏与单文件便携性，结构严密，排版克制，杜绝外部网络依赖与破损死链。

---

## 1. 多切片知识蒸馏与去重 (Multi-Slice Synthesis)

**把零碎探索笔记变成结构严密的出版级白皮书，严禁机械拼接与套话冗余。**

编译引擎会自动扫描 `studies/<repo_name>/` 目录下的所有结构化产物：
- `README.md`：项目概述与核心领域覆盖度看板；
- `ARCHITECTURE.md`：宏观系统原罪、第一性矛盾、剧本角色表与宏观架构拓扑；
- `traces/*.md`：各核心领域的端到端数据旅程与时序图；
- `DEBUG_NOTES.md`：状态机模型、承重算法锚点与极限 What-If 灾难推演。

**知识去重铁律 (Zero Information Redundancy)**：
- 严禁将相同的角色定义或背景痛点在不同章节反复讲；
- 自动合并零散问答与极限演练卡片，按“架构基石 ➔ 数据旅程 ➔ 深度防线 ➔ 思考题”逻辑组织。

---

## 2. 单文件离线白皮书编译器 (Standalone Architecture Manual)

**离线单文件交付，能在任何内网、断网机房及移动端浏览器中瞬间秒开。**

生成的 HTML 白皮书必须满足工业级自包含标准：
1. **零外部 CDN 依赖**：
   - 所有 CSS 样式、JavaScript 交互逻辑、图标字体与 Mermaid 渲染引擎全部内联打包在单一 `.html` 文件中；
   - 在完全断网飞行模式下打开，样式与图表渲染 100% 完整正常。
2. **极简暗黑与明亮自适应主题**：
   - 内置工程师友好的专业排版风格，字号、行距、代码高亮均经过视网膜屏调优；
   - 支持一键切换全屏阅读模式与目录侧边栏快速跳转。
3. **交互式架构组件**：
   - **Mermaid 动态渲染**：支持图表无级缩放与拖拽；
   - **代码锚点直觉高亮**：点击代码引用跳转到代码卡片；
   - **交互式认知挑战卡片 (Self-Check Challenge Cards)**：点击展开“What-If 灾难答案与防线解析”，供团队内训考评。

---

## 3. 零占位符与罐头文本门禁 (Zero Canned Boilerplate Gate)

**真正的白皮书必须全是硬核代码事实，严禁任何“TODO”或假数据占位符。**

在执行导出编译前，编译器执行静态合规检查：
- 严禁包含 `Lorem Ipsum`、`待补充`、`TODO` 等未完成标记；
- 严禁输出静态空卡片（如没有任何挑战演练却留着空白问答框）；
- 若某核心领域尚未完成深入探索，明确标为“未探索盲区 (Unexplored Blind-Spot)”，绝不编造虚假及格分。

---

## 4. 怎么做 vs 不要怎么做 (对比清单)

| 绝对不要（粗糙杂乱） | 必须做到（整洁、完整、开箱即用） |
| :--- | :--- |
| **外部 CDN 依赖**：引用 `unpkg.com` 或 `cdnjs`，断网即全白屏或图表崩溃。 | **全内嵌单文件**：所有运行时资源与图表库内敛打包，单一文件拷走即用。 |
| **碎片散落**：交出 15 个零散 Markdown 文件让读者在文件夹中自行翻找。 | **结构化一页读透**：按认知变焦层次融合成交互式页面与导航树。 |
| **虚假占位符**：未分析完的模块留着模板空括号和虚假内容。 | **客观诚实报告**：明确标注当前已覆盖的核心领域与未探索盲区。 |

---

## 5. 确定性工具链执行 (Goal-Driven Execution)

编译与导出白皮书时，运行确定性导出工具：

```bash
# 1. 导出编译生成单文件离线交互式 HTML 白皮书
repo-mentor export studies/<repo_name>/

# 2. 导出时指定输出文件名或自定义路径
repo-mentor export studies/<repo_name>/ --out my_whitepaper.html
```

---

## 6. 内部验收清单 (仅供内部自检，严禁输出给用户)

导出流程完成时，必须满足：
- [ ] **生成单文件 `.html`**：保存在 `studies/<repo_name>/` 目录下；
- [ ] **断网自测通过**：在无网络环境下通过本地浏览器打开，CSS/JS/Mermaid 渲染正常；
- [ ] **交互式导航健全**：左侧目录树跳转顺畅，Mermaid 图表支持点击与缩放；
- [ ] **零占位符与死链**：无未填写的模板变量，无失效跳转；
- [ ] **CLI 成功输出并显示生成文件物理大小与路径**。

---

## 参考资源（按需加载）

研读产物的交付格式参考（`repo-mentor init` 会基于真实仓库数据生成对应骨架）：

- [模板：ARCHITECTURE.md 架构白皮书](../../templates/ARCHITECTURE.md)
- [模板：DEBUG_NOTES.md 调试与极限推演笔记](../../templates/DEBUG_NOTES.md)
- [模板：STUDY_INDEX.md 研读索引](../../templates/STUDY_INDEX.md)
