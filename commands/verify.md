---
description: 代码事实审计与文档质检门禁（/repo-verify 的可选短别名）。静态核验代码锚点真实性与 Mermaid 图表语法。
---

# /verify — 代码事实审计与文档质检门禁

> **对应技能**: [`/repo-verify`](../skills/repo-verify/SKILL.md)（技能名即命令名；本文件是可选短别名，需拷入平台命令目录后生效）  
> **核心职责**: **Verifying reality is your job, never the user's.** (核实真实性是你的天职，绝不是用户的。)

运行确定性静态分析引擎，自动化核验研读文档中引用的物理文件路径、代码行号范围、AST 符号及 Mermaid 架构图语法，确保文档内容与代码库物理事实 100% 对齐。

---

## 执行工作流

### 1. 运行确定性质检工具
```bash
# 1. 静态核验文档中的代码行号、符号存在性与 Mermaid 图表语法 (开启自动修复)
repo-mentor verify <target_path> <study_doc.md> --fix

# 2. 批量校验整个研读工作区目录
repo-mentor verify <target_path> studies/<repo_name>/ --fix

# 3. 运行客观质量与事实锚定评估
repo-mentor eval <target_path> studies/<repo_name>/
```

---

### 2. 输出质检审计报告
- **物理文件存在性**：引用的文件是否在磁盘真实存在；
- **行号边界有效性**：引用行号是否在有效范围内（未越界、无倒置）；
- **符号对齐度**：行号区域内是否包含文档声称的函数、类或变量；
- **Mermaid 渲染健康度**：架构图与时序图语法是否合规并通过自动修复。
