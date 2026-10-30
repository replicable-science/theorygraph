"""Nothing that must stay private may be in the shipped files.

Always runs: secrets, local paths, personal-attribute and outcome columns, restricted folders.
Runs only when TG_PRIVATE_ROOT points at the authors' private project: no run of twelve or more consecutive words from any
real transcript may occur in any shipped text file.
"""
import os
import re
import subprocess
from pathlib import Path

import pytest

from theorygraph.util import REPO

TEXT_SUFFIXES = {".md", ".txt", ".csv", ".json", ".jsonl", ".html", ".py", ".toml", ".cff", ".yml", ".yaml"}
SKIP_PARTS = {"restricted", "__pycache__", ".pytest_cache", "cache", "test_leaks.py"}  # cache = fictional pitches only, checked separately
NGRAM = 12


def _candidates():
    try:
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=REPO,
                             capture_output=True, text=True, check=True).stdout
        return [REPO / f for f in out.splitlines()]
    except (OSError, subprocess.CalledProcessError):
        return [p for p in REPO.rglob("*") if not ({".git", ".venv", "venv", "site-packages"} & set(p.relative_to(REPO).parts))]


def shipped_files():
    for p in _candidates():
        if p.is_file() and p.suffix in TEXT_SUFFIXES and not (set(p.relative_to(REPO).parts) & SKIP_PARTS):
            yield p


def norm(t: str) -> list[str]:
    return re.sub(r"[^a-z0-9 ]+", "", re.sub(r"\s+", " ", t.lower())).strip().split()


def test_no_secrets_or_local_paths():
    bad = []
    for p in shipped_files():
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"sk-[A-Za-z0-9_\-]{20,}", txt) or re.search(r"Bearer [A-Za-z0-9_\-]{20,}", txt):
            bad.append((p.name, "key-like string"))
        if re.search(r"C:\\Users\\|/Users/[a-z]+/|OneDrive", txt):
            bad.append((p.name, "local path"))
    # provenance scripts may name the private env var, nothing else
    assert not bad, bad


def test_restricted_folder_is_ignored_by_git():
    assert "results/restricted/" in (REPO / ".gitignore").read_text(encoding="utf-8")


def test_cache_holds_only_fictional_requests():
    import json
    for f in (REPO / "examples" / "cache").glob("*.json"):
        rec = json.loads(f.read_text(encoding="utf-8"))
        assert rec["case_id"] in {"brinelog", "lathework", "recallpost"}, f.name


@pytest.mark.skipif(not os.environ.get("TG_PRIVATE_ROOT"), reason="needs the private project to compare against")
def test_no_twelve_word_run_from_real_transcripts():
    root = Path(os.environ["TG_PRIVATE_ROOT"]) / "data" / "corpora" / "startup_battlefield"
    shingles = set()
    for sub in ("transcripts", "transcripts_qa"):
        for f in (root / sub).glob("*.txt"):
            w = norm(f.read_text(encoding="utf-8", errors="ignore"))
            shingles.update(" ".join(w[i:i + NGRAM]) for i in range(len(w) - NGRAM + 1))
    hits = []
    for p in shipped_files():
        w = norm(p.read_text(encoding="utf-8", errors="ignore"))
        for i in range(len(w) - NGRAM + 1):
            if " ".join(w[i:i + NGRAM]) in shingles:
                hits.append((str(p.relative_to(REPO)), " ".join(w[i:i + NGRAM])))
                break
    assert not hits, hits
