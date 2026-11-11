"""Agent Skills 规范一致性测试：frontmatter、资源挂链与 .agents 符号链接。

纯标准库实现（不依赖 PyYAML），覆盖根技能与 skills/ 下全部子技能。
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
ROOT_SKILL = REPO_ROOT / "SKILL.md"
AGENTS_SKILLS_DIR = REPO_ROOT / ".agents" / "skills"
COMMANDS_DIR = REPO_ROOT / "commands"

VALID_TOOLS = {
    "Read",
    "Write",
    "Edit",
    "Glob",
    "Grep",
    "Bash",
    "AskUserQuestion",
    "WebFetch",
    "WebSearch",
    "Agent",
    "NotebookEdit",
    "Skill",
}

CJK_RE = re.compile(r"[一-鿿]")
ASCII_WORD_RE = re.compile(r"[A-Za-z]{3,}")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """极简 YAML frontmatter 解析：支持单行值与 >- / | 折叠块。"""
    lines = text.splitlines()
    assert lines and lines[0].strip() == "---", "missing frontmatter opener"
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    fields: dict[str, str] = {}
    i = 1
    while i < end:
        m = re.match(r"^([A-Za-z0-9_-]+):(.*)$", lines[i])
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in (">", ">-", "|", "|-"):
            block = []
            i += 1
            while i < end and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            fields[key] = " ".join(p for p in block if p)
        else:
            fields[key] = val.strip("'\"")
            i += 1
    return fields, "\n".join(lines[end + 1 :])


def _all_skill_files() -> list[Path]:
    return [ROOT_SKILL] + sorted(SKILLS_DIR.glob("*/SKILL.md"))


def test_frontmatter_name_description_and_body():
    for skill_file in _all_skill_files():
        text = skill_file.read_text(encoding="utf-8")
        fields, body = _parse_frontmatter(text)

        expected_name = skill_file.parent.name
        assert fields.get("name") == expected_name, (
            f"{skill_file}: name {fields.get('name')!r} != directory {expected_name!r}"
        )
        assert re.fullmatch(r"[a-z0-9-]+", fields["name"]), f"{skill_file}: bad name format"

        desc = fields.get("description", "")
        assert desc, f"{skill_file}: missing description"
        assert "\n" not in desc, f"{skill_file}: description must be single-line"
        assert len(desc) <= 1024, f"{skill_file}: description too long ({len(desc)})"
        assert CJK_RE.search(desc), f"{skill_file}: description missing Chinese"
        assert ASCII_WORD_RE.search(desc), f"{skill_file}: description missing English"

        assert len(body.splitlines()) < 500, f"{skill_file}: body exceeds 500 lines"
        assert not re.search(r"\bTODO:|\bFIXME\b", text), f"{skill_file}: unresolved marker"


def test_tools_are_valid_and_root_has_bash():
    for skill_file in _all_skill_files():
        fields, _ = _parse_frontmatter(skill_file.read_text(encoding="utf-8"))
        if "tools" not in fields:
            continue
        tools = {t.strip() for t in fields["tools"].split(",") if t.strip()}
        assert tools <= VALID_TOOLS, f"{skill_file}: invalid tools {tools - VALID_TOOLS}"
        if skill_file == ROOT_SKILL:
            assert "Bash" in tools, "root skill must allow Bash for the CLI engine"


def test_resource_links_resolve():
    docs = _all_skill_files() + sorted(COMMANDS_DIR.glob("*.md"))
    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        for target in LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part = target.split("#", 1)[0]
            resolved = (doc.parent / path_part).resolve()
            assert resolved.exists(), f"{doc}: broken link {target!r}"


def test_agents_symlinks_consistent():
    skill_names = {p.name for p in SKILLS_DIR.iterdir() if p.is_dir()}
    agent_entries = {p.name for p in AGENTS_SKILLS_DIR.iterdir()}
    assert agent_entries == skill_names, "`.agents/skills` must mirror `skills/`"

    for name in sorted(skill_names):
        entry = AGENTS_SKILLS_DIR / name
        canonical = (SKILLS_DIR / name).resolve()
        if entry.is_symlink():
            assert entry.resolve() == canonical, f"{entry}: symlink target drifted"
        else:
            # Windows checkout with core.symlinks=false degrades to a text file
            # containing the link target path.
            target = entry.read_text(encoding="utf-8").strip()
            assert (entry.parent / target).resolve() == canonical, (
                f"{entry}: degraded symlink content {target!r} does not point at {canonical}"
            )


def test_command_aliases_have_frontmatter():
    for cmd in sorted(COMMANDS_DIR.glob("*.md")):
        fields, _ = _parse_frontmatter(cmd.read_text(encoding="utf-8"))
        desc = fields.get("description", "")
        assert desc, f"{cmd}: missing description frontmatter"
        assert "\n" not in desc and len(desc) <= 1024, f"{cmd}: bad description"
        if "argument-hint" in fields:
            assert fields["argument-hint"], f"{cmd}: empty argument-hint"
