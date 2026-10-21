#!/usr/bin/env python3
"""Print GitHub links for the user to confirm an archived report before any PR / merge (SKILL step 7).

The branch must already be pushed. Links point at the branch, so they work before the PR is merged.

Usage: python3 scripts/review_links.py watch-output/<領域>/<資料夾>
"""
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

REVIEW_FILES = ("summary.md", "transcript.zh.md", "supplement.md", "sop.md")


def repo_slug(remote_url: str) -> str:
    """owner/repo from an https/ssh remote, including the local-proxy form http://.../git/owner/repo."""
    m = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?/?$", remote_url.strip())
    if not m:
        raise ValueError(f"cannot read owner/repo from remote '{remote_url}'")
    return m.group(1)


def build_links(slug: str, branch: str, folder: str, files) -> list:
    base = f"https://github.com/{slug}"
    b = quote(branch, safe="/")
    out = [("資料夾", f"{base}/tree/{b}/{quote(folder)}")]
    out += [(name, f"{base}/blob/{b}/{quote(folder + '/' + name)}") for name in files]
    out.append(("與 main 的差異（開 PR 前看這個）", f"{base}/compare/main...{b}"))
    return out


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    folder = Path(sys.argv[1])
    rel = folder.resolve().relative_to(Path.cwd().resolve()).as_posix()
    files = sorted(p.name for p in folder.iterdir()
                   if p.name.endswith(("_report.md", "_report.docx", "_操作SOP.docx")) or p.name in REVIEW_FILES)
    run = lambda *a: subprocess.run(a, capture_output=True, text=True, check=True).stdout.strip()
    for label, url in build_links(repo_slug(run("git", "remote", "get-url", "origin")), run("git", "branch", "--show-current"), rel, files):
        print(f"{label}: {url}")


if __name__ == "__main__":
    main()
