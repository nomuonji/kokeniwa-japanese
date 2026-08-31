#!/usr/bin/env python3
"""Build expanded purchaser CSV files from canonical book JSONL data."""
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "data" / "book_series.json").read_text(encoding="utf-8"))["books"]
FIELDS = [
    "Japanese", "Kana", "Romaji", "Meaning", "Part of speech", "Chapter",
    "Register", "Usage note", "Example 1 (Japanese)", "Example 1 (English)",
    "Example 2 (Japanese)", "Example 2 (English)", "Contrast", "Misuse note",
]


def build(key):
    cfg = CONFIG[key]
    source = ROOT / cfg["source"]
    rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
    output = ROOT / "anki" / cfg["bonus_file"]
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(FIELDS)
        for row in rows:
            contrast = row.get("contrast", [])
            if isinstance(contrast, list):
                contrast = " / ".join(contrast)
            writer.writerow([
                row.get("jp", ""), row.get("kana", ""), row.get("romaji", ""), row.get("en", ""),
                row.get("pos", ""), row.get("chapter_title", row.get("category", "")),
                row.get("register", row.get("safety_label", "")), row.get("usage_note_en", ""),
                row.get("example_ja", ""), row.get("example_en", ""),
                row.get("example_ja_2", ""), row.get("example_en_2", ""),
                contrast, row.get("misuse_note_en", row.get("real_life_use", "")),
            ])
    print(f"[{key}] {len(rows)} rows -> {output}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("book", choices=list(CONFIG))
    args = parser.parse_args()
    build(args.book)


if __name__ == "__main__":
    main()
