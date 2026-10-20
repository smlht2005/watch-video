#!/usr/bin/env python3
"""Move archived folders into watch-output/<category>/ and rebuild index.md.

Usage:
  python3 scripts/organize.py            # move legacy flat folders (category from meta.json, else glossary, else 未分類)
  python3 scripts/organize.py --map map.json   # {"<folder name or video id>": "<category>"} overrides, stored in meta.json

Every category is checked against glossary/categories.json first; any invalid value aborts before a single folder moves.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import watch_archive as wa  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", help="JSON file: folder name or video ID -> category")
    args = ap.parse_args()
    overrides = json.loads(Path(args.map).read_text(encoding="utf-8")) if args.map else {}
    cats = wa.load_categories()

    plan, errors = [], []
    folders = [p for p in wa.OUT_ROOT.glob("*__*") if p.is_dir()] + [p for p in wa.OUT_ROOT.glob("*/*__*") if p.is_dir()]
    for d in sorted(folders):
        mp = d / "meta.json"
        if not mp.exists():
            continue
        meta = json.loads(mp.read_text(encoding="utf-8"))
        vid = meta.get("video_id", d.name.rpartition("__")[2])
        try:
            cat = wa.pick_category(overrides.get(d.name) or overrides.get(vid, ""), meta.get("category", ""), meta.get("glossaries", []), cats)
        except ValueError as e:
            errors.append(f"{d.name}: {e}")
            continue
        plan.append((d, meta, cat))
    if errors:
        sys.exit("nothing moved; fix these first:\n" + "\n".join(errors))

    for d, meta, cat in plan:
        meta["category"] = cat
        target = wa.OUT_ROOT / cat / d.name
        if target != d:
            target.parent.mkdir(exist_ok=True)
            shutil.move(str(d), str(target))
        (target / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    wa.update_index()
    print(f"organized {len(plan)} folder(s)")


if __name__ == "__main__":
    main()
