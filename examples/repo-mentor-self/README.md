# repo-mentor Self-Study Workspace

A real, fact-grounded study of this repository, produced with the tool itself and kept in the repo as the export demo.

## Contents
- `ARCHITECTURE.md` — positioning, module topology, live hotspots, invariants & trade-offs.
- `DEBUG_NOTES.md` — local debug commands, core structures, gotchas, and two limit drills.
- `traces/verify_pipeline.md` — end-to-end trace of the `verify` quality gate.
- `dist/index.html` — the compiled offline whitepaper (open it with the network disabled).

## Reproduce

```bash
repo-mentor verify . examples/repo-mentor-self/ --fix
repo-mentor export examples/repo-mentor-self/
```