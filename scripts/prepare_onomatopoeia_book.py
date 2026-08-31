#!/usr/bin/env python3
"""Add non-destructive book fields to the public onomatopoeia source.

This establishes one canonical source for the site, EPUB, and bonus CSV. It does
not claim that editorial review has happened: every newly prepared row remains
``pending`` until a human-quality language pass approves it.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "themed_onomatopoeia.jsonl"

CHAPTERS = [
    ("anticipation-and-emotion", "Anticipation and Emotion"),
    ("weather-and-temperature", "Unsettled Feelings, Weather, and Temperature"),
    ("wind-light-and-surfaces", "Wind, Light, and Surfaces"),
    ("texture-and-eating", "Texture and Eating"),
    ("food-and-cooking", "Food and Cooking"),
    ("faces-laughter-and-fatigue", "Faces, Laughter, and Fatigue"),
    ("sleep-looking-and-wandering", "Sleep, Looking, and Wandering"),
    ("ways-of-moving", "Ways of Moving"),
    ("impact-sounds-and-pain", "Impact Sounds and Pain"),
    ("body-reactions-and-startle", "Body Reactions and Startle"),
    ("relief-disappointment-and-surprise", "Relief, Disappointment, and Surprise"),
    ("strong-feelings-and-sudden-action", "Strong Feelings and Sudden Action"),
    ("progress-delay-and-confusion", "Progress, Delay, and Confusion"),
    ("social-behavior-and-chatter", "Social Behavior and Chatter"),
    ("silence-secrecy-and-anger", "Silence, Secrecy, and Anger"),
    ("agreement-appetite-and-vitality", "Agreement, Appetite, and Vitality"),
    ("posture-appearance-and-escape", "Posture, Appearance, and Escape"),
    ("hopping-rolling-and-swaying", "Hopping, Rolling, and Swaying"),
    ("shaking-breaking-and-scattering", "Shaking, Breaking, and Scattering"),
    ("mess-sound-and-flow", "Mess, Sound, and Flow"),
    ("liquids-bubbles-and-clatter", "Liquids, Bubbles, and Clatter"),
    ("shape-surface-and-sudden-motion", "Shape, Surface, and Sudden Motion"),
    ("clarity-change-and-body-shape", "Clarity, Change, and Body Shape"),
    ("build-cutting-and-bluntness", "Build, Cutting, and Bluntness"),
    ("complaints-commotion-and-pain", "Complaints, Commotion, and Pain"),
]

SOUND_MARKERS = (
    "sound", "rattl", "thud", "bang", "crash", "sizzling", "crackl",
    "clapping", "snoring", "knocking", "coughing", "clinking", "clatter",
    "pouring rain", "wind blowing", "rumbling", "tearing",
)


def main():
    rows = [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != 250:
        raise SystemExit(f"Expected 250 rows, found {len(rows)}")
    for row in rows:
        index = (int(row["id"]) - 1) // 10
        slug, title = CHAPTERS[index]
        meaning = row["en"].strip().rstrip(".")
        subtype = "giongo" if any(marker in meaning.lower() for marker in SOUND_MARKERS) else "gitaigo"
        additions = {
            "category": slug,
            "chapter": index + 1,
            "chapter_title": title,
            "subtype": subtype,
            "register": "neutral",
            "usage_note_en": f"Expresses {meaning}. Check the example for the kind of subject and situation it naturally describes.",
            "contrast": [],
            "example_ja_2": "",
            "example_en_2": "",
            "misuse_note_en": "Do not rely on the English gloss alone; the natural subject and construction vary by mimetic word.",
            "review_status": "pending",
        }
        for key, value in additions.items():
            row.setdefault(key, value)
    SOURCE.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    print(f"prepared {len(rows)} rows in {SOURCE}")


if __name__ == "__main__":
    main()
