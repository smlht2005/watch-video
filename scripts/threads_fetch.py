#!/usr/bin/env python3
"""Archive a Threads image post (carousel) that yt-dlp cannot handle: caption + every page image -> folder skeleton.

What Threads exposes without a login (verified 2026-10-27):
  <post url>         og:description = the caption, og:title = '<name> (@handle) on Threads', og:image = page 1 only
  <post url>/embed   every page image (cdninstagram.com JPG, ~1254 px); the first '.../t51.2885-19/...' is the avatar
A /share/<code>/ link redirects to the post url. Only public pages are read: no cookies, no login; a private or
login-walled post fails with a clear message and the caller falls back to "upload the images yourself".

scaffold() writes the skeleton the video pipeline expects (meta.json with media_type "carousel", frames.json, frames/,
transcript.md / summary.md placeholders, supplement.md holding the caption). The page text is still transcribed by
Claude from the images (step 4); nothing here reads text out of the pictures.

Usage (normally called by watch_archive.py): python3 scripts/threads_fetch.py <threads url> [--category AI]
"""
import datetime as dt
import html
import json
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

UA = {"User-Agent": "Mozilla/5.0"}
CDN_SUFFIXES = ("cdninstagram.com", "fbcdn.net")  # page images only from Meta's CDN, never an arbitrary host in the HTML
MAX_PAGES = 30
MAX_BYTES = 15 * 1024 * 1024
AVATAR = "t51.2885-19"  # Instagram CDN path segment of profile pictures
POST_RE = re.compile(r"^/@([^/]+)/post/([\w-]+)")
IMG_RE = re.compile(r"https:[^\"'\s<>]+?\.(?:jpg|webp)[^\"'\s<>]*")
# video posts carry og:video / og:type video; a bare '.mp4' is no signal (the page's own UI assets are .mp4 files)
VIDEO_RE = re.compile(r'property="og:video|property="og:type"[^>]*content="video|video_versions')


class ThreadsError(Exception):
    """Fetch or parse failure; the message says which kind (network / login wall / page changed / no images)."""


def is_threads(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    return host.endswith("threads.com") or host.endswith("threads.net")


def http_get(url: str, timeout: int = 30):
    """(final url, html) of a public page."""
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
            return r.geturl(), r.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        raise ThreadsError(f"network: {type(e).__name__}: {e}") from e


def meta_content(page: str, prop: str) -> str:
    m = re.search(rf'<meta[^>]+(?:property|name)="{re.escape(prop)}"[^>]+content="([^"]*)"', page)
    return html.unescape(m.group(1)).strip() if m else ""


def parse_post_url(final_url: str):
    """(canonical post url, handle, post id) from a resolved url; ThreadsError when it is not a post page."""
    u = urlparse(final_url)
    m = POST_RE.match(u.path)
    if not m:
        raise ThreadsError(f"not a post page (login wall or unsupported link): {final_url}")
    return f"https://www.threads.com/@{m.group(1)}/post/{m.group(2)}", m.group(1), m.group(2)


def parse_images(embed_html: str):
    """Post page images in order, de-duplicated by path (query strings differ), avatar removed."""
    seen, out = set(), []
    for m in IMG_RE.finditer(embed_html):
        url = html.unescape(m.group(0)).replace("\\/", "/").replace("\\u0026", "&").replace("\\u00253D", "%3D")
        key = url.split("?")[0]
        if key in seen:
            continue
        seen.add(key)
        host = urlparse(url).netloc.lower()
        if AVATAR in key or urlparse(url).scheme != "https" or not host.endswith(CDN_SUFFIXES):
            continue
        out.append(url)
    return out[:MAX_PAGES]


def author_name(og_title: str) -> str:
    """'王啟樺 (@chihua.wang.3) on Threads' -> '王啟樺'."""
    return re.sub(r"\s*\(@[^)]*\)\s*on Threads\s*$", "", og_title).strip()


def fetch(url: str, get=http_get) -> dict:
    """Resolve, read caption and page images. Returns {} when the post has a video (let the video pipeline take it)."""
    final, page = get(url)
    post_url, handle, post_id = parse_post_url(final)
    if VIDEO_RE.search(page):
        return {}
    _, embed = get(post_url + "/embed")
    images = parse_images(embed)
    if not images:
        raise ThreadsError("page changed or login required: no page images found in /embed")
    return {"post_url": post_url, "handle": handle, "post_id": post_id,
            "author": author_name(meta_content(page, "og:title")),
            "caption": meta_content(page, "og:description"), "images": images}


def download(url: str, dest: Path, get_bytes=None):
    def fetch_bytes(u):
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40) as r:
            data = r.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError(f"image larger than {MAX_BYTES // 1024 // 1024} MB")
        return data

    try:
        dest.write_bytes((get_bytes or fetch_bytes)(url))
    except Exception as e:  # noqa: BLE001
        raise ThreadsError(f"network: image download failed ({type(e).__name__}: {e})") from e


