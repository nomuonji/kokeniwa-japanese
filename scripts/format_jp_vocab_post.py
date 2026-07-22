# -*- coding: utf-8 -*-
"""JLPT語彙(data/vocab_{level}.jsonl)を投稿文へ整形する(kokeniwa-japanese 用)。

英語話者向けサイトに合わせ、日本語(読み)= 英語の意味 の形で 6語/投稿。
データ列: id, jp, kana, romaji, en, example_ja, example_en

使い方:
    python scripts/format_jp_vocab_post.py n3            # 先頭6語
    python scripts/format_jp_vocab_post.py n2 --cursor 12
"""
import argparse
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WORDS_PER_POST = 6
THREADS_LIMIT = 500

# level -> サイトの slug / 見出し(vocab_{level}.jsonl を読む)
LEVELS = {
    "n5": {"slug": "n5", "file": "vocab_n5.jsonl", "title": "JLPT N5 Vocabulary"},
    "n4": {"slug": "n4", "file": "vocab_n4.jsonl", "title": "JLPT N4 Vocabulary"},
    "n3": {"slug": "n3", "file": "vocab_n3.jsonl", "title": "JLPT N3 Vocabulary"},
    "n2": {"slug": "n2", "file": "vocab_n2.jsonl", "title": "JLPT N2 Vocabulary"},
    "n1": {"slug": "n1", "file": "vocab_n1.jsonl", "title": "JLPT N1 Vocabulary"},
}

# 既定のローテーション(english-learner の稼働構成を踏襲: n3 → n2 → n1)
ROTATION = ["n3", "n2", "n1"]


def load_words(level):
    path = DATA_DIR / LEVELS[level]["file"]
    words = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                words.append(json.loads(line))
    return words


def pick_chunk(words, cursor, size=WORDS_PER_POST):
    n = len(words)
    return [words[(cursor + i) % n] for i in range(size)]


def build_post(level, rows):
    cfg = LEVELS[level]
    first, last = rows[0]["id"], rows[-1]["id"]
    head = f"【{cfg['title']} No.{first}-{last}】"
    lines = [head, ""]
    lines += [f"・{r['jp']} ({r['romaji']}) = {r['en']}" for r in rows]
    lines += ["", "#JLPT"]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("level", choices=list(LEVELS))
    ap.add_argument("--cursor", type=int, default=0, help="語インデックス(0始まり)")
    args = ap.parse_args()
    words = load_words(args.level)
    rows = pick_chunk(words, args.cursor % len(words))
    post = build_post(args.level, rows)
    n = len(post)
    warn = "  ⚠ 500超" if n > THREADS_LIMIT else ""
    print(f"----- {args.level} cursor={args.cursor} ({n}/{THREADS_LIMIT}){warn} -----")
    print(post)


if __name__ == "__main__":
    main()
