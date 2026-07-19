"""Site settings and constants. Loads site_config.json and holds the vocab-set table."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"
CONTENT_DIR = ROOT / "content"
SITE_DIR = ROOT / "site"
DIST_DIR = ROOT / "dist"


def load_config():
    with open(ROOT / "site_config.json", encoding="utf-8") as f:
        return json.load(f)


# Vocabulary sets. key = internal id. `file` under data/. Order = display order.
# `mature` sets are noindex and excluded from the main navigation.
VOCAB_SETS = {
    "n5": {
        "slug": "n5", "file": "vocab_n5.jsonl", "level": "N5",
        "title": "JLPT N5 Vocabulary", "short": "N5", "icon": "🌱",
        "description": "The most common Japanese words for absolute beginners. Everyday nouns, verbs and adjectives you meet first.",
    },
    "n4": {
        "slug": "n4", "file": "vocab_n4.jsonl", "level": "N4",
        "title": "JLPT N4 Vocabulary", "short": "N4", "icon": "🌿",
        "description": "Elementary Japanese vocabulary. Build on N5 with words for daily conversations and simple texts.",
    },
    "n3": {
        "slug": "n3", "file": "vocab_n3.jsonl", "level": "N3",
        "title": "JLPT N3 Vocabulary", "short": "N3", "icon": "🍃",
        "description": "Intermediate Japanese vocabulary bridging everyday and more abstract topics.",
    },
    "n2": {
        "slug": "n2", "file": "vocab_n2.jsonl", "level": "N2",
        "title": "JLPT N2 Vocabulary", "short": "N2", "icon": "🌳",
        "description": "Upper-intermediate vocabulary for news, work and academic Japanese.",
    },
    "n1": {
        "slug": "n1", "file": "vocab_n1.jsonl", "level": "N1",
        "title": "JLPT N1 Vocabulary", "short": "N1", "icon": "🎌",
        "description": "Advanced Japanese vocabulary — nuanced, formal and literary words for the highest JLPT level.",
    },
    "phrases": {
        "slug": "phrases", "file": "phrases.jsonl", "level": None,
        "title": "Survival Phrases", "short": "Phrases", "icon": "💬",
        "description": "Practical set phrases for travel and daily life in Japan — greetings, requests and essentials.",
    },
    # --- themed sets: 一時オフ（themed_*.jsonl データ未作成のため）。データが揃ったら復活する。 ---
    # "travel": {
    #     "slug": "travel", "file": "themed_travel.jsonl", "level": None, "group": "themed",
    #     "title": "Travel Japanese", "short": "Travel", "icon": "🧳",
    #     "description": "Practical words for getting around Japan — stations, hotels, restaurants, shopping and emergencies.",
    # },
    # "food": {
    #     "slug": "food", "file": "themed_food.jsonl", "level": None, "group": "themed",
    #     "title": "Food & Cooking Japanese", "short": "Food", "icon": "🍜",
    #     "description": "Dishes, ingredients, flavors and restaurant Japanese — everything you need to eat well in Japan.",
    # },
    # "anime": {
    #     "slug": "anime", "file": "themed_anime.jsonl", "level": None, "group": "themed",
    #     "title": "Anime & Casual Japanese", "short": "Anime", "icon": "🎌",
    #     "description": "Casual speech, slang and expressions you actually hear in anime, dramas and daily conversation.",
    # },
    # "business": {
    #     "slug": "business", "file": "themed_business.jsonl", "level": None, "group": "themed",
    #     "title": "Business Japanese", "short": "Business", "icon": "💼",
    #     "description": "Keigo, office vocabulary and email phrases for working with Japanese companies.",
    # },
    # "onomatopoeia": {
    #     "slug": "onomatopoeia", "file": "themed_onomatopoeia.jsonl", "level": None, "group": "themed",
    #     "title": "Japanese Onomatopoeia", "short": "Onomatopoeia", "icon": "💥",
    #     "description": "Giongo and gitaigo — the sound and mimetic words that make Japanese vivid and natural.",
    # },
    "adult": {
        "slug": "adult", "file": "adult.jsonl", "level": None,
        "title": "Mature Vocabulary (18+)", "short": "18+", "icon": "🔞",
        "description": "Adult-oriented Japanese vocabulary for advanced learners. Not linked from the main site.",
        "mature": True,
    },
}

# Sets shown in nav / on the home page (mature excluded).
PUBLIC_SETS = [k for k, v in VOCAB_SETS.items() if not v.get("mature")]
LEVEL_SETS = [k for k, v in VOCAB_SETS.items() if v.get("level")]
THEMED_SETS = [k for k, v in VOCAB_SETS.items() if v.get("group") == "themed"]

# Closed vocabulary for the optional `pos` field on vocab rows.
POS_VALUES = [
    "noun", "verb", "i-adj", "na-adj", "adverb", "particle",
    "expression", "counter", "onomatopoeia", "other",
]

# Grammar-quiz categories: slug -> display name. Order = display order.
QUIZ_CATEGORIES = {
    "particles": "Particles",
    "verb-forms": "Verb Forms",
    "te-form": "Te-form Usage",
    "conditionals": "Conditionals",
    "passive-causative": "Passive & Causative",
    "keigo": "Keigo & Politeness",
    "giving-receiving": "Giving & Receiving",
    "counters": "Counters",
    "word-choice": "Word Choice",
    "comparisons": "Comparisons",
    "conjunctions": "Conjunctions",
    "reading-comprehension": "Reading Comprehension",
}

# JLPT levels for quiz pages: key -> label/description. Order = display order.
QUIZ_LEVELS = {
    "n5": {"label": "N5", "description": "Beginner — basic particles, verb forms and everyday sentences."},
    "n4": {"label": "N4", "description": "Elementary — te-form, plain form and simple compound sentences."},
    "n3": {"label": "N3", "description": "Intermediate — conditionals, giving/receiving and natural word choice."},
    "n2": {"label": "N2", "description": "Upper-intermediate — nuanced grammar for news and workplace Japanese."},
    "n1": {"label": "N1", "description": "Advanced — formal, literary and subtle grammar distinctions."},
}
