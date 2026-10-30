"""One thin chat interface with two modes.

replay  (default) answer from a stored reply whose request hash matches exactly. Nothing leaves the machine
        and the result is identical on every run. A miss is an error, never a silent fallback.
live    send the request to any OpenAI-compatible endpoint, store the reply, and log the call.

The endpoint is plain HTTP (`urllib`), so the same code reaches OpenAI, a local Ollama or vLLM server, or any
gateway that speaks the chat-completions protocol. Set THEORYGRAPH_BASE_URL and THEORYGRAPH_API_KEY.
Nothing here depends on a particular vendor, and a model is just a name you pass in.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from .util import CACHE, LOGS, canonical_json, sha256_text


class ReplayMiss(RuntimeError):
    pass


def request_key(model: str, temperature: float | None, messages: list[dict]) -> str:
    return sha256_text(canonical_json({"model": model, "temperature": temperature, "messages": messages}))


class Chat:
    def __init__(self, mode: str = "replay", model: str = "gpt-4o-mini", temperature: float | None = 0.0,
                 cache_dir: Path = CACHE, log_path: Path | None = LOGS / "runs.jsonl",
                 store_messages: bool = True, json_mode: bool = True):
        if mode not in ("replay", "live"):
            raise ValueError("mode must be 'replay' or 'live'")
        self.mode, self.model, self.temperature = mode, model, temperature
        self.cache_dir, self.log_path = Path(cache_dir), (Path(log_path) if log_path else None)
        self.store_messages, self.json_mode = store_messages, json_mode
        self.base_url = os.environ.get("THEORYGRAPH_BASE_URL", "https://api.openai.com/v1").rstrip("/")

    # ------------------------------------------------------------------ public
    def complete(self, messages: list[dict], *, pass_name: str, case_id: str, prompt_sha256: str) -> dict:
        key = request_key(self.model, self.temperature, messages)
        path = self.cache_dir / f"{key[:20]}.json"
        if path.exists():
            rec = json.loads(path.read_text(encoding="utf-8"))
            self._log(pass_name, case_id, key, cached=True, prompt_sha256=prompt_sha256, usage=rec.get("usage"), latency=0.0)
            return {"text": rec["response_text"], "key": key, "cached": True, "created_at": rec.get("created_at")}
        if self.mode == "replay":
            raise ReplayMiss(
                f"no stored reply for pass={pass_name} case={case_id} model={self.model} (request {key[:12]}). "
                "Replay needs the exact stored request. Re-run with --live to create it.")
        text, usage, latency = self._call(messages)
        rec = {
            "request_sha256": key, "pass": pass_name, "case_id": case_id, "model": self.model, "temperature": self.temperature,
            "endpoint_host": self.base_url.split("//")[-1].split("/")[0], "prompt_sha256": prompt_sha256,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "usage": usage, "response_text": text,
        }
        if self.store_messages:
            rec["messages"] = messages
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        self._log(pass_name, case_id, key, cached=False, prompt_sha256=prompt_sha256, usage=usage, latency=latency)
        return {"text": text, "key": key, "cached": False, "created_at": rec["created_at"]}

    # ------------------------------------------------------------------ internals
    def _call(self, messages: list[dict]):
        api_key = os.environ.get("THEORYGRAPH_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if not api_key and "api.openai.com" in self.base_url:
            raise RuntimeError("live mode needs THEORYGRAPH_API_KEY (or OPENAI_API_KEY) in the environment")
        body: dict = {"model": self.model, "messages": messages}
        if self.temperature is not None:
            body["temperature"] = self.temperature
        if self.json_mode:
            body["response_format"] = {"type": "json_object"}
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions", data=json.dumps(body).encode("utf-8"), method="POST",
            headers={"Content-Type": "application/json", **({"Authorization": f"Bearer {api_key}"} if api_key else {})})
        last = None
        for attempt in range(4):
            t0 = time.time()
            try:
                with urllib.request.urlopen(req, timeout=240) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"], data.get("usage"), round(time.time() - t0, 2)
            except urllib.error.HTTPError as e:
                detail = e.read().decode("utf-8", "ignore")[:300]
                last = f"HTTP {e.code}: {detail}"
                if e.code not in (429, 500, 502, 503, 504):
                    break
            except Exception as e:  # network error
                last = repr(e)
            time.sleep(2 ** attempt)
        raise RuntimeError(f"live call failed: {last}")

    def _log(self, pass_name, case_id, key, *, cached, prompt_sha256, usage, latency):
        if not self.log_path or cached:  # the log records calls that were made, not replays
            return
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        row = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "mode": self.mode, "pass": pass_name,
               "case_id": case_id, "model": self.model, "request_sha256": key[:20], "cached": cached,
               "prompt_sha256": prompt_sha256[:16], "usage": usage, "latency_s": latency}
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
