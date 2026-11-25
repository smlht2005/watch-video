#!/usr/bin/env python3
"""把 watch-output 的資料夾與其中以 <stem> 命名的檔案，由舊順序 <日期>_<平台>_<標題>__<ID>
改成新順序 <標題>_<日期>_<平台>__<ID>（2026-11-25 使用者指定）。

預設 dry-run，只列清單；加 --apply 才改名。改完另外要：
  python3 -c "import sys; sys.path.insert(0,'scripts'); import watch_archive as w; w.update_index()"
  python3 scripts/obsidian_export.py --all
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_report as br  # noqa: E402
import watch_archive as wa  # noqa: E402


def is_legacy(name: str) -> bool:
    return bool(br._OLD_NAME_RE.match(name.rpartition("__")[0] or name)) and not br._NEW_NAME_RE.match(name.rpartition("__")[0] or name)


def plan():
    out = []
    for mp in sorted([*wa.OUT_ROOT.glob("*/*__*/meta.json"), *wa.OUT_ROOT.glob("*/*/*__*/meta.json")]):
        d = mp.parent
        if not is_legacy(d.name):
            continue
        title, date, platform, vid = br.parse_folder_name(d.name)
        out.append((d, d.with_name(br.make_folder_name(date, platform, title, vid))))
    return out


def stem_of(name: str) -> str:
    return br.file_stem(Path(name))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    items = plan()
    targets = [n for _, n in items]
    dup = {t for t in targets if targets.count(t) > 1}
    exists = [n for _, n in items if n.exists()]
    for old, new in items:
        print(f"{old.relative_to(wa.OUT_ROOT)}  ->  {new.name}")
    print(f"\n共 {len(items)} 個資料夾；目標重名 {len(dup)}；目標已存在 {len(exists)}")
    if dup or exists:
        sys.exit("有衝突，不改名")
    if not a.apply:
        print("dry-run，未改動。確認後加 --apply")
        return
    nfiles = 0
    for old, new in items:
        t0, d0, p0, v0 = br.parse_folder_name(old.name)
        old_stem, new_stem = f"{d0}_{p0}_{t0[:20].rstrip(chr(45))}__{v0}", stem_of(new.name)
        old.rename(new)
        for base in (new, new / "media"):
            if not base.is_dir():
                continue
            for f in base.iterdir():
                if f.is_file() and f.name.startswith(old_stem):
                    f.rename(f.with_name(new_stem + f.name[len(old_stem):]))
                    nfiles += 1
    print(f"已改名 {len(items)} 個資料夾、{nfiles} 個以 stem 命名的檔案")


if __name__ == "__main__":
    main()
