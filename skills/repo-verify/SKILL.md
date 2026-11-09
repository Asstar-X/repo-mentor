---
name: repo-verify
description: >-
  代码事实真实性审计与 Mermaid 图表自愈质检门禁技能。用于在编写或修改研读文档后，自动化静态校验所引用代码文件与行号的物理存在性、语法自愈纠偏 Mermaid 架构图，确保 100% 事实锚定。
license: MIT
---

# Repo Verify — 代码锚点真实性与质检门禁

`repo-verify` 是代码库研读成果的确定性质量检验门禁。它的使命是确保研读文档中的每一处代码引用、流程图和核心论断都严格基于代码库的真实事实，消除文件不存在、行号越界和图表语法损坏。

---

## 1. 三锚点真实性静态校验 (Triple-Anchor Verification)

文档中所有代码引用格式推荐符合 `[path/to/file.ext#Lstart-Lend]`，质检引擎执行三道静态门卡：

1. **门禁 1: 物理文件存在性 (File Existence)**：
   - 引用的文件路径必须在目标代码库根目录下实际存在；
   - 杜绝引用不存在的虚拟文件。
2. **门禁 2: 行号边界合法性 (Line Bounds)**：
   - `start_line` 必须 $\ge 1$ 且 $\le \text{EOF}$；
   - `end_line` 必须 $\ge \text{start_line}$ 且 $\le \text{EOF}$；
   - 避免倒置行号或超出文件实际总行数。
3. **门禁 3: 语义符号对齐 (Symbol Grounding & Drift Tolerance)**：
   - 行号范围内应包含文档所指出的函数名、类名或核心变量；
   - 允许小范围版本漂移，超出漂移范围将提示并支持自动修正 (`--fix`)。

---

## 2. Mermaid 图表语法校验与自愈 (Diagram Linting & Auto-Healing)

保障文档中的 Mermaid 架构图无语法报错：

1. **顶格边距规范 (Flush Left Margin)**：
   - ````mermaid` 建议从行首开始，避免非法缩进破坏解析。
2. **节点标签引号转义**：
   - 包含小括号、中括号、特殊符号的节点标签使用双引号包裹：
     - 正确示例：`NodeA["API Gateway (port 8080)"]`
3. **状态图冒号语法约束 (`stateDiagram-v2`)**：
   - 状态迁移标签使用冒号隔开：
     - 正确示例：`StateA --> StateB : on_success`
4. **关键字冲突规避**：
   - 避免使用 `end` 作为节点标识符（因 `end` 为 Mermaid 保留字），自动替换为 `end_node`。

---

## 3. 确定性工具链执行 (Goal-Driven Execution)

在完成或更新研读文档后，执行确定性质检与自愈命令：

```bash
# 1. 静态校验单个文档的代码锚点真实性与 Mermaid 语法（开启自动修复）
repo-mentor verify <target_path> <study_doc.md> --fix

# 2. 批量校验整个研读工作区目录
repo-mentor verify <target_path> studies/<repo_name>/ --fix

# 3. 运行客观质量与事实锚定评估
repo-mentor eval <target_path> studies/<repo_name>/
```

---

## 4. 内部验收清单 (仅供内部自检，严禁输出给用户)

质检执行完成后，应满足：
- [ ] 所有引用的文件路径在目标仓库中真实存在；
- [ ] 引用的代码行号均在文件总行数范围内；
- [ ] 文档中嵌入的 Mermaid 图表经校验无语法错误且可正常渲染；
- [ ] 关键技术结论均有真实文件或代码事实作为支撑。
