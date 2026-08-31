#!/usr/bin/env python3
"""Prepare the existing 250 anime/fandom entries as an editorial book draft."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "themed_anime.jsonl"

CHAPTERS = [
    "Favorites, Fandom, and Adaptations", "Episodes, Songs, and Analysis",
    "Fan Works and Merchandise", "Watching and Discussing a Series",
    "Characters, Popularity, and Film Editions", "Casual Reactions and Character Types",
    "Power, Fantasy, and Battle Tropes", "Romance, Emotion, and Suspense",
    "Publishing and Serialization", "Creators, Editions, and New Series",
    "School and Romance Setups", "Social Types and Fandom Identities",
    "Streaming, Creators, and Online Video", "Online Communities and Conflict",
    "Collector Editions and Fan Events", "Bosses, Levels, and Gacha",
    "Updates, Progression, and Game Endings", "Challenges and Competitive Play",
    "Teams, Builds, and Game Genres", "Story Routes and Emotional Endings",
    "Slang, Comedy, and Slice of Life", "Manga Demographics and Classic Tropes",
    "Genre, Mystery, and Plot Twists", "Sequels, Retellings, and Crossovers",
    "Events, Fan Art, and Favorite Characters",
]

RUDE_IDS = {53, 54, 57, 198, 203}
CASUAL_IDS = {51, 52, 55, 56, 64, 73, 74, 75, 77, 79, 80, 81, 111, 200, 205, 210}
DIALOGUE_IDS = RUDE_IDS | CASUAL_IDS | {199, 247}
PRODUCTION_RANGES = ((6, 20), (31, 40), (85, 100), (124, 130), (145, 151), (232, 240))
STORY_RANGES = ((41, 45), (61, 84), (101, 114), (152, 231))


def in_ranges(value, ranges):
    return any(start <= value <= end for start, end in ranges)


def main():
    rows = [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != 250:
        raise SystemExit(f"Expected 250 rows, found {len(rows)}")
    for row in rows:
        number = int(row["id"])
        chapter = (number - 1) // 10 + 1
        if number in DIALOGUE_IDS:
            section = "dialogue"
        elif in_ranges(number, PRODUCTION_RANGES):
            section = "production"
        elif in_ranges(number, STORY_RANGES):
            section = "story"
        else:
            section = "fandom"
        if number in RUDE_IDS:
            safety = "Rude"
        elif number in CASUAL_IDS:
            safety = "Casual"
        elif section == "fandom":
            safety = "Fandom"
        else:
            safety = "Recognition only"
        if safety == "Rude":
            real_life = "Understand it, but avoid directing it at people unless you know the relationship and force of the expression."
        elif safety == "Casual":
            real_life = "Common in casual speech; avoid treating it as a neutral expression for formal situations."
        elif safety == "Fandom":
            real_life = "Use it when discussing media or fan activity; it may not carry the same meaning outside fandom."
        else:
            real_life = "Useful primarily for recognizing and discussing stories, production, or game conventions."
        additions = {
            "category": f"anime-chapter-{chapter:02d}",
            "chapter": chapter,
            "chapter_title": CHAPTERS[chapter - 1],
            "section": section,
            "safety_label": safety,
            "register": safety.lower(),
            "speaker_image": "Depends on genre and context; verify during editorial review.",
            "real_life_use": real_life,
            "usage_note_en": f"Draft usage note for {row['en']}. Confirm current nuance and range before publication.",
            "contrast": [],
            "example_ja_2": "",
            "example_en_2": "",
            "misuse_note_en": real_life,
            "review_status": "pending",
        }
        for key, value in additions.items():
            row.setdefault(key, value)
    SOURCE.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    print(f"prepared {len(rows)} anime/manga draft rows")


if __name__ == "__main__":
    main()
