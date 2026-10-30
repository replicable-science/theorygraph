"""Rebuild transcripts from the public recordings listed in video_sources.csv.

STATUS: UNTESTED IN THIS FORM. The transcripts used in the study were made from local copies of the videos with the same
speech-recognition model and settings (faster-whisper, h2oai/faster-whisper-large-v3-turbo, English, beam size 5, voice-activity
filter, segments joined by a space). This script repeats those steps starting from the public links. Rebuilt transcripts will be close to,
not identical with, the originals (different audio cut, library versions, and hardware change the text slightly).

Needs: yt-dlp, ffmpeg on the PATH, and `pip install faster-whisper`. Check the terms of the video host before you run it;
the transcripts are third-party speech and stay on your machine (the output folder is git-ignored).

    python data/rebuild_transcripts.py --case pilot-853
    python data/rebuild_transcripts.py --all --out data/transcripts_rebuilt
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODEL_ID = "h2oai/faster-whisper-large-v3-turbo"


def to_seconds(hms: str) -> float:
    parts = [float(x) for x in hms.split(":")]
    return sum(p * 60 ** i for i, p in enumerate(reversed(parts)))


def fetch_audio(url: str, start: str, end: str, wav: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "src.%(ext)s"
        subprocess.check_call(["yt-dlp", "-f", "bestaudio/best", "-o", str(src), url])
        downloaded = next(Path(tmp).glob("src.*"))
        subprocess.check_call(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(downloaded), "-ss", str(to_seconds(start)),
                               "-to", str(to_seconds(end)), "-ar", "16000", "-ac", "1", str(wav)])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", help="one case id, e.g. pilot-853")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default=str(HERE / "transcripts_rebuilt"))
    args = ap.parse_args()
    if not (args.case or args.all):
        ap.error("give --case or --all")
    from faster_whisper import WhisperModel  # imported late so --help works without it

    model = WhisperModel(MODEL_ID)
    out = Path(args.out)
    rows = list(csv.DictReader((HERE / "video_sources.csv").open(encoding="utf-8")))
    for r in rows:
        if args.case and r["case_id"] != args.case:
            continue
        if not r["video_url"]:
            continue
        folder = out / ("transcripts" if r["segment"] == "PITCH" else "transcripts_qa")
        target = folder / f"{r['case_id']}.txt"
        if target.exists():
            continue
        folder.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "a.wav"
            fetch_audio(r["video_url"], r["start"], r["end"], wav)
            segs, _ = model.transcribe(str(wav), beam_size=5, language="en", vad_filter=True, word_timestamps=False)
            target.write_text(" ".join(s.text.strip() for s in segs if s.text.strip()), encoding="utf-8")
        print("wrote", target)


if __name__ == "__main__":
    main()
