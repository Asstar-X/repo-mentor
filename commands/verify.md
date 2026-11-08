# /verify (别名: /audit) — 代码事实强锚定与质检门禁

> **支撑技能**: [`skills/repo-verify/SKILL.md`](../skills/repo-verify/SKILL.md)

运行确定性静态分析引擎，自动化核验研读文档中引用的所有文件路径、代码行号范围、AST 符号及 Mermaid 架构图语法，彻底消除虚假幻觉与“AI味”吹捧套话。

---

## 执行工作流

### 1. 运行确定性质检工具
```bash
# 1. 静态核验文档中的代码行号、符号存在性与 Mermaid 图表语法 (开启自动修复)
repo-mentor verify <target_path> studies/<repo_name>/ARCHITECTURE.md --fix
repo-mentor verify <target_path> studies/<repo_name>/DEBUG_NOTES.md --fix
repo-mentor verify <target_path> studies/<repo_name>/traces/ --fix

# 2. 运行反 AI 虚夸词检测与百分制客观裁判评估
repo-mentor eval <target_path> studies/<repo_name>/
```

---

### 2. 输出质检审计报告
- **扫描锚点总数**：检测到的代码引用锚点数量；
- **有效通过率 (目标 100%)**：物理文件存在、行号在 EOF 范围内、语义符号对齐的比例；
- **Mermaid 健康度**：拓扑图与时序图语法是否完全通过无报错；
- **反 AI 纯净度**：52 个禁用套话词命中次数（目标：0 次）与未锚定长段落标记。
