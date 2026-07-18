"""Append a batch of generated rows to a data/*.jsonl file, safely.

Usage: python scripts/append_batch.py <set_key|quiz> <batch.jsonl>

- Batch rows must NOT contain "id"; ids are assigned continuing from the
  current max id in the target file.
- Vocab rows duplicated (by jp) against the target file — or, for JLPT sets,
  against ANY JLPT level file — are skipped with a note.
- Always writes UTF-8 without BOM, LF newlines.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "site"))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from lib import config  # noqa: E402
from lib.data_loader import VOCAB_REQUIRED_FIELDS, QUIZ_REQUIRED_FIELDS  # noqa: E402


def read_rows(path):
    rows = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    set_key, batch_path = sys.argv[1], Path(sys.argv[2])

    if set_key == "quiz":
        target = config.DATA_DIR / "quiz_problems.jsonl"
        required = [k for k in QUIZ_REQUIRED_FIELDS if k != "id"]
    else:
        target = config.DATA_DIR / config.VOCAB_SETS[set_key]["file"]
        required = [k for k in VOCAB_REQUIRED_FIELDS if k != "id"]

    existing = read_rows(target) if target.exists() else []
    next_id = max((int(r["id"]) for r in existing), default=0) + 1

    # Dedup universe: target file, plus every JLPT file for level sets.
    seen = {r["jp"] for r in existing} if set_key != "quiz" else set()
    if set_key in config.LEVEL_SETS:
        for k in config.LEVEL_SETS:
            f = config.DATA_DIR / config.VOCAB_SETS[k]["file"]
            if f.exists():
                seen |= {r["jp"] for r in read_rows(f)}

    batch = read_rows(batch_path)
    out, skipped = [], []
    for i, row in enumerate(batch, 1):
        missing = [k for k in required if k not in row]
        if missing:
            sys.exit(f"batch row {i}: missing fields {missing} — nothing appended")
        if "id" in row:
            sys.exit(f"batch row {i}: must not contain 'id' — nothing appended")
        if set_key != "quiz":
            if row["jp"] in seen:
                skipped.append(row["jp"])
                continue
            seen.add(row["jp"])
            pos = row.get("pos")
            if pos is not None and pos not in config.POS_VALUES:
                sys.exit(f"batch row {i}: invalid pos {pos!r} — nothing appended")
        row = {"id": next_id, **row}
        next_id += 1
        out.append(json.dumps(row, ensure_ascii=False))

    with open(target, "a", encoding="utf-8", newline="\n") as f:
        for line in out:
            f.write(line + "\n")

    print(f"{target.name}: appended {len(out)}, skipped {len(skipped)} dup(s), total {len(existing) + len(out)}")
    if skipped:
        print("  skipped: " + ", ".join(skipped))


if __name__ == "__main__":
    main()
