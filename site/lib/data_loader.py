"""Load JSONL under data/ and validate the required fields."""
import json

from . import config

# One word/phrase row must contain these.
VOCAB_REQUIRED_FIELDS = ["id", "jp", "kana", "romaji", "en"]


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
