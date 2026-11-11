# repo-mentor Source Walkthrough & Debug Journal

> **Repository**: `repo-mentor`
> **Ecosystem**: Python (pytest)

---

## 1. Local Debugging & Smoke Run Commands

### Build & Test Commands
```bash
pip install -e ".[dev,ast]"
pytest -q          # 99+ tests, < 2s
ruff check .
mypy repo_mentor
```

### Golden Breakpoint Call Stack (verify command)
```text
1. repo_mentor/cli.py:292        verify() — Typer ingress
2. anchor_verifier.py:566        verify_study_anchors() — fan-out over *.md
3. anchor_verifier.py:342        AnchorVerifier.verify_item() — three gates
4. mermaid_verifier.py:246       verify_study_mermaid() — lint + optional repair
```

---

## 2. Core Structures & Critical Gotchas

### 1. Core Data Structures
- [repo_mentor/core/parser.py#L461-L542] `SymbolIndex`: file → symbols/calls maps; built once per judge/verifier run, `max_depth=3`.
- [repo_mentor/verification/judge.py#L35-L51] `EvaluationReport`: Pydantic model; `dimension_scores` carries D1–D5, `violations` aggregates all gate failures.

### 2. System Invariants & Subtle Gotchas
1. **Diagram counter is global**: `_DIAGRAM_COUNTER` in html_compiler.py only resets inside `compile_study_html`. Calling `build_full_html_page` directly in tests keeps incrementing — assert on presence, not exact numbering.
2. **f-string brace doubling**: the whole HTML page is one f-string; any literal JS `{` must be `{{`. The vendored Mermaid bundle is injected as a single `{mermaid_js}` placeholder precisely to avoid re-escaping 3 MB of JS.
3. **Judge D2/D3 are keyword heuristics**: headings like "Trade-offs" or "Golden Path" earn points ([repo_mentor/verification/judge.py#L165-L194]). A doc can game them — treat the score as a lint signal, not proof of understanding.

---

## 3. Limit Scenario Hypothesis & Drills

### Limit Drill Scenario 1: Air-Gapped Whitepaper Review (Offline Rendering)
- **Failure Scenario**: An engineer opens the exported whitepaper in an air-gapped lab; the old CDN loader fails all three mirrors and every diagram degrades to source text.
- **Architectural Focus**: Zero external runtime dependencies; render path must not touch the network.
- **Reference Solution**: The compiler inlines the vendored mermaid@10.9.1 bundle via `_load_mermaid_js` ([repo_mentor/export/html_compiler.py#L25-L31]); a regression test asserts no `<script src=` survives in the output.
- **Architectural Verdict**: Offline rendering is now a compile-time guarantee, not a runtime hope; the cost is ~3.3 MB per whitepaper.

### Limit Drill Scenario 2: Anchor Drift After Refactor (Fact Decay)
- **Failure Scenario**: A target repo inserts 40 lines at the top of a file; every `#L120-L145` citation in existing study notes now points at the wrong code.
- **Architectural Focus**: Citations must decay loudly, never silently — gate 2 (line bounds) and gate 3 (symbol grounding) in [repo_mentor/verification/anchor_verifier.py#L342-L346].
- **Reference Solution**: `repo-mentor verify <repo> <notes> --fix` re-resolves drifted symbols through `SymbolIndex` and rewrites anchors; unresolvable ones are reported as hallucinations and penalized in D1.
- **Architectural Verdict**: Drift tolerance is bounded — small shifts auto-heal, renamed or deleted symbols fail closed.