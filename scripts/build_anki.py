# -*- coding: utf-8 -*-
"""Build Anki-importable CSV decks from the vocab sets (comma-separated, no HTML).

Output: anki/{slug}_anki.csv for every non-mature set in VOCAB_SETS.
- Front = Japanese word / Back = meaning + reading + example / tags = set key.
- Header carries Anki directives (deck / notetype / tags column). HTML off.

Usage:
    python scripts/build_anki.py            # all public sets
    python scripts/build_anki.py n5 travel  # only the named sets
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "site"))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from lib import config  # noqa: E402
from lib.data_loader import load_vocab  # noqa: E402

OUT = ROOT / "anki"


def para(*parts):
    return "\n\n".join(p for p in parts if p)


def header(deck):
    return [
        "#separator:comma",
        "#html:false",
        f"#deck:{deck}",
        "#notetype:Basic",
        "#tags column:3",
    ]


def build_set(set_key):
    vset = config.VOCAB_SETS[set_key]
    words = load_vocab(set_key)
    rows = []
    for w in words:
        front = w["jp"]
        reading = w["kana"] + (f" · {w['romaji']}" if w.get("romaji") else "")
        example = "\n".join(p for p in [w.get("example_ja", ""), w.get("example_en", "")] if p)
        back = para(f"{w['en']}\n{reading}", example)
        tags = " ".join([set_key] + list(w.get("tags", [])))
        rows.append([front, back, tags])
    OUT.mkdir(exist_ok=True)
    path = OUT / f"{vset['slug']}_anki.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        for h in header(vset["title"]):
            f.write(h + "\n")
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        writer.writerows(rows)
    print(f"{set_key}: {len(rows)} notes -> {path.relative_to(ROOT)}")


def main():
    keys = sys.argv[1:] or config.PUBLIC_SETS
    for key in keys:
        if key not in config.VOCAB_SETS:
            sys.exit(f"unknown set: {key}")
        build_set(key)


if __name__ == "__main__":
    main()
