"""Build the Kindle reader-bonus CSV from the canonical reading corpus."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "reading_problems.jsonl"
OUTPUT = ROOT / "anki" / "japanese_reading_200_anki.csv"


def main():
    rows = [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != 200:
        raise SystemExit(f"Expected 200 rows, found {len(rows)}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Japanese", "English", "Category", "Reading point"])
        writer.writerows((r["sentence_ja"], r["translation_en"], r["category"], r["point"]) for r in rows)
    print(OUTPUT)


if __name__ == "__main__":
    main()
