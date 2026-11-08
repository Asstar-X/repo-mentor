# Contributing to repo-mentor

Thank you for your interest in contributing to **repo-mentor**! We are building the universal, zero-fluff codebase deep-reading assistant for developers and AI coding agents.

Please take a moment to review this guide before submitting code, methodologies, or issue reports.

---

## Engineering Philosophy: Zero "AI-Flavor"

At `repo-mentor`, our defining ethos is **engineering rigor over marketing buzzwords**. When contributing to documentation, methodologies, or analysis algorithms:

- **Anchor to Code Facts**: Never cite abstract concepts without physical code locations (`path/to/file.py:42-88`).
- **Surface Invariants & Trade-offs**: Real systems have trade-offs (memory vs. latency, consistency vs. availability). Never produce uncritical praise.
- **Strictly Ban Buzzword Fluff**: Eliminate empty transitional phrases ("seamlessly integrates", "cutting-edge paradigm", "robust comprehensive solution"). State directly *what* the component does and *how* it handles edge cases.

---

## Development Setup

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Git
- `pip` or modern packaging tools (`uv`, `pipx`)

### Initial Setup
```bash
# 1. Clone your fork
git clone https://github.com/<your-username>/repo-mentor.git
cd repo-mentor

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install in editable mode with development & AST dependencies
pip install --upgrade pip
pip install -e ".[dev,ast]"
```

---

## Development Workflow

### 1. Branching Strategy
- Always create a descriptive branch off `main`:
  ```bash
  git checkout -b feat/ast-symbol-cache
  # or
  git checkout -b fix/mermaid-cycle-detection
  ```

### 2. Code Standards & Tooling
All code must pass our automated linting, typing, and testing checks:

- **Linting & Formatting (Ruff)**:
  ```bash
  ruff check .
  ruff format --check .
  ```
- **Type Checking (Mypy)**:
  ```bash
  mypy repo_mentor
  ```
- **Automated Tests (Pytest)**:
  ```bash
  pytest
  # With coverage:
  pytest --cov=repo_mentor --cov-report=term-missing
  ```

### 3. Adding New Features or Engines
- Ensure all new public functions and classes have explicit type annotations.
- Include unit tests in `tests/` covering both happy paths and boundary/failure cases (e.g., malformed syntax, cyclic imports, non-existent files).
- Keep changes minimal and surgical—avoid unrelated reformatting.

---

## Deliverables & Documentation Style

If you are updating documentation or methodologies:
1. Preserve markdown linting hygiene (valid headings, clean code fences).
2. Validate any Mermaid diagrams using the built-in verifier or CLI tool.
3. Keep CLI commands documented in both `README.md` and Typer CLI help strings.

---

## Pull Request Process

1. **Self-Check**: Run the full suite locally before pushing:
   ```bash
   ruff check . && mypy repo_mentor && pytest
   ```
2. **Commit Messages**: Write clear, imperative commit messages (e.g., `feat(ast): add Go interface lexer`, `fix(cli): resolve relative path error in scanner`).
3. **Open a PR**: Fill out the Pull Request template describing the problem, proposed solution, and test evidence.
4. **CI Verification**: Ensure all GitHub Actions matrix jobs (Ubuntu, macOS, Windows across Python 3.10-3.12) pass cleanly.

Thank you for helping build a more rigorous, fact-grounded codebase reading experience!
