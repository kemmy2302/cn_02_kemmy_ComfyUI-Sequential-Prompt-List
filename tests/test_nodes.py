import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nodes import OPTSequentialPromptList, OPTSequentialPromptListString


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

    def test_empty_records_encode_prefix_and_suffix(self):
        result = OPTSequentialPromptList().build(
            self.FakeClip(), '{"records": []}', "character", "quality"
        )
        self.assertEqual(
            result[0][0], [["conditioning", "character\nquality"]]
        )

    def test_string_output_keeps_order_and_joins_all_parts(self):
        state = {"records": [
            {"id": "1", "enabled": True, "prompt": "school"},
            {"id": "2", "enabled": False, "prompt": "skip"},
            {"id": "3", "enabled": True, "prompt": "class"},
        ]}
        result = OPTSequentialPromptListString().build(
            json.dumps(state), "character", "quality"
        )
        self.assertEqual(result[0], [
            "character\nschool\nquality",
            "character\nclass\nquality",
        ])

    def test_string_output_omits_blank_optional_parts(self):
        state = {"records": [{"id": "1", "enabled": True, "prompt": "school"}]}
        result = OPTSequentialPromptListString().build(json.dumps(state))
        self.assertEqual(result[0], ["school"])

    def test_string_output_empty_records_joins_prefix_and_suffix(self):
        result = OPTSequentialPromptListString().build(
            '{"records": []}', "character", "quality"
        )
        self.assertEqual(result[0], ["character\nquality"])

    def test_string_output_empty_records_and_empty_fixed_prompts(self):
        result = OPTSequentialPromptListString().build('{"records": []}')
        self.assertEqual(result[0], [""])

if __name__ == "__main__":
    unittest.main()
