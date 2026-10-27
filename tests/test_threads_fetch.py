"""Tests for the Threads image-post entry. No network: pages and image bytes are injected. Run: python3 -m unittest discover -s tests -v"""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import threads_fetch as tf  # noqa: E402
import watch_archive as wa  # noqa: E402

CDN = "https://scontent-ord5-1.cdninstagram.com/v/t51.82787-15/"
MAIN = ('<meta property="og:title" content="王啟樺 (&#064;chihua.wang.3) on Threads" />'
        '<meta property="og:description" content="第一行&#xff0c;本文&#10;- 要點" /><meta property="og:type" content="article" />')
EMBED = (f'<img src="{CDN.replace("82787-15", "2885-19")}avatar.jpg?x=1">'
         + "".join(f'<img src="{CDN}p{i}.jpg?stp=a&amp;b=c">' for i in range(1, 4))
         + f'<img src="{CDN}p1.jpg?other=query">'            # same image, other query string: one page
         + '<img src="https://evil.example.com/x.jpg">'      # not Meta's CDN: ignored
         + '<img src="http://scontent.cdninstagram.com/y.jpg">')  # not https: ignored
POST = "https://www.threads.com/@chihua.wang.3/post/De9qij5FKBy"


def fake_get(main=MAIN, embed=EMBED, final=POST):
    def get(url):
        return (final, embed) if url.endswith("/embed") else (final, main)
    return get


class Parse(unittest.TestCase):
    def test_images_in_order_without_avatar_duplicates_or_foreign_hosts(self):
        urls = tf.parse_images(EMBED)
        self.assertEqual([u.split("?")[0].rsplit("/", 1)[1] for u in urls], ["p1.jpg", "p2.jpg", "p3.jpg"])
        self.assertIn("&b=c", urls[0])  # &amp; unescaped

    def test_json_escaped_url_has_no_trailing_backslash(self):
        blob = r'{"u":"https:\/\/scontent.cdninstagram.com\/v\/p1.jpg?stp=x\u0026_nc=y\"}'
        self.assertEqual(tf.parse_images(blob), ["https://scontent.cdninstagram.com/v/p1.jpg?stp=x&_nc=y"])

    def test_page_cap(self):
        many = "".join(f'<img src="{CDN}q{i}.jpg">' for i in range(tf.MAX_PAGES + 5))
        self.assertEqual(len(tf.parse_images(many)), tf.MAX_PAGES)

    def test_post_url_and_author(self):
        self.assertEqual(tf.parse_post_url(POST + "?xmt=1"), (POST, "chihua.wang.3", "De9qij5FKBy"))
        self.assertEqual(tf.author_name("王啟樺 (@chihua.wang.3) on Threads"), "王啟樺")
        with self.assertRaises(tf.ThreadsError):
            tf.parse_post_url("https://www.threads.com/login")

    def test_is_threads(self):
        self.assertTrue(tf.is_threads("https://www.threads.com/share/abc/"))
        self.assertFalse(tf.is_threads("https://www.youtube.com/watch?v=1"))

    def test_fetch_returns_caption_and_images_or_nothing_for_video_or_no_images(self):
        info = tf.fetch("https://www.threads.com/share/_x/", get=fake_get())
        self.assertEqual((info["post_id"], info["author"], len(info["images"])), ("De9qij5FKBy", "王啟樺", 3))
        self.assertIn("要點", info["caption"])
        self.assertEqual(tf.fetch(POST, get=fake_get(main=MAIN + '<meta property="og:video" content="x">')), {})
        with self.assertRaises(tf.ThreadsError):
            tf.fetch(POST, get=fake_get(embed="<html>login</html>"))
        # a bare .mp4 (the page's own UI assets) is no video signal
        self.assertTrue(tf.fetch(POST, get=fake_get(main=MAIN + '"uri":"https://static.cdninstagram.com/a.mp4"')))


