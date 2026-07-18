"""Load JSONL under data/ and validate the required fields."""
import json

from . import config

# One word/phrase row must contain these.
VOCAB_REQUIRED_FIELDS = ["id", "jp", "kana", "romaji", "en"]

# One quiz problem row must contain these.
QUIZ_REQUIRED_FIELDS = [
    "id", "category", "point", "level", "sentence_ja", "question_en",
    "choices", "answer_index", "translation_en", "explanation_en", "status",
]


def load_vocab(set_key):
    """Load a vocabulary set (JSONL) and return it as an id-sorted list."""
    vset = config.VOCAB_SETS[set_key]
    path = config.DATA_DIR / vset["file"]
    words = []
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            w = json.loads(line)
            missing = [k for k in VOCAB_REQUIRED_FIELDS if k not in w]
            if missing:
                raise ValueError(f"{path.name}:{lineno} missing fields: {missing}")
            w["id"] = int(w["id"])
            words.append(w)
    words.sort(key=lambda w: w["id"])
    return words


def load_quiz_problems():
    """Load quiz problems (JSONL) as an id-sorted list. Rejected/draft rows are dropped."""
    path = config.DATA_DIR / "quiz_problems.jsonl"
    if not path.exists():
        return []
    problems = []
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            p = json.loads(line)
            missing = [k for k in QUIZ_REQUIRED_FIELDS if k not in p]
            if missing:
                raise ValueError(f"{path.name}:{lineno} missing fields: {missing}")
            if p["status"] != "published":
                continue
            if p["category"] not in config.QUIZ_CATEGORIES:
                raise ValueError(f"{path.name}:{lineno} unknown category: {p['category']}")
            if p["level"] not in config.QUIZ_LEVELS:
                raise ValueError(f"{path.name}:{lineno} unknown level: {p['level']}")
            if not (0 <= p["answer_index"] < len(p["choices"])):
                raise ValueError(f"{path.name}:{lineno} answer_index out of range")
            p["id"] = int(p["id"])
            problems.append(p)
    problems.sort(key=lambda p: p["id"])
    return problems
