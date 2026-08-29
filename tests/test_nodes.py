import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nodes import OPTSequentialPromptList


class SequentialPromptListTests(unittest.TestCase):
    class FakeClip:
        def tokenize(self, text):
            return {"text": text}

        def encode_from_tokens_scheduled(self, tokens):
            return [["conditioning", tokens["text"]]]

    def test_enabled_records_keep_order(self):
        state = {"records": [
            {"id": "1", "enabled": True, "prompt": "school"},
            {"id": "2", "enabled": False, "prompt": "skip"},
            {"id": "3", "enabled": True, "prompt": "class"},
        ]}
        result = OPTSequentialPromptList().build(
            self.FakeClip(), json.dumps(state), "character", "quality"
        )
        self.assertEqual(result[0][0], [["conditioning", "character\nschool\nquality"]])
        self.assertEqual(result[0][1], [["conditioning", "character\nclass\nquality"]])

    def test_empty_records_fail(self):
        with self.assertRaises(ValueError):
            OPTSequentialPromptList().build(self.FakeClip(), '{"records": []}')


if __name__ == "__main__":
    unittest.main()
