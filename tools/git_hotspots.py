#!/usr/bin/env python3
"""
git_hotspots.py - Git Churn & Architectural Gravity Hotspot Analyzer
Part of repo-mentor skill.

Based on Adam Tornhill's 'Your Code as a Crime Scene' methodology.
Calculates file modification frequency (revisions) and code churn (insertions + deletions)
to identify the top architectural hotspots (the 20% of files carrying 80% of complexity).
"""

import os
import sys
import math
import json
import argparse
import subprocess
from pathlib import Path

IGNORED_EXTENSIONS = {
    ".lock", ".json", ".csv", ".tsv", ".svg", ".png", ".jpg", ".jpeg",
    ".gif", ".ico", ".pdf", ".zip", ".tar", ".gz", ".map", ".min.js",
    ".min.css", ".sum"
}

IGNORED_PATHS = {
    "node_modules/", "vendor/", ".git/", "target/", "dist/", "build/",
    "tests/fixtures/", "fixtures/", "docs/", "assets/"
}


def is_ignored(path_str: str) -> bool:
    posix_path = path_str.replace("\\", "/")
    for ign in IGNORED_PATHS:
        if ign in posix_path:
            return True
    ext = os.path.splitext(posix_path)[1].lower()
    return ext in IGNORED_EXTENSIONS


def get_git_hotspots(repo_dir: str, max_commits: int = 500, top_n: int = 15) -> dict:
    repo_path = Path(repo_dir).resolve()
    
    try:
        check_git = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, check=False
        )
        has_git = check_git.returncode == 0 and check_git.stdout.strip() == "true"
    except Exception:
        has_git = False

    if not has_git:
        fallback_hotspots = []
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {"node_modules", "target", "vendor", ".git", "build", "dist"}]
            for f in files:
                full_p = Path(root) / f
                rel_p = full_p.relative_to(repo_path).as_posix()
                if is_ignored(rel_p):
                    continue
                try:
                    with open(full_p, "r", encoding="utf-8", errors="replace") as fp:
                        lc = sum(1 for _ in fp)
                    if lc > 0:
                        fallback_hotspots.append({
                            "file": rel_p,
                            "revisions": 1,
                            "churn": lc,
                            "complexity_score": lc,
                            "hotspot_rank": 0,
                            "fallback": True
                        })
                except Exception:
                    pass
        fallback_hotspots.sort(key=lambda x: x["complexity_score"], reverse=True)
        for idx, h in enumerate(fallback_hotspots[:top_n], start=1):
            h["hotspot_rank"] = idx
        return {
            "is_git_repo": False,
            "message": "Not a git repository or git command not available. Falling back to static size ranking.",
            "hotspots": fallback_hotspots[:top_n]
        }

    initial_commit_info = {}
    try:
        init_cmd = subprocess.run(
            ["git", "-C", str(repo_path), "rev-list", "--max-parents=0", "HEAD"],
            capture_output=True, text=True, check=False
        )
        if init_cmd.returncode == 0:
            init_hash = init_cmd.stdout.strip().split("\n")[0]
            log_init = subprocess.run(
                ["git", "-C", str(repo_path), "log", "-1", "--pretty=format:%h|%an|%ad|%s", "--date=short", init_hash],
                capture_output=True, text=True, check=False
            )
            if log_init.returncode == 0 and log_init.stdout.strip():
                parts = log_init.stdout.strip().split("|")
                if len(parts) >= 4:
                    initial_commit_info = {
                        "hash": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "subject": parts[3]
                    }
    except Exception:
        pass

    try:
        log_cmd = subprocess.run(
            ["git", "-C", str(repo_path), "log", f"-n{max_commits}", "--numstat", "--pretty=format:COMMIT:%h"],
            capture_output=True, text=True, check=False, encoding="utf-8", errors="replace"
        )
        log_output = log_cmd.stdout
    except Exception as e:
        return {"error": f"Failed to execute git log: {str(e)}"}

    stats = {}

    for line in log_output.splitlines():
        line = line.strip()
        if not line or line.startswith("COMMIT:"):
            continue
        parts = line.split("\t")
        if len(parts) == 3:
            ins_str, del_str, file_path = parts
            if is_ignored(file_path):
                continue
            
            if ins_str == "-" or del_str == "-":
                continue
            if "=>" in file_path:
                if "{" in file_path and "}" in file_path:
                    prefix = file_path[:file_path.find("{")]
                    suffix = file_path[file_path.find("}")+1:]
                    middle = file_path[file_path.find("{")+1:file_path.find("}")]
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
            entry["churn"] += (ins + dels)

    ranked_hotspots = []
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
        
        if exists and loc > 5:
            score = round(data["churn"] * math.log10(loc + 10) * math.sqrt(data["revisions"]), 1)
            ranked_hotspots.append({
                "path": file_rel.replace("\\", "/"),
                "revisions": data["revisions"],
                "churn": data["churn"],
                "loc": loc,
                "hotspot_score": score
            })

    ranked_hotspots.sort(key=lambda x: x["hotspot_score"], reverse=True)

    return {
        "is_git_repo": True,
        "commits_analyzed": max_commits,
        "initial_commit": initial_commit_info,
        "total_active_files": len(ranked_hotspots),
        "hotspots": ranked_hotspots[:top_n]
    }


def main():
    parser = argparse.ArgumentParser(description="Calculate git churn and architectural hotspot rankings.")
    parser.add_argument("path", nargs="?", default=".", help="Root directory of the git repository")
    parser.add_argument("--commits", type=int, default=300, help="Number of recent commits to analyze (default: 300)")
    parser.add_argument("--top", type=int, default=15, help="Number of top hotspot files to output (default: 15)")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")
    args = parser.parse_args()

    result = get_git_hotspots(args.path, max_commits=args.commits, top_n=args.top)
    if args.pretty:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
