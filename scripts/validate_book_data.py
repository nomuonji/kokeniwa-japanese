#!/usr/bin/env python3
"""Validate canonical book data at data and publication quality gates."""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "data" / "book_series.json"
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
HTML_RE = re.compile(r"<(?:script|iframe|object|embed|style)\b", re.I)

COMMON_REQUIRED = {
    "id", "jp", "kana", "romaji", "en", "pos", "example_ja", "example_en",
    "category", "chapter", "chapter_title", "register", "usage_note_en",
    "review_status",
}
PUBLICATION_REQUIRED = COMMON_REQUIRED | {
    "subtype", "contrast", "example_ja_2", "example_en_2", "misuse_note_en",
}


def load_rows(path):
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{number}: invalid JSON: {exc}") from exc
    return rows


def validate(key, cfg, publication=False):
    errors, warnings = [], []
    path = ROOT / cfg["source"]
    if not path.is_file():
        return [f"missing source: {path}"], warnings
    try:
        rows = load_rows(path)
    except ValueError as exc:
        return [str(exc)], warnings
    expected = int(cfg["expected_count"])
    if len(rows) != expected:
        errors.append(f"expected {expected} rows, found {len(rows)}")
    required = PUBLICATION_REQUIRED if publication else COMMON_REQUIRED
    ids, heads, examples = [], [], []
    for row in rows:
        label = f"row {row.get('id', '?')}"
        missing = sorted(field for field in required if field not in row)
        empty = sorted(field for field in required if field in row and row[field] in (None, "", []))
        if missing:
            errors.append(f"{label}: missing {missing}")
        if empty:
            errors.append(f"{label}: empty {empty}")
        ids.append(row.get("id"))
        heads.append(row.get("jp"))
        examples.append(row.get("example_ja"))
        if row.get("review_status") not in {"pending", "approved", "rejected"}:
            errors.append(f"{label}: invalid review_status")
        if row.get("review_status") == "approved":
            approved_empty = sorted(
                field for field in PUBLICATION_REQUIRED
                if field not in row or row[field] in (None, "", [])
            )
            if approved_empty:
                errors.append(f"{label}: approved row has incomplete editorial fields {approved_empty}")
        if publication and row.get("review_status") != "approved":
            errors.append(f"{label}: publication requires review_status=approved")
        joined = " ".join(str(value) for value in row.values())
        if CONTROL_RE.search(joined):
            errors.append(f"{label}: control character found")
        if HTML_RE.search(joined):
            errors.append(f"{label}: dangerous HTML found")
        if len(str(row.get("example_ja", ""))) > 180:
            warnings.append(f"{label}: unusually long Japanese example; review for quotation risk")
        if key == "anime" and row.get("safety_label") is None:
            errors.append(f"{label}: anime data requires safety_label")
        if key == "anime" and row.get("safety_label") not in {
            "Safe", "Casual", "Rude", "Fandom", "Recognition only"
        }:
            errors.append(f"{label}: invalid anime safety_label")
        if key == "anime" and row.get("review_status") == "approved":
            anime_required = ("speaker_image", "real_life_use", "example_ja_2", "example_en_2", "contrast")
            anime_empty = [field for field in anime_required if row.get(field) in (None, "", [])]
            if anime_empty:
                errors.append(f"{label}: approved anime row has incomplete usage fields {anime_empty}")
            if "Confirm current nuance" in row.get("usage_note_en", ""):
                errors.append(f"{label}: approved anime row retains draft usage note")
    if ids != list(range(1, expected + 1)):
        errors.append("ids must be consecutive and ordered from 1")
    for label, values in (("headword", heads), ("Japanese example", examples)):
        dupes = [value for value, count in Counter(values).items() if value and count > 1]
        if dupes:
            errors.append(f"duplicate {label}: {dupes[:5]}")
    chapters = Counter(row.get("chapter") for row in rows)
    if key == "onomatopoeia" and chapters != Counter({i: 10 for i in range(1, 26)}):
        errors.append(f"onomatopoeia chapters must be 25 x 10; found {dict(chapters)}")
    if key == "anime" and chapters != Counter({i: 10 for i in range(1, 26)}):
        errors.append(f"anime chapters must be 25 x 10; found {dict(chapters)}")
    if key == "collocations" and chapters != Counter({i: 50 for i in range(1, 11)}):
        errors.append(f"collocation chapters must be 10 x 50; found {dict(chapters)}")
    if key == "anime" and publication:
        sections = Counter(row.get("section") for row in rows)
        target = Counter({"dialogue": 100, "story": 50, "production": 40, "fandom": 60})
        if sections != target:
            errors.append(f"anime publication sections must be {dict(target)}; found {dict(sections)}")
    chapter_titles = {}
    for row in rows:
        chapter_titles.setdefault(row.get("chapter"), set()).add(row.get("chapter_title"))
    inconsistent = {chapter: sorted(titles) for chapter, titles in chapter_titles.items() if len(titles) != 1}
    if inconsistent:
        errors.append(f"inconsistent chapter titles: {inconsistent}")
    return errors, warnings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("book", choices=["all", "onomatopoeia", "anime", "collocations"])
    parser.add_argument("--publication", action="store_true", help="Require completed editorial fields and approval")
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text(encoding="utf-8"))["books"]
    keys = list(config) if args.book == "all" else [args.book]
    failed = False
    for key in keys:
        errors, warnings = validate(key, config[key], args.publication)
        print(f"[{key}] {config[key]['source']}")
        for warning in warnings:
            print(f"  WARNING: {warning}")
        if errors:
            failed = True
            for error in errors[:30]:
                print(f"  ERROR: {error}")
            if len(errors) > 30:
                print(f"  ERROR: ... {len(errors) - 30} more")
        else:
            print("  OK")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
