# /export (别名: /report) — 离线 HTML 架构白皮书编译导出

> **支撑技能**: [`skills/repo-export/SKILL.md`](../skills/repo-export/SKILL.md)

将积累在 `studies/<repo_name>/` 下的所有研读资产去重合成，编译为一份完全自包含、可在无网络机房离线查阅的单文件 HTML 交互式架构白皮书。

---

## 执行工作流

### 1. 导出前质量门禁审计
在执行编译前，确保所有研读文档通过 High-Star 门禁：
```bash
repo-mentor verify <target_path> studies/<repo_name>/ --fix
repo-mentor eval <target_path> studies/<repo_name>/
```
确保零失效代码锚点、零 Mermaid 语法报错、零禁用浮夸套话。

---

### 2. 执行编译导出命令
```bash
# 编译并导出单文件离线交互式 HTML 白皮书
repo-mentor export studies/<repo_name>/
```

编译器会自动扫描并结构化融合以下资产：
- `studies/<repo_name>/README.md`
- `studies/<repo_name>/ARCHITECTURE.md`
- `studies/<repo_name>/DEBUG_NOTES.md`
- `studies/<repo_name>/traces/*.md`

---

### 3. 验证交付物
- 确认 `studies/<repo_name>/` 下已生成对应的 `.html` 白皮书文件；
- 本地断开网络自测，验证在浏览器中打开时 CSS 样式、JavaScript 交互与 Mermaid 图表渲染 100% 正常。
