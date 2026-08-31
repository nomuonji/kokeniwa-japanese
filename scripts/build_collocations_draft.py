#!/usr/bin/env python3
"""Mine a balanced 500-row collocation draft from existing reviewed site examples.

The output is deliberately pending editorial review. Evidence points back to the
existing source row so reviewers can audit every candidate without guessing its origin.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUTPUT = DATA / "themed_collocations.jsonl"

CHAPTERS = [
    ("daily-life", "Daily Life", "morning night time day everyday weather clothes book phone use open close wake sleep"),
    ("home-housework", "Home and Housework", "home house room kitchen bath laundry clean wash window door bed trash cook"),
    ("food-shopping", "Food and Shopping", "food eat drink meal rice bread restaurant shop buy sell price money order taste"),
    ("relationships", "Relationships", "friend family person meet promise help invite marry love talk together gift"),
    ("feelings-thoughts", "Feelings and Thoughts", "feel think mind worry interest hope idea understand remember forget decide"),
    ("learning-language", "Learning and Language", "study school class language Japanese read write listen question answer practice learn"),
    ("work-contact", "Work and Communication", "work company office meeting email contact report call plan task business customer"),
    ("travel-movement", "Travel and Movement", "travel train bus station airport road hotel arrive leave ride walk cross return"),
    ("health-body", "Health and the Body", "health body hospital doctor medicine sick pain cold exercise rest sleep eye hand"),
    ("society-schedule", "Society and Plans", "society event schedule appointment rule news community public government future date"),
]

SOURCES = [
    "vocab_n5.jsonl", "vocab_n4.jsonl", "vocab_n3.jsonl", "vocab_n2.jsonl", "vocab_n1.jsonl",
    "phrases.jsonl", "themed_travel.jsonl", "themed_food.jsonl", "themed_business.jsonl",
]
PARTICLE_RE = re.compile(r"[をにがでとへ]")
BAD = re.compile(r"[？?！!「」『』…]|(です|ます|でした|ました|ません|ましょう)$")


def level_for(filename):
    match = re.search(r"vocab_(n[1-5])", filename)
    return match.group(1).upper() if match else "N4-N2"


def category_scores(text):
    lowered = text.lower()
    scores = []
    for _, _, keywords in CHAPTERS:
        scores.append(sum(1 for keyword in keywords.split() if keyword in lowered))
    return scores


def main():
    candidates = []
    seen = set()
    for filename in SOURCES:
        path = DATA / filename
        for source_id, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            row = json.loads(line)
            sentence = row.get("example_ja", "").strip()
            english = row.get("example_en", "").strip()
            phrase = sentence.rstrip("。")
            if not sentence or not english or not (4 <= len(phrase) <= 22):
                continue
            if BAD.search(phrase) or not PARTICLE_RE.search(phrase) or phrase in seen:
                continue
            if any(mark in phrase for mark in ("私は", "あなたは", "彼は", "彼女は", "これは", "それは")):
                continue
            seen.add(phrase)
            context = " ".join((row.get("jp", ""), row.get("en", ""), phrase, english))
            scores = category_scores(context)
            category = max(range(10), key=lambda index: scores[index]) if max(scores) else None
            candidates.append({
                "source": filename, "source_id": source_id, "source_row": row,
                "phrase": phrase, "sentence": sentence, "english": english,
                "category": category, "score": max(scores), "level": level_for(filename),
            })

    buckets = defaultdict(list)
    reserve = []
    for candidate in candidates:
        if candidate["category"] is None:
            reserve.append(candidate)
        else:
            buckets[candidate["category"]].append(candidate)
    for values in buckets.values():
        values.sort(key=lambda item: (-item["score"], len(item["phrase"]), item["source_id"]))
    reserve.sort(key=lambda item: (len(item["phrase"]), item["source"], item["source_id"]))

    selected, used = [], set()
    for chapter in range(10):
        choices = [item for item in buckets[chapter] if item["phrase"] not in used][:50]
        while len(choices) < 50:
            item = next(item for item in reserve if item["phrase"] not in used and item not in choices)
            choices.append(item)
        for item in choices:
            used.add(item["phrase"])
            selected.append((chapter, item))

    rows = []
    for number, (chapter, item) in enumerate(selected, 1):
        source = item["source_row"]
        slug, title, _ = CHAPTERS[chapter]
        particle = PARTICLE_RE.search(item["phrase"]).group(0)
        rows.append({
            "id": number,
            "headword": source.get("jp", item["phrase"]),
            "jp": item["phrase"],
            "kana": source.get("kana", ""),
            "romaji": source.get("romaji", ""),
            "collocation": item["phrase"],
            "particle": particle,
            "meaning_en": item["english"],
            "en": item["english"],
            "pos": "collocation",
            "category": slug,
            "chapter": chapter + 1,
            "chapter_title": title,
            "level": item["level"],
            "register": "neutral",
            "example_ja": item["sentence"],
            "example_en": item["english"],
            "usage_note_en": "Draft candidate mined from an existing Kokeniwa example. Confirm the particle and natural range during editorial review.",
            "literal_trap_en": "Do not replace the Japanese predicate or particle mechanically from English.",
            "wrong_example": "",
            "correct_example": item["phrase"],
            "contrast": [],
            "example_ja_2": "",
            "example_en_2": "",
            "misuse_note_en": "Confirm whether this is a fixed or strongly preferred pairing rather than a freely generated phrase.",
            "evidence": [f"data/{item['source']}:{item['source_id']}"],
            "review_status": "pending",
        })
    OUTPUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    print(f"wrote {len(rows)} collocation candidates -> {OUTPUT}")
    for index, (_, title, _) in enumerate(CHAPTERS, 1):
        print(f"  {index}. {title}: {sum(1 for row in rows if row['chapter'] == index)}")


if __name__ == "__main__":
    main()
