# /history (Alias for /overview)

> 💡 `/history` is part of the macro reconnaissance in [`/overview`](overview.md), backed by [`skills/repo-recon/SKILL.md`](../skills/repo-recon/SKILL.md).

Git churn hotspots and commit volatility are analyzed automatically during `/overview` to identify the system's architectural gravity centers.
Run [`/overview`](overview.md) or invoke CLI directly:
```bash
repo-mentor hotspots <target_path> --commits 300 --top 10
```
