"""Validate all JSONL data files under data/.

Run: python scripts/validate_data.py
Exit code 1 on any error. Warnings do not fail the run.
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "site"))

from lib import config  # noqa: E402
from lib.data_loader import VOCAB_REQUIRED_FIELDS, QUIZ_REQUIRED_FIELDS  # noqa: E402

errors = []
warnings = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def read_jsonl(path):
    """Parse a JSONL file. Returns list of (lineno, obj). Checks UTF-8 without BOM."""
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        err(f"{path.name}: has a UTF-8 BOM (must be plain UTF-8)")
        raw = raw[3:]
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        err(f"{path.name}: is UTF-16 (must be UTF-8)")
        return []
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        err(f"{path.name}: not valid UTF-8: {e}")
        return []
    rows = []
    for lineno, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append((lineno, json.loads(line)))
        except json.JSONDecodeError as e:
            err(f"{path.name}:{lineno} bad JSON: {e}")
    return rows


def check_vocab_file(path):
    """Validate one vocab/themed JSONL. Returns (count, set of jp values)."""
    rows = read_jsonl(path)
    ids = set()
    jps = set()
    for lineno, w in rows:
        missing = [k for k in VOCAB_REQUIRED_FIELDS if k not in w]
        if missing:
            err(f"{path.name}:{lineno} missing fields: {missing}")
            continue
        try:
            wid = int(w["id"])
        except (TypeError, ValueError):
            err(f"{path.name}:{lineno} id not an int: {w['id']!r}")
            continue
        if wid in ids:
            err(f"{path.name}:{lineno} duplicate id: {wid}")
        ids.add(wid)
        jp = w["jp"]
        if jp in jps:
            err(f"{path.name}:{lineno} duplicate jp: {jp}")
        jps.add(jp)
        for k in ("jp", "kana", "romaji", "en"):
            if not str(w[k]).strip():
                err(f"{path.name}:{lineno} empty field: {k}")
        pos = w.get("pos")
        if pos is not None and pos not in config.POS_VALUES:
            err(f"{path.name}:{lineno} invalid pos: {pos!r}")
        tags = w.get("tags")
        if tags is not None and not (isinstance(tags, list) and all(isinstance(t, str) for t in tags)):
            err(f"{path.name}:{lineno} tags must be a list of strings")
        for k in ("example_ja", "example_en"):
            if k in w and not str(w[k]).strip():
                err(f"{path.name}:{lineno} empty field: {k}")
        ex = w.get("example_ja")
        if ex and w["jp"] not in ex and w["kana"] not in ex:
            # Conjugation means the dictionary form may legitimately be absent.
            stem = w["jp"][:-1] if len(w["jp"]) > 1 else w["jp"]
            if stem not in ex:
                warn(f"{path.name}:{lineno} example_ja may not contain the term: {w['jp']}")
    return len(rows), jps


def check_quiz_file(path):
    rows = read_jsonl(path)
    ids = set()
    n_published = 0
    for lineno, p in rows:
        missing = [k for k in QUIZ_REQUIRED_FIELDS if k not in p]
        if missing:
            err(f"{path.name}:{lineno} missing fields: {missing}")
            continue
        try:
            pid = int(p["id"])
        except (TypeError, ValueError):
            err(f"{path.name}:{lineno} id not an int: {p['id']!r}")
            continue
        if pid in ids:
            err(f"{path.name}:{lineno} duplicate id: {pid}")
        ids.add(pid)
        if p["status"] not in ("draft", "published", "rejected"):
            err(f"{path.name}:{lineno} invalid status: {p['status']!r}")
        if p["status"] == "published":
            n_published += 1
        if p["category"] not in config.QUIZ_CATEGORIES:
            err(f"{path.name}:{lineno} unknown category: {p['category']!r}")
        if p["level"] not in config.QUIZ_LEVELS:
            err(f"{path.name}:{lineno} unknown level: {p['level']!r}")
        choices = p["choices"]
        if not (isinstance(choices, list) and 3 <= len(choices) <= 4):
            err(f"{path.name}:{lineno} choices must be a list of 3-4 strings")
        elif not (isinstance(p["answer_index"], int) and 0 <= p["answer_index"] < len(choices)):
            err(f"{path.name}:{lineno} answer_index out of range")
        elif len(set(choices)) != len(choices):
            err(f"{path.name}:{lineno} duplicate choices")
        for k in ("sentence_ja", "question_en", "translation_en", "explanation_en", "point"):
            if not str(p[k]).strip():
                err(f"{path.name}:{lineno} empty field: {k}")
    return len(rows), n_published


def main():
    counts = []

    # Vocab sets (JLPT + phrases + adult + themed).
    level_jps = {}   # set_key -> jp set, for cross-JLPT dedup
    themed_jps = {}
    for key, vset in config.VOCAB_SETS.items():
        path = config.DATA_DIR / vset["file"]
        if not path.exists():
            warn(f"{vset['file']}: file missing (set '{key}' registered in config)")
            continue
        n, jps = check_vocab_file(path)
        counts.append((vset["file"], n))
        if key in config.LEVEL_SETS:
            level_jps[key] = jps
        elif key in config.THEMED_SETS:
            themed_jps[key] = jps

    # jp must be unique across the JLPT levels (one word, one level).
    seen = {}
    for key, jps in level_jps.items():
        for jp in jps:
            if jp in seen:
                err(f"'{jp}' appears in both {seen[jp]} and {key}")
            else:
                seen[jp] = key

    # Themed <-> JLPT overlap is allowed; themed <-> themed duplicates are warned.
    tseen = {}
    for key, jps in themed_jps.items():
        for jp in jps:
            if jp in tseen:
                warn(f"'{jp}' appears in both themed sets {tseen[jp]} and {key}")
            else:
                tseen[jp] = key

    # Quiz problems.
    quiz_path = config.DATA_DIR / "quiz_problems.jsonl"
    if quiz_path.exists():
        n, n_pub = check_quiz_file(quiz_path)
        counts.append((quiz_path.name, f"{n} ({n_pub} published)"))

    print("Counts:")
    for name, n in counts:
        print(f"  {name}: {n}")
    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings[:40]:
            print(f"  WARN {w}")
        if len(warnings) > 40:
            print(f"  ... and {len(warnings) - 40} more")
    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors[:80]:
            print(f"  ERROR {e}")
        if len(errors) > 80:
            print(f"  ... and {len(errors) - 80} more")
        sys.exit(1)
    print("\nOK")


if __name__ == "__main__":
    main()
