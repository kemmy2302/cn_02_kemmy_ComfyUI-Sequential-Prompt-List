import json
import uuid


def _clean(value):
    return str(value or "").strip()


def _join_prompt(*parts):
    return "\n".join(part for part in (_clean(value) for value in parts) if part)


def _parse_json(raw, fallback):
    if isinstance(raw, (dict, list)):
        return raw
    try:
        return json.loads(str(raw or ""))
    except (TypeError, ValueError, json.JSONDecodeError):
        return fallback



class OPTSequentialPromptList:
    """Encode one ordered conditioning item per enabled GUI record."""

    RETURN_TYPES = ("CONDITIONING",)
    RETURN_NAMES = ("conditioning",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "build"
    CATEGORY = "Ordered Prompt Tools"
    DESCRIPTION = "Encode enabled prompt records from top to bottom with optional prefix and suffix inputs."

    @classmethod
    def INPUT_TYPES(cls):
        default = json.dumps(
            {
                "version": 1,
                "records": [
                    {
                        "id": str(uuid.uuid4()),
                        "enabled": True,
                        "title": "List Item 001",
                        "prompt": "",
                    }
                ],
            },
            ensure_ascii=False,
        )
        return {
            "required": {
                "clip": ("CLIP",),
                "records_json": (
                    "STRING",
                    {"default": default, "multiline": True, "dynamicPrompts": False},
                ),
            },
            "optional": {
                "prefix_prompt": ("STRING", {"forceInput": True}),
                "suffix_prompt": ("STRING", {"forceInput": True}),
            },
        }

    def build(
        self,
        clip,
        records_json,
        prefix_prompt="",
        suffix_prompt="",
    ):
        state = _parse_json(records_json, {})
        records = state.get("records", []) if isinstance(state, dict) else []
        records = [
            record
            for record in records
            if isinstance(record, dict)
            and record.get("enabled", True)
            and _clean(record.get("prompt"))
        ]
        if not records:
            prompt = _join_prompt(prefix_prompt, suffix_prompt)
            tokens = clip.tokenize(prompt)
            return ([clip.encode_from_tokens_scheduled(tokens)],)

        conditionings = []
        for record in records:
            record_prompt = _clean(record.get("prompt"))
            prompt = _join_prompt(prefix_prompt, record_prompt, suffix_prompt)
            tokens = clip.tokenize(prompt)
            conditionings.append(clip.encode_from_tokens_scheduled(tokens))

        return (conditionings,)


class OPTSequentialPromptListString:
    """Build one ordered prompt string per enabled GUI record."""

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "build"
    CATEGORY = "Ordered Prompt Tools"
    DESCRIPTION = (
        "Combine optional prefix and suffix inputs with each enabled prompt record, "
        "then emit the completed strings from top to bottom."
    )

    @classmethod
    def INPUT_TYPES(cls):
        default = json.dumps(
            {
                "version": 1,
                "records": [
                    {
                        "id": str(uuid.uuid4()),
                        "enabled": True,
                        "title": "List Item 001",
                        "prompt": "",
                    }
                ],
            },
            ensure_ascii=False,
        )
        return {
            "required": {
                "records_json": (
                    "STRING",
                    {"default": default, "multiline": True, "dynamicPrompts": False},
                ),
            },
            "optional": {
                "prefix_prompt": ("STRING", {"forceInput": True}),
                "suffix_prompt": ("STRING", {"forceInput": True}),
            },
        }

    def build(self, records_json, prefix_prompt="", suffix_prompt=""):
        state = _parse_json(records_json, {})
        records = state.get("records", []) if isinstance(state, dict) else []
        prompts = [
            _join_prompt(prefix_prompt, record.get("prompt"), suffix_prompt)
            for record in records
            if isinstance(record, dict)
            and record.get("enabled", True)
            and _clean(record.get("prompt"))
        ]
        if not prompts:
            prompts = [_join_prompt(prefix_prompt, suffix_prompt)]

        return (prompts,)


NODE_CLASS_MAPPINGS = {
    "OPTSequentialPromptList": OPTSequentialPromptList,
    "OPTSequentialPromptListString": OPTSequentialPromptListString,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OPTSequentialPromptList": "cn_02_kemmy_Sequential Prompt List",
    "OPTSequentialPromptListString": "cn_02_kemmy_Sequential Prompt List (String)",
}