def slide(n: int) -> str:
    return f"slide_{n:02d}.jpg"


def scaffold(dest: Path, info: dict, share_url: str, title: str, category: str, get_bytes=None) -> dict:
    """Create or refresh the archive folder. Hand-written files and hand-curated meta fields of an existing folder
    are never overwritten; only missing page images are downloaded and the source fields refreshed."""
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "frames").mkdir(exist_ok=True)
    n_pages = len(info["images"])
    for n, url in enumerate(info["images"], 1):
        if not (dest / "frames" / slide(n)).exists():
            download(url, dest / "frames" / slide(n), get_bytes)
    ts = lambda n: f"00:{n:02d}"  # noqa: E731  page N sits at 00:0N: the pipeline's time axis is the page number
    frames = [{"file": slide(n), "t": ts(n), "reason": "carousel-page"} for n in range(1, n_pages + 1)]
    (dest / "frames.json").write_text(json.dumps(frames, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    today = dt.date.today().isoformat()
    mp = dest / "meta.json"
    prev = json.loads(mp.read_text(encoding="utf-8")) if mp.exists() else {}
    meta = {
        "url": info["post_url"], "share_url": share_url, "platform": "Threads", "video_id": info["post_id"],
        "title": prev.get("title") or title, "title_override": prev.get("title_override", ""), "category": category,
        "media_type": "carousel", "uploader": f"{info['author']}（@{info['handle']}）" if info["author"] else f"@{info['handle']}",
        "duration": f"{n_pages} 頁（完整）", "detail": "balanced",
        "transcript_source": "圖片文字（逐頁人工抄錄，非語音轉錄）", "detected_language": "zh", "language_source": "manual",
        "needs_zh_translation": False, "glossaries": prev.get("glossaries", []),
        "keywords": prev.get("keywords", []), "known_asr_errors": prev.get("known_asr_errors", []),
        "first_archived": prev.get("first_archived", today), "last_updated": today,
        "slides": prev.get("slides") or [{"start": ts(n), "frame": slide(n), "title": f"第 {n} 頁", "note": "", "keywords": []}
                                          for n in range(1, n_pages + 1)],
    }
    mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not (dest / "transcript.md").exists():
        lines = "\n".join(f"[{ts(n)}] （待抄錄第 {n} 頁圖上文字）" for n in range(1, n_pages + 1))
        (dest / "transcript.md").write_text(
            f"# 逐頁抄錄（圖片文字，非語音；時間碼＝頁碼）\n\n```\n{lines}\n```\n", encoding="utf-8")
    if not (dest / "summary.md").exists():
        (dest / "summary.md").write_text(f"# 摘要：{meta['title']}\n\n_待補：請看圖逐頁抄錄後撰寫摘要。_\n", encoding="utf-8")
    if info["caption"] and not (dest / "supplement.md").exists():
        quoted = info["caption"].strip()
        (dest / "supplement.md").write_text(
            f"# 補充資料\n\n## 貼文本文（Threads 頁面 og:description，逐字；作者主張，未查證）\n{quoted}\n", encoding="utf-8")
    return meta


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    args = ap.parse_args()
    try:
        info = fetch(args.url)
    except ThreadsError as e:
        sys.exit(f"threads fetch failed: {e}")
    if not info:
        sys.exit("post has a video: use watch_archive.py")
    print(json.dumps({k: v for k, v in info.items() if k != "images"} | {"pages": len(info["images"])}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
