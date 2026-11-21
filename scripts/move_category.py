#!/usr/bin/env python3
"""改領域：把單支影片搬到另一個領域，或把整個領域／子領域改名（目標已存在就是合併）。

預設只列出會做什麼（dry-run）；確認後加 --apply 才執行。

Usage:
  # (a) 搬單支影片（目標領域必須已在 glossary/categories.json 白名單）
  python3 scripts/move_category.py --video watch-output/<領域>/<資料夾> --to AI/TTS [--apply]

  # (b) 整個領域改名（舊名從白名單換成新名），(c) 目標已存在則合併（舊名從白名單移除）
  python3 scripts/move_category.py --from AI/Agent --to AI/GrokBot [--apply]

做的事（--apply）：改 meta.json 的 category（只動被搬的影片，保留原本結尾換行，不像 organize.py 會改到別支）、
搬資料夾、更新白名單（改名／合併時）、重建 watch-output/index.md、重匯 Obsidian（影片筆記與知識點檔名的領域前綴
會跟著改，舊檔由匯出的 manifest 清掉），最後掃 vault 的 [[連結]] 有沒有壞掉。
只列出、不自動改：CLAUDE.md／params.md 裡的領域清單文字、你自己的筆記裡指向舊檔名的連結。
不會自動 commit、也不會開 PR。
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import watch_archive as wa  # noqa: E402
import obsidian_export as oe  # noqa: E402

ROOT = wa.ROOT
CATS_PATH = ROOT / "glossary" / "categories.json"
DOCS = [ROOT / "CLAUDE.md", ROOT / ".claude" / "skills" / "watch-archive" / "references" / "params.md"]


def read_meta(folder: Path):
    raw = (folder / "meta.json").read_text(encoding="utf-8")
    return json.loads(raw), raw.endswith("\n")


def write_meta(folder: Path, meta: dict, trailing_newline: bool):
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + ("\n" if trailing_newline else ""),
                                      encoding="utf-8")


def all_folders():
    return sorted(p.parent for p in [*wa.OUT_ROOT.glob("*/*__*/meta.json"), *wa.OUT_ROOT.glob("*/*/*__*/meta.json")])


def confirmed_points(folder: Path) -> int:
    f = folder / "knowledge.md"
    if not f.exists():
        return 0
    n, on = 0, False
    for line in f.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            on = line.strip() == "## 已確認"
        elif on and line.startswith("### "):
            n += 1
    return n


def norm(cat: str, cats: list) -> str:
    """Whitelist spelling (simplified→traditional, case) via the archive's own picker; ValueError if not listed."""
    return wa.check_category(cat, cats)


def doc_mentions(name: str):
    return [p.relative_to(ROOT).as_posix() for p in DOCS if p.exists() and name in p.read_text(encoding="utf-8")]


