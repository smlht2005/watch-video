#!/usr/bin/env python3
"""Print GitHub links for the user to confirm an archived report before any PR / merge (.claude/skills/watch-archive/references/deliver.md, step 7).

The branch must already be pushed. Links point at the branch, so they work before the PR is merged.

Usage: python3 scripts/review_links.py watch-output/<領域>/<資料夾> [--skip-second-pass]

閘門：2026-11-21 起歸檔的影片，meta.json 沒有 second_pass.done 就不印確認連結（先做第二輪逐行校稿，
再 python3 scripts/proofread_check.py <資料夾> --mark-done --fixes N）；更早歸檔的只印警告。
"""
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

REVIEW_FILES = ("summary.md", "transcript.zh.md", "supplement.md", "sop.md", "mindmap.md", "mindmap.png", "knowledge.md", "links.md")


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


def wait_confirm_lines(folder: Path) -> list:
    """Lines about waitConfirm/ (local only, gitignored): the index.md path, a warning if it is missing, nothing if no folder."""
    wc = folder.resolve() / "waitConfirm"
    if not wc.is_dir():
        return []
    index = wc / "index.md"
    if not index.is_file():
        return [f"WARNING: {wc} 沒有 index.md（上次剪音檔可能中斷），請重跑 clip_check.py --wait-confirm"]
    return [f"待確認音檔（本機）: {index}", "  GitHub 上看不到這些音檔，要在本機打開 index.md 點 ▶ 重聽"]


def candidate_lines(folder: Path) -> list:
    """列出 knowledge.md「## 候選」區的知識點標題（編號），供使用者用編號確認。"""
    f = folder / "knowledge.md"
    if not f.exists():
        return []
    out, in_cand = [], False
    for line in f.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_cand = line.strip() == "## 候選"
        elif in_cand and line.startswith("### "):
            out.append(f"  {len(out) + 1}. {line[4:].strip()}")
    return ["知識點候選（請用編號回覆：確認 1,3／刪 2／改 4）："] + out if out else []


GATE_FROM = "2026-11-21"  # 這天起歸檔的影片必須完成第二輪校稿才給確認連結


def second_pass_status(folder: Path):
    """回傳 (done, enforced)。"""
    try:
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    except Exception as exc:  # 讀不到 meta.json 就不能判斷閘門，不要悄悄放行
        sys.exit(f"ERROR: 讀不到 {folder}/meta.json，無法檢查第二輪校稿閘門：{exc}")
    done = bool((meta.get("second_pass") or {}).get("done"))
    first = meta.get("first_archived") or ""
    enforced = first == "" or first >= GATE_FROM  # 沒有 first_archived 視為新影片，照樣把關
    return done, enforced


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    skip = "--skip-second-pass" in sys.argv
    if len(args) != 1:
        sys.exit(__doc__)
    folder = Path(args[0])
    done, enforced = second_pass_status(folder)
    if not done:
        msg = ("第二輪逐行校稿尚未完成（meta.json 沒有 second_pass.done）：先跑 python3 scripts/proofread_check.py "
               f"{args[0]} 看機械提示，用 Read 逐行重讀並修正，再加 --mark-done --fixes N。")
        if enforced and not skip:
            sys.exit("ERROR: " + msg + "（要略過加 --skip-second-pass）")
        print("WARNING: " + msg, file=sys.stderr)
    rel = folder.resolve().relative_to(Path.cwd().resolve()).as_posix()
    files = sorted(p.name for p in folder.iterdir()
                   if p.name.endswith(("_report.md", "_report.docx", "_操作SOP.md", "_操作SOP.docx")) or p.name in REVIEW_FILES)
    run = lambda *a: subprocess.run(a, capture_output=True, text=True, check=True).stdout.strip()
    for label, url in build_links(repo_slug(run("git", "remote", "get-url", "origin")), run("git", "branch", "--show-current"), rel, files):
        print(f"{label}: {url}")
    for line in wait_confirm_lines(folder):
        print(line)
    for line in candidate_lines(folder):
        print(line)


if __name__ == "__main__":
    main()
