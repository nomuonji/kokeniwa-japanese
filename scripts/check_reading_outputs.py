#!/usr/bin/env python3
"""Validate the Japanese interpretation source and generated EPUB."""
import html
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "reading_problems.jsonl"
EPUB = Path(r"D:\youph\Kindle\日本語解釈トレーニング200問\Japanese_Reading_Training_200.epub")
REQUIRED = {
    "id", "category", "point", "difficulty", "format", "sentence_ja",
    "question_en", "choices", "answer_index", "translation_en",
    "explanation_en", "status", "used_at",
}
BANNED = (
    "___", "In this complete sentence", "The key wording is",
    "use its full context rather than", "(誤りを選ぶ)",
    "(相手も知っている情報について)", "安けれ安ければ", "とか/とか",
)


def fail(message):
    raise SystemExit(f"ERROR: {message}")


def main():
    rows = [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != 200:
        fail(f"expected 200 rows, found {len(rows)}")
    if [row["id"] for row in rows] != list(range(1, 201)):
        fail("ids must be consecutive from 1 to 200")

    for row in rows:
        missing = REQUIRED - row.keys()
        if missing:
            fail(f"No.{row.get('id')} missing fields: {sorted(missing)}")
        if row["difficulty"] not in (1, 2, 3):
            fail(f"No.{row['id']} invalid difficulty")
        if row["status"] != "published":
            fail(f"No.{row['id']} is not published")
        joined = " ".join((row["sentence_ja"], row["translation_en"], row["explanation_en"]))
        for marker in BANNED:
            if marker in joined:
                fail(f"No.{row['id']} contains banned artifact: {marker}")
        if not re.search(r"[ぁ-んァ-ヶ一-龯]", row["sentence_ja"]):
            fail(f"No.{row['id']} has no Japanese text")
        if len(row["translation_en"].split()) < 3 or len(row["explanation_en"].split()) < 8:
            fail(f"No.{row['id']} answer or explanation is too short")
        if row["format"] == "translation":
            if row["choices"] or row["answer_index"] is not None:
                fail(f"No.{row['id']} translation task has quiz data")
        elif row["format"] == "quiz":
            if len(row["choices"]) != 4 or row["answer_index"] not in range(4):
                fail(f"No.{row['id']} invalid quiz data")
        else:
            fail(f"No.{row['id']} invalid format")

    for field in ("sentence_ja", "translation_en", "explanation_en"):
        values = [row[field] for row in rows]
        if len(values) != len(set(values)):
            fail(f"duplicate {field}")

    quizzes = [row for row in rows if row["format"] == "quiz"]
    answers = Counter(row["answer_index"] for row in quizzes)
    if max(answers.values()) - min(answers.values()) > 1:
        fail(f"unbalanced quiz answers: {dict(answers)}")

    if not EPUB.is_file():
        fail(f"missing EPUB: {EPUB}")
    with zipfile.ZipFile(EPUB) as book:
        bad = book.testzip()
        if bad:
            fail(f"EPUB CRC failure: {bad}")
        xhtml = "\n".join(
            book.read(name).decode("utf-8")
            for name in book.namelist()
            if name.endswith((".xhtml", ".html"))
        )
    for row in rows:
        for field in ("sentence_ja", "translation_en", "explanation_en"):
            if html.escape(str(row[field]), quote=False) not in xhtml:
                fail(f"EPUB is out of sync at No.{row['id']} field {field}")

    print(f"OK: {len(rows)} unique problems; {len(quizzes)} quizzes / {len(rows)-len(quizzes)} translation tasks")
    print(f"Quiz answer positions: {dict(sorted(answers.items()))}")
    print(f"EPUB ZIP integrity and source synchronization: OK ({EPUB.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
