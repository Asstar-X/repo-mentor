# /tracker — Study Progress & Domain Checklist

Displays the learning progress across core functional domains using a clean, binary checklist (Explored vs. Blind Spot).

---

## 1. Domain Coverage Checklist

Rather than arbitrary float formulas, real mastery is measured by whether the critical path domains have been explored end-to-end:

```markdown
### Core Functional Domains Checklist
- [x] **Macro Architecture & First Tension (Level 1 & 2)**: Explored via `repo-recon` in `ARCHITECTURE.md`
- [x] **Domain 1: [Domain Name]** (`[path/to/module]`) — Explored via `repo-trace` & `repo-deepdive`
- [ ] **Domain 2: [Domain Name]** (`[path/to/module]`) — ⚠️ Unexplored (Blind Spot)
- [ ] **Domain 3: [Domain Name]** (`[path/to/module]`) — ⚠️ Unexplored (Blind Spot)
```

---

## 2. Next Action
- If any Tier-0 domain remains unchecked: run `/trace <domain>` or `/deep-dive <domain>` to eliminate the blind spot.
- When all core domains are checked: run `/verify` followed by `/export`.
