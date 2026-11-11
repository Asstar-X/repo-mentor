"""repo_mentor.core.hotspots: Git Churn & Architectural Gravity Hotspot Analyzer.

Based on Adam Tornhill's 'Your Code as a Crime Scene' methodology.
Calculates revision frequency and code churn (insertions + deletions) via git log --numstat.
Ranks the top architectural hotspots using:
    Hotspot Score = Churn * log10(LOC + 10) * sqrt(Revisions)
Provides a graceful fallback for non-git directories.
"""

from __future__ import annotations

import math
import os
import subprocess
from pathlib import Path
from typing import Any

IGNORED_EXTENSIONS: set[str] = {
    ".lock",
    ".json",
    ".csv",
    ".tsv",
    ".svg",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".map",
    ".min.js",
    ".min.css",
    ".sum",
    ".bin",
    ".wasm",
    ".pyc",
}

IGNORED_PATHS: set[str] = {
    "node_modules/",
    "vendor/",
    ".git/",
    "target/",
    "dist/",
    "build/",
    "tests/fixtures/",
    "fixtures/",
    "docs/",
    "assets/",
    ".venv/",
    "venv/",
}


def _is_ignored(path_str: str) -> bool:
    posix_path = path_str.replace("\\", "/")
    for ign in IGNORED_PATHS:
        if ign in posix_path:
            return True
    ext = os.path.splitext(posix_path)[1].lower()
    return ext in IGNORED_EXTENSIONS


def get_git_hotspots(
    repo_dir: str | Path, max_commits: int = 300, top_n: int = 15
) -> dict[str, Any]:
    """Calculates git churn and architectural hotspot rankings with non-git fallback."""
    repo_path = Path(repo_dir).resolve()
    if not repo_path.is_dir():
        return {
            "error": f"Path is not a directory: {repo_dir}",
            "is_git_repo": False,
            "hotspots": [],
        }

    # 1. Check whether it's a git repository
    try:
        check_git = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False,
        )
        has_git = check_git.returncode == 0 and check_git.stdout.strip() == "true"
    except Exception:
        has_git = False

    # Graceful fallback for non-git directories
    if not has_git:
        fallback_hotspots: list[dict[str, Any]] = []
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in {"node_modules", "target", "vendor", ".git", "build", "dist"}
            ]
            for f in files:
                full_p = Path(root) / f
                rel_p = full_p.relative_to(repo_path).as_posix()
                if _is_ignored(rel_p):
                    continue
                try:
                    with open(full_p, "rb") as fp:
                        lc = sum(1 for _ in fp)
                    if lc > 0:
                        fallback_hotspots.append(
                            {
                                "path": rel_p,
                                "revisions": 1,
                                "churn": lc,
                                "loc": lc,
                                "hotspot_score": round(float(lc), 1),
                                "fallback": True,
                            }
                        )
                except Exception:
                    pass

        fallback_hotspots.sort(key=lambda x: x["hotspot_score"], reverse=True)
        for idx, h in enumerate(fallback_hotspots[:top_n], start=1):
            h["hotspot_rank"] = idx

        return {
            "is_git_repo": False,
            "message": "Not a git repository or git not available. Falling back to static size ranking.",
            "commits_analyzed": 0,
            "initial_commit": {},
            "total_active_files": len(fallback_hotspots),
            "hotspots": fallback_hotspots[:top_n],
        }

    # 2. Extract genesis / initial commit info
    initial_commit_info: dict[str, str] = {}
    try:
        init_cmd = subprocess.run(
            ["git", "-C", str(repo_path), "rev-list", "--max-parents=0", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        if init_cmd.returncode == 0:
            init_hash = init_cmd.stdout.strip().split("\n")[0]
            if init_hash:
                log_init = subprocess.run(
                    [
                        "git",
                        "-C",
                        str(repo_path),
                        "log",
                        "-1",
                        "--pretty=format:%h|%an|%ad|%s",
                        "--date=short",
                        init_hash,
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if log_init.returncode == 0 and log_init.stdout.strip():
                    parts = log_init.stdout.strip().split("|")
                    if len(parts) >= 4:
                        initial_commit_info = {
                            "hash": parts[0],
                            "author": parts[1],
                            "date": parts[2],
                            "subject": parts[3],
                        }
    except Exception:
        pass

    # 3. Extract churn from git log --numstat
    try:
        log_cmd = subprocess.run(
            [
                "git",
                "-C",
                str(repo_path),
                "log",
                f"-n{max_commits}",
                "--numstat",
                "--pretty=format:COMMIT:%h",
            ],
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        log_output = log_cmd.stdout
    except Exception as e:
        return {
            "error": f"Failed to execute git log: {str(e)}",
            "is_git_repo": True,
            "hotspots": [],
        }

    stats: dict[str, dict[str, int]] = {}

    for line in log_output.splitlines():
        line = line.strip()
        if not line or line.startswith("COMMIT:"):
            continue
        parts = line.split("\t")
        if len(parts) == 3:
            ins_str, del_str, file_path = parts
            if _is_ignored(file_path):
                continue
            if ins_str == "-" or del_str == "-":
                continue

            # Handle Git rename syntax: e.g., "{old => new}/path" or "old => new"
            if "=>" in file_path:
                if "{" in file_path and "}" in file_path:
                    prefix = file_path[: file_path.find("{")]
                    suffix = file_path[file_path.find("}") + 1 :]
                    middle = file_path[file_path.find("{") + 1 : file_path.find("}")]
                    new_mid = middle.split("=>")[-1].strip()
                    file_path = prefix + new_mid + suffix
                else:
                    file_path = file_path.split("=>")[-1].strip()

            try:
                ins = int(ins_str)
                dels = int(del_str)
            except ValueError:
                continue

            entry = stats.setdefault(file_path, {"revisions": 0, "churn": 0})
            entry["revisions"] += 1
            entry["churn"] += ins + dels

    ranked_hotspots: list[dict[str, Any]] = []
    for file_rel, data in stats.items():
        abs_path = repo_path / file_rel
        loc = 0
        exists = abs_path.is_file()
        if exists:
            try:
                with open(abs_path, "rb") as fp:
                    loc = sum(1 for _ in fp)
            except Exception:
                loc = 0

        # Only count existing files with meaningful content
        if exists and loc > 3:
            score = round(data["churn"] * math.log10(loc + 10) * math.sqrt(data["revisions"]), 1)
            ranked_hotspots.append(
                {
                    "path": file_rel.replace("\\", "/"),
                    "revisions": data["revisions"],
                    "churn": data["churn"],
                    "loc": loc,
                    "hotspot_score": score,
                }
            )

    ranked_hotspots.sort(key=lambda x: x["hotspot_score"], reverse=True)
    for idx, h in enumerate(ranked_hotspots[:top_n], start=1):
        h["hotspot_rank"] = idx

    return {
        "is_git_repo": True,
        "commits_analyzed": max_commits,
        "initial_commit": initial_commit_info,
        "total_active_files": len(ranked_hotspots),
        "hotspots": ranked_hotspots[:top_n],
    }
