---
name: repo-verify
description: >-
  代码事实真实性审计、Mermaid 图表自愈与反 AI 套话质检门禁技能。用于在编写或修改研读文档后，自动化静态校验所引用代码文件与行号的物理存在性、语法自愈纠偏 Mermaid 架构图、拦截 52 个反 AI 虚夸词，执行百分制量化门禁。
license: MIT
---

# Repo Verify — 代码锚点真实性与反 AI 套话质检门禁

`repo-verify` 是代码库研读成果的确定性质量检验门禁。它的使命是帮助开发者与 Agent **彻底根除大模型胡编乱造虚假代码行、死链、损坏的 Mermaid 图表以及毫无技术价值的“AI味”吹捧套话**，确保研读报告达到 100% 工业级代码事实真实验证。

**取舍 (Tradeoff):** 零容忍幻觉与模糊套话，严格执行自动化拦截；未通过质量门禁的文档一律拒绝放行。  
**人设 (Personality):** 冷酷无情的编译器与质检法官——不听主观辩解，只看静态代码事实验证通过率与规则扣分项。

---

## 1. 三锚点真实性静态校验 (Triple-Anchor Verification)

**引用的每一行代码必须在磁盘上真实存在，严禁任何代码行号幻觉。**

文档中所有代码引用格式必须符合 `[path/to/file.ext#Lstart-Lend]`，质检引擎将执行三道静态门卡：
1. **门禁 1: 物理文件存在性 (File Existence)**：
   - 引用的文件路径必须在目标代码库根目录下实际存在；
   - 引用了不存在的虚拟文件直接判定为**致命幻觉**（一票否决扣 100 分）。
2. **门禁 2: 行号边界合法性 (Line Bounds)**：
   - `start_line` 必须 $\ge 1$ 且 $\le \text{EOF}$；
   - `end_line` 必须 $\ge \text{start_line}$ 且 $\le \text{EOF}$；
   - 禁止倒置行号（如 `L100-L20`）或超出文件实际总行数。
3. **门禁 3: 语义符号对齐 (Symbol Grounding & Drift Tolerance)**：
   - 行号范围内必须包含文档所声称的函数名、类名或核心变量；
   - 允许 $\pm 5$ 行以内的正常小范围版本漂移，超出漂移范围将告警并触发自动修正 (`--fix`)。

---

## 2. Mermaid 图表语法校验与自愈 (Diagram Linting & Auto-Healing)

**绝不产出报错爆红的 Mermaid 架构图。常见的大模型语法低级错误必须 100% 拦截并自动修复。**

质量引擎自动对文档中的 Mermaid 代码块执行合规校验：
1. **顶格边距纪律 (Flush Left Margin)**：
   - ````mermaid` 必须从行首第 0 列开始，禁止任何多余的前置缩进空格。
2. **节点标签双引号强制转义**：
   - 包含小括号、中括号、特殊符号的节点标签必须用双引号包裹：
     - ❌ 错误：`NodeA[API Gateway (port 8080)]`
     - ✅ 正确：`NodeA["API Gateway (port 8080)"]`
3. **状态图冒号语法约束 (`stateDiagram-v2`)**：
   - 状态迁移标签必须使用冒号隔开，禁止多重非法连线字符：
     - ✅ 正确：`StateA --> StateB : on_success`
4. **关键字冲突规避**：
   - 严禁使用 `end` 作为节点标识符（因 `end` 为 Mermaid 内部保留字）；
   - 自动将孤立 `end` 标识符替换为 `end_node`。

---

## 3. 52 个反 AI 虚夸词库过滤 (Anti-AI Fluff Linting)

**剔除商业吹捧与学究式冗余废话。技术报告只认事实与数据。**

质检引擎自动扫描以下 50+ 个负向反模式套话，命中即扣分：
- **中文禁用词表**：
  `极其优雅`, `完美融合`, `巧夺天工`, `无缝衔接`, `企业级标准`, `无可挑剔`, `毋庸置疑`, `革命性`, `划时代`, `独树一帜`, `不言而喻`, `不失为`, `众所周知`, `集大成者`, `极具前瞻性`
- **英文禁用词表**：
  `seamlessly integrates`, `cutting-edge`, `state-of-the-art`, `masterpiece`, `elegant design`, `flawless`, `industry standard`, `revolutionary`, `par excellence`, `game-changer`
- **未锚定长段落惩罚 (Ungrounded Paragraph Penalty)**：
  - 任何超过 45 个单词（或 90 个汉字）的技术性论断段落，若全文未包含任何物理代码锚点、文件名或量化指标，将被标记为“悬空空话”，强制扣分。

---

## 4. 百分制量化质检卡 (100-Point Quantitative Rubric)

运行评估命令时，根据以下量化评分卡生成综合成绩单：

| 评估维度 | 分值权重 | 扣分与及格标准 |
| :--- | :---: | :--- |
| **代码锚点真实率 (Grounding Rate)** | **35 分** | 锚点真实有效率需 $\ge 95\%$；出现 1 个不存在文件直接扣 100 分。 |
| **反套话纯净度 (Anti-Fluff Score)** | **25 分** | 每命中 1 个禁用浮夸词扣 5 分；每出现 1 处未锚定长段落扣 3 分。 |
| **极限场景防御 (Limit Scenarios)** | **20 分** | 必须包含至少 1 个经过代码行验证的 What-If 灾难假设推演与反例。 |
| **状态机与架构图 (FSM & Diagrams)** | **20 分** | 必须包含合规且渲染通过的 Mermaid 拓扑图或状态流转图。 |
| **总计门禁合格线** | **100 分** | **$\ge 85$ 分评为 High-Star 合格；$< 85$ 分拒绝放行。** |

---

## 5. 确定性工具链执行 (Goal-Driven Execution)

在完成任何研读文档后，必须执行确定性质检与自愈命令：

```bash
# 1. 静态校验代码锚点真实性与 Mermaid 语法（开启自动修复）
repo-mentor verify <target_path> <study_doc.md> --fix

# 2. 批量校验整个研读工作区目录
repo-mentor verify <target_path> studies/<repo_name>/ --fix

# 3. 运行反 AI 废话与百分制客观评分
repo-mentor eval <target_path> studies/<repo_name>/
```

---

## 6. 验收清单 (Verifiable Success Criteria)

质检流程完成时，必须满足：
- [ ] **锚点真实率 100%**：所有引用的文件物理存在，所有行号均在文件总行数范围之内；
- [ ] **Mermaid 0 语法报错**：所有架构图与时序图经校验器检测无语法缺陷；
- [ ] **反 AI 废话 0 违规**：52 个禁用词库无任何命中记录；
- [ ] **百分制总分 $\ge 85$ 分**：综合评分达到 High-Star 交付标准；
- [ ] **CLI 退出码为 0**：`repo-mentor verify` 正常退出无未捕获异常。
