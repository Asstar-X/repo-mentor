# /tracker — 研读进度与领域二元看板

以清晰的二元清单（已探索 vs 盲区）展示核心领域的覆盖进度，杜绝虚假打分。

---

## 1. 核心领域覆盖度看板

真实的技术掌握度应当以关键链路领域是否被端到端彻底打通来衡量：

```markdown
### 核心功能领域清单 (Tier-0)
- [x] **宏观架构与第一性矛盾 (Level 1 & 2)**: 已在 `ARCHITECTURE.md` 完成 (基于 `repo-recon`)
- [x] **领域 1: [领域名称]** (`[path/to/module]`) — 已探索 (基于 `repo-trace` 与 `repo-deepdive`)
- [ ] **领域 2: [领域名称]** (`[path/to/module]`) — ⚠️ 未探索盲区
- [ ] **领域 3: [领域名称]** (`[path/to/module]`) — ⚠️ 未探索盲区
```

---

## 2. 下一步决策
- 若仍存在未勾选的 Tier-0 盲区：运行 `/trace <domain>` 与 `/deep-dive <domain>` 消灭盲区；
- 当所有核心领域均已勾选：运行 `/verify` 进行全量门禁审计，随后执行 `/export` 编译白皮书。