class Archive(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        for mod, name, value in ((wa, "OUT_ROOT", self.root / "watch-output"), (wa, "ROOT", self.root)):
            old = getattr(mod, name)
            setattr(mod, name, value)
            self.addCleanup(setattr, mod, name, old)
        cat = self.root / "glossary"
        cat.mkdir()
        (cat / "categories.json").write_text(json.dumps({"categories": ["AI", "未分類"]}), encoding="utf-8")
        self.addCleanup(setattr, wa, "glossary_dir", wa.glossary_dir)
        wa.glossary_dir = lambda: cat
        self.calls = []

    def run_archive(self, **kw):
        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGB", (8, 8)).save(buf, "JPEG")
        def get_bytes(u):
            self.calls.append(u)
            return buf.getvalue()
        fetch = kw.pop("fetch", lambda url: tf.fetch(url, get=fake_get()))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return wa.archive_threads_post("https://www.threads.com/share/_x/", "AI", "", fetch=fetch, get_bytes=get_bytes, **kw)

    def folder(self):
        return next((self.root / "watch-output" / "AI").glob("*__De9qij5FKBy"))

    def test_skeleton(self):
        self.assertTrue(self.run_archive())
        d = self.folder()
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        self.assertEqual((meta["media_type"], meta["platform"], meta["video_id"], len(meta["slides"])), ("carousel", "Threads", "De9qij5FKBy", 3))
        self.assertEqual(sorted(p.name for p in (d / "frames").iterdir()), ["slide_01.jpg", "slide_02.jpg", "slide_03.jpg"])
        self.assertIn("要點", (d / "supplement.md").read_text(encoding="utf-8"))
        self.assertEqual(len(self.calls), 3)
        self.assertTrue(list(d.glob("*_report.md")))

    def test_rerun_keeps_handwritten_files_and_downloads_nothing_new(self):
        self.run_archive()
        d = self.folder()
        (d / "summary.md").write_text("# 我寫的摘要\n", encoding="utf-8")
        (d / "transcript.md").write_text("```\n[00:01] 我抄的\n```\n", encoding="utf-8")
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        meta["keywords"] = ["k"]
        meta["title"] = meta["title_override"] = "自訂標題"
        (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        self.calls.clear()
        self.run_archive()
        self.assertEqual(self.calls, [])
        self.assertEqual((d / "summary.md").read_text(encoding="utf-8"), "# 我寫的摘要\n")
        self.assertIn("我抄的", (d / "transcript.md").read_text(encoding="utf-8"))
        again = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        self.assertEqual((again["keywords"], again["title"]), (["k"], "自訂標題"))

    def test_rerun_with_more_pages_extends_slides_and_keeps_hand_fields(self):
        self.run_archive()
        d = self.folder()
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        meta["slides"][0]["title"] = "我寫的第一頁"
        meta["video_type"] = "carousel-note"
        meta["detail"] = "detailed"
        (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        more = EMBED + f'<img src="{CDN}p4.jpg">'
        self.run_archive(fetch=lambda url: tf.fetch(url, get=fake_get(embed=more)))
        again = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        self.assertEqual([sl["frame"] for sl in again["slides"]], [f"slide_0{i}.jpg" for i in range(1, 5)])
        self.assertEqual(again["slides"][0]["title"], "我寫的第一頁")
        self.assertEqual((again["video_type"], again["detail"], again["duration"]), ("carousel-note", "detailed", "4 頁（完整）"))

    def test_category_change_moves_the_folder(self):
        self.run_archive()
        (self.root / "glossary" / "categories.json").write_text(json.dumps({"categories": ["AI", "身心生活", "未分類"]}), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            wa.archive_threads_post("https://www.threads.com/share/_x/", "身心生活", "", fetch=lambda url: tf.fetch(url, get=fake_get()),
                                    get_bytes=lambda u: b"")
        self.assertFalse(list((self.root / "watch-output" / "AI").glob("*__De9qij5FKBy")))
        moved = next((self.root / "watch-output" / "身心生活").glob("*__De9qij5FKBy"))
        self.assertEqual(json.loads((moved / "meta.json").read_text(encoding="utf-8"))["category"], "身心生活")

    def test_video_post_falls_back_to_video_pipeline(self):
        self.assertFalse(self.run_archive(fetch=lambda url: {}))
        self.assertFalse((self.root / "watch-output").exists() and any((self.root / "watch-output").rglob("meta.json")))

    def test_fetch_failure_warns_and_falls_back(self):
        def boom(url):
            raise tf.ThreadsError("network: timeout")
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            ok = wa.archive_threads_post("https://www.threads.com/share/_x/", "AI", "", fetch=boom)
        self.assertFalse(ok)
        self.assertIn("network: timeout", err.getvalue())

    def test_image_download_error_stops_with_a_clear_message(self):
        def bad(u):
            raise OSError("reset")
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(io.StringIO()):
            wa.archive_threads_post("https://www.threads.com/share/_x/", "AI", "", fetch=lambda url: tf.fetch(url, get=fake_get()), get_bytes=bad)
        self.assertIn("download failed", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
