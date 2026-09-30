import json
import re
import unicodedata
from pathlib import Path


def safe_name(value, suffix=".json"):
    name = unicodedata.normalize("NFC", str(value or "")).strip()
    if not name or name in {".", ".."}:
        raise ValueError("name is empty")
    if Path(name).name != name or "/" in name or "\\" in name:
        raise ValueError("directory components are not allowed")
    if re.search(r'[<>:"/\\|?*\x00-\x1f]', name):
        raise ValueError("name contains unsupported characters")
    name = name.rstrip(". ")
    if not name:
        raise ValueError("name is empty")
    if suffix and not name.lower().endswith(suffix):
        name += suffix
    stem = name[: -len(suffix)] if suffix and name.lower().endswith(suffix) else name
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
    if stem.upper() in reserved:
        raise ValueError("reserved filename")
    return name


def atomic_write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def read_json(path, fallback):
    path = Path(path)
    if not path.is_file():
        return fallback
    return json.loads(path.read_text(encoding="utf-8-sig"))
