# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-11

### Added
- Fully offline single-file HTML whitepaper export: Mermaid.js 10.9.1 is vendored
  and inlined (`repo_mentor/export/assets/mermaid.min.js`), zero CDN requests.
- Documentation smoke tests (`tests/test_docs_smoke.py`): every documented CLI
  flag is validated against the real Typer command tree, and the documented
  workflow runs end-to-end in CI.
- Agent Skills spec tests (`tests/test_skill_spec.py`): frontmatter validity,
  bilingual descriptions, resource-link existence, `.agents/skills` symlink
  consistency (with Windows text-file fallback).
- Bilingual (Chinese/English) descriptions for the root skill and all six
  sub-skills; methodology and template resources linked from each skill.
- Frontmatter (`description`, `argument-hint`) for `commands/*.md`, positioned as
  optional short aliases of the skill-name commands.
- Self-study demo under `examples/repo-mentor-self/` (Grade A, 100% grounding)
  with a compiled whitepaper and README screenshot.
- Release workflow (`.github/workflows/release.yml`): tag-triggered build, wheel
  asset assertion, PyPI trusted publishing, GitHub Release attachments.
- `THIRD_PARTY_NOTICES.md` for the vendored Mermaid.js MIT license.
- Coverage gate in CI (`--cov-fail-under=88`).

### Changed
- Command names now equal skill names (`/repo-recon`, `/repo-core`, `/repo-trace`,
  `/repo-drill`, `/repo-verify`, `/repo-export`); short aliases remain optional.
- README (EN/ZH) rewritten: source-first installation, real CLI signatures,
  real architecture diagram, and the scoring rubric matching `judge.py`.
- `__version__` is derived from installed package metadata; `pyproject.toml` is
  the single source of truth.
- Root skill frontmatter uses the valid `tools` key (replaces `allowed-tools`).

### Fixed
- Documented CLI flags that never existed (`ast --symbol`, `export --output`).
- Dead references to removed N1-N8/P1-P5 framework artifacts in both READMEs.
- Mermaid diagrams now render on page load (explicit node list passed to
  `mermaid.run`), with source-view fallback when rendering fails.

[1.0.0]: https://github.com/Asstar-X/repo-mentor/releases/tag/v1.0.0