"""Paths, hashing and small helpers shared by the package."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROMPTS = REPO / "prompts"
EXAMPLES = REPO / "examples"
CACHE = EXAMPLES / "cache"
DERIVED = REPO / "data" / "derived"
RESULTS = REPO / "results"
LOGS = REPO / "logs"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def write_json(path: Path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def read_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parse_json_reply(text: str) -> dict:
    """Parse a model reply that should be one JSON object (tolerates a code fence)."""
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def natural_key(pid: str):
    m = re.match(r"([A-Za-z]+)(\d+)$", str(pid))
    return (m.group(1), int(m.group(2))) if m else (str(pid), 0)
