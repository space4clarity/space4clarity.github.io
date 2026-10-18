"""Failure-path checks for unattended publication; no model/network calls."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("daily", Path(__file__).with_name("daily.py"))
daily = importlib.util.module_from_spec(spec)
spec.loader.exec_module(daily)


class DailyChecks(unittest.TestCase):
    def setUp(self):
        self.quote = "A precise quotation that actually appears within this supplied source passage."
        self.passages = [{"text": "Before. " + self.quote + " After.", "start_paragraph": 1, "end_paragraph": 3}]
        self.post = {
            "title": "What we owe the things we make", "summary": "A reflection on responsibility after the moment of creation.",
            "topic": "Responsibility continues after creation", "passage_index": 0, "quote": self.quote,
            "paragraphs": [" ".join(["An ordinary example invites a careful reading of this difficult situation."] * 8)] * 6,
            "question": "What responsibility remains after the first decision?",
            "date": "2026-10-17", "slug": "2026-10-17-example", "book_title": "Frankenstein", "author": "Mary Shelley",
            "book_id": 84, "source_start": 1, "source_end": 3, "source_url": "https://www.gutenberg.org/ebooks/84"
        }

    def test_quote_verification_rejects_invented_words(self):
        daily.validate_post(self.post, self.passages, [])
        self.post["quote"] = self.quote.replace("precise", "invented")
        with self.assertRaisesRegex(ValueError, "verbatim"):
            daily.validate_post(self.post, self.passages, [])

    def test_duplicate_topic_rejected(self):
        previous = copy.deepcopy(self.post)
        previous["title"] = "A completely different title"
        with self.assertRaisesRegex(ValueError, "Repeated topic"):
            daily.validate_post(self.post, self.passages, [previous])

    def test_additional_unverified_quotes_rejected(self):
        self.post["paragraphs"][0] += ' Someone said "invented words".'
        with self.assertRaisesRegex(ValueError, "verified quotation field"):
            daily.validate_post(self.post, self.passages, [])

    def test_model_text_is_escaped(self):
        self.post["title"] = '<script>alert("x")</script>'
        rendered = daily.render_post(self.post)
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)

    def test_retry_push_without_creating_another_commit(self):
        calls = []
        def fake_git(*args):
            calls.append(args)
            return ""
        with patch.object(daily, "git", fake_git):
            daily.publish([self.post])
        self.assertEqual([args[0] for args in calls], ["status", "push"])

    def test_home_and_archive_rerender_is_idempotent(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "index.html"
            path.write_text('<section>\n        <article class="post-preview">Old personal post</article>\n</section>', encoding="utf-8")
            daily.update_listing(path, [self.post])
            first = path.read_text(encoding="utf-8")
            daily.update_listing(path, [self.post])
            self.assertEqual(first, path.read_text(encoding="utf-8"))
            self.assertIn("Old personal post", first)
            self.assertEqual(first.count('class="post-preview daily-preview"'), 1)

    def test_wrong_or_missing_book_markers_rejected(self):
        with self.assertRaisesRegex(ValueError, "markers"):
            daily.book_paragraphs("<html>Not a book</html>")

    def test_failed_site_check_rolls_back_all_publication_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "posts").mkdir()
            auto = root / ".automation"
            auto.mkdir()
            original = '<section>\n        <article class="post-preview">Existing post</article>\n</section>'
            for name in ["index.html", "archive.html"]:
                (root / name).write_text(original, encoding="utf-8")
            with patch.object(daily, "ROOT", root), patch.object(daily, "AUTO", auto), patch.object(daily, "check_site", side_effect=ValueError("broken link")):
                with self.assertRaisesRegex(ValueError, "broken link"):
                    daily.save_post(self.post, [])
            self.assertEqual((root / "index.html").read_text(encoding="utf-8"), original)
            self.assertEqual((root / "archive.html").read_text(encoding="utf-8"), original)
            self.assertEqual(list((root / "posts").iterdir()), [])
            self.assertFalse((root / "feed.xml").exists())
            self.assertFalse((auto / "history.json").exists())


if __name__ == "__main__":
    unittest.main()
