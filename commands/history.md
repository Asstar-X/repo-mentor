# /history (命令别名)

> 💡 `/history` 已作为演进热点考古整合到 [`/overview`](overview.md) 中，底层由 [`skills/repo-recon/SKILL.md`](../skills/repo-recon/SKILL.md) 驱动。

Git 变更热点与提交活跃度会在 `/overview` 阶段自动执行，用于定位系统的架构重心地带。
运行 [`/overview`](overview.md) 或直接调用底层 CLI：
```bash
repo-mentor hotspots <target_path> --commits 300 --top 10
```
