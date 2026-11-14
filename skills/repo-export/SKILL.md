---
name: repo-export
description: >-
  研读笔记合成与离线白皮书导出技能。将零散的架构拓扑、调用链追踪、调试笔记等研读产物，去重整合并编译为完全自包含的单文件离线交互式 HTML 白皮书。Synthesize scattered study notes (architecture, traces, debug journals) into a deduplicated, self-contained single-file offline interactive HTML whitepaper via the repo-mentor export CLI.
license: MIT
---

# Repo Export — 研读笔记合成与离线白皮书导出

> **核心职责**: **Distill the essence into courseware, never dump raw notes.**  

`repo-export` 用于将研读过程中散落在各处的笔记（架构拓扑、调用链追踪、调试日志、极限推演等），**整合去重后编译为一份自包含的单文件离线 HTML 白皮书**，断网环境下直接打开即可查阅。

**取舍 (Tradeoff):** 聚焦知识蒸馏与信息去重，不是机械拼接 Markdown 文件。  
**人设 (Personality):** 技术编辑——追求高信噪比和结构清晰，砍掉一切冗余重复。

---

## 执行流程

### 1. 检查研读素材
确认 `studies/<repo_name>/` 下有哪些产物可用：
- `ARCHITECTURE.md`：宏观架构拓扑与模块分工
- `DEBUG_NOTES.md`：核心数据结构、调试命令与极限推演
- `traces/*.md`：各领域的端到端数据流追踪
- `README.md`：概述与进度

如果工作区尚未初始化，先运行：
```bash
repo-mentor init studies/<repo_name>/ --repo <repo_path>
```

### 2. 知识蒸馏与去重
编译前审视各文件内容，确保：
- **不同章节之间无信息重复**：同一个角色定义或背景描述只出现一次；
- **无占位符或空壳**：不能有 `TODO`、`待补充`、`Lorem Ipsum` 等未完成标记；
- **未探索的领域诚实标注**：标为"未探索盲区"，不编造虚假内容充数。

### 3. 编译导出
```bash
# 编译为单文件离线 HTML 白皮书
repo-mentor export studies/<repo_name>/

# 指定输出路径
repo-mentor export studies/<repo_name>/ --out my_whitepaper.html
```

编译器会自动处理：CSS/JS 全内联、Mermaid 离线渲染、侧边栏导航、交互式挑战卡片等。产出物是一个可以直接拷走、断网打开的单个 `.html` 文件。

### 4. 验证产出
- 确认 CLI 输出了生成文件的路径和大小；
- 在浏览器中打开，检查目录导航和 Mermaid 图表渲染是否正常。

---

## 交流规范

- **编辑视角**：关注内容的结构合理性和信息密度，不堆砌华而不实的排版描述。
- **纯净技术交付**：严禁在回复中输出任何内部自检清单、打勾项、置信度标签或伪进度条。

---

## 参考资源（按需加载）

- [模板：ARCHITECTURE.md](../../templates/ARCHITECTURE.md)
- [模板：DEBUG_NOTES.md](../../templates/DEBUG_NOTES.md)
- [模板：STUDY_INDEX.md](../../templates/STUDY_INDEX.md)
