import tempfile
import unittest
from pathlib import Path

from storage import atomic_write_json, read_json, safe_name


class StorageTests(unittest.TestCase):
    def test_safe_name_keeps_japanese(self):
        self.assertEqual(safe_name("学校シーン"), "学校シーン.json")
        self.assertEqual(safe_name("学校シーン.json"), "学校シーン.json")

    def test_safe_name_rejects_directories_and_invalid_characters(self):
        for value in ("../secret", "folder/file", r"folder\file", "bad?.json"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    safe_name(value)

    def test_unicode_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / safe_name("日本語リスト")
            payload = {"version": 1, "records": [{"prompt": "学校へ行く"}]}
            atomic_write_json(path, payload)
            self.assertEqual(read_json(path, {}), payload)


if __name__ == "__main__":
    unittest.main()