def broken_links(vault: Path):
    names = {p.stem for p in vault.rglob("*.md")}
    bad = []
    for p in vault.rglob("*.md"):
        for m in re.findall(r"\[\[([^\]|#]+)", p.read_text(encoding="utf-8")):
            if m.strip() and m.strip() not in names:
                bad.append((p.relative_to(vault).as_posix(), m.strip()))
    return sorted(set(bad))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", help="watch-output/<領域>/<資料夾>：搬單支影片")
    ap.add_argument("--from", dest="src", help="舊領域名（整個領域改名／合併）")
    ap.add_argument("--to", required=True, help="新領域名")
    ap.add_argument("--apply", action="store_true", help="真的執行（沒加就只列出會做什麼）")
    ap.add_argument("--vault", default=None, help="自己的 vault（同 obsidian_export.py）；預設是 repo 內的 obsidian-vault/")
    args = ap.parse_args()
    if bool(args.video) == bool(args.src):
        sys.exit("give either --video <folder> or --from <old domain>")

    cats_doc = json.loads(CATS_PATH.read_text(encoding="utf-8"))
    cats = cats_doc["categories"]
    mode = "move"
    new_whitelist = None
    try:
        if args.video:
            target = norm(args.to, cats)  # 搬單支：目標必須已在白名單
            vd = Path(args.video).resolve()
            if not (vd / "meta.json").is_file():
                sys.exit(f"不是影片資料夾（找不到 meta.json）：{args.video}")
            try:
                vd.relative_to(wa.OUT_ROOT.resolve())
            except ValueError:
                sys.exit(f"--video 必須在 watch-output/ 底下：{args.video}")
            folders = [vd]
        else:
            old = norm(args.src, cats)
            folders = [d for d in all_folders() if (read_meta(d)[0].get("category") or "") == old]
            if not folders:
                sys.exit(f"「{old}」底下沒有影片，沒事可做")
            try:
                target = norm(args.to, cats)  # 目標已存在 → 合併
                mode = "merge"
                new_whitelist = [c for c in cats if c != old]
            except ValueError:  # 目標是新名字 → 改名
                target = args.to.strip()
                bad_name = (not target or target.count("/") > 1 or re.search(r'[\\:*?"<>|]', target)
                            or target.startswith("/") or target.endswith("/") or wa.to_traditional(target) != target)
                if bad_name:
                    sys.exit(f"新領域名稱不合規（最多一層「父/子」、不含特殊字元、中文要用繁體）：{target}")
                mode = "rename"
                new_whitelist = [target if c == old else c for c in cats]
    except ValueError as e:
        sys.exit(f"領域不在白名單（搬單支影片前請先新增領域）：{e}")

    root = wa.OUT_ROOT.resolve()
    plan = []
    for d in folders:
        meta, nl = read_meta(d)
        cur = meta.get("category") or d.resolve().parent.relative_to(root).as_posix()
        if cur == target:
            print(f"略過（已在 {target}）：{d.name}")
            continue
        plan.append((d, meta, nl, cur))
    if not plan:
        sys.exit("沒有需要搬的影片")
    conflicts = [d for d, _, _, _ in plan if (wa.OUT_ROOT / target / d.name).exists()]
    if conflicts:  # shutil.move 遇到同名目標會把來源塞進去變成 X/X，並覆寫到目標原有的 meta.json
        sys.exit(f"目標領域「{target}」已有同名資料夾，未搬任何東西（請先處理重複，例如刪掉較舊的那份）：\n  "
                 + "\n  ".join(d.name for d in conflicts))

    verb = {"move": "搬移", "rename": "領域改名", "merge": "合併領域"}[mode]
    print(f"{verb}：{'(dry-run，加 --apply 才執行)' if not args.apply else '執行中'}")
    pts = 0
    for d, meta, nl, cur in plan:
        k = confirmed_points(d)
        pts += k
        print(f"  {cur} → {target}  {d.name[:50]}  （已確認知識點 {k} 則）")
    print(f"  共 {len(plan)} 支影片、{pts} 則已確認知識點筆記會改檔名前綴")
    if new_whitelist is not None:
        print(f"  白名單：{'改名' if mode == 'rename' else '移除舊名'}（{args.src} → {target if mode == 'rename' else '併入 ' + target}）")
    old_names = sorted({cur for *_, cur in plan})
    for name in old_names:
        hits = doc_mentions(name)
        if hits:
            print(f"  提醒：{', '.join(hits)} 的領域清單文字仍寫著「{name}」，請手動改")
    if not args.apply:
        return

    vault = Path(args.vault) / "watch-archive" if args.vault else oe.DEFAULT_VAULT
    before = set(broken_links(vault)) if vault.exists() else set()  # 搬之前就待建立的概念節點不算
    for d, meta, nl, cur in plan:
        meta["category"] = target
        dest = wa.OUT_ROOT / target / d.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(d), str(dest))
        write_meta(dest, meta, nl)
        old_dir = d.parent
        try:
            old_dir.rmdir()  # 舊領域資料夾空了就刪（非空會失敗，忽略）
        except OSError:
            pass
    try:
        if new_whitelist is not None:
            cats_doc["categories"] = new_whitelist
            CATS_PATH.write_text(json.dumps(cats_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        wa.update_index()
        for d, *_ in plan:
            dest = wa.OUT_ROOT / target / d.name
            for p in oe.export(dest, vault, False):
                pass
        oe.write_index(vault)
    except Exception as exc:  # 資料夾已搬、後續步驟失敗：給復原指令，不要留在半套狀態而無提示
        print(f"ERROR：資料夾已搬到「{target}」，但後續步驟失敗：{exc}", file=sys.stderr)
        print("復原：git checkout -- . && git clean -fd watch-output obsidian-vault glossary；或修好原因後對各資料夾重跑 "
              "python3 scripts/obsidian_export.py <資料夾>，並檢查 glossary/categories.json 與 watch-output/index.md", file=sys.stderr)
        sys.exit(1)
    bad = [b for b in broken_links(vault) if b not in before]
    print(f"完成：搬了 {len(plan)} 支影片；Obsidian 知識點筆記改檔名 {pts} 則；搬移造成的新壞連結 {len(bad)} 條")
    for path, link in bad[:20]:
        print(f"  壞連結：{path} → [[{link}]]")
    if mode != "move" or any(not (wa.OUT_ROOT / c).exists() for c in old_names):
        print("提醒：空掉的舊領域若仍在白名單，請決定是否移除（搬單支時預設保留）")
    print("未 commit、未開 PR；請檢查 git diff 後再 commit。")


if __name__ == "__main__":
    main()
