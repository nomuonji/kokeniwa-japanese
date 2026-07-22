# -*- coding: utf-8 -*-
"""サイト誘導リプライの本文を組み立てる(kokeniwa-japanese 用)。

構成は「今日の単語おぼえてる？(self-test)」＋「無料の単語帳/学習サイトへ誘導」。
毎回同じ定型文だと bot 判定されやすいので、書き出し(hook)と締め(cta)を複数候補
からランダムに選び、単語の並びと合わせて投稿ごとに文面を変える。英語話者向け。

リンク先は該当カードへのディープリンク /vocab/{slug}/#w{先頭id}。
将来 独自ドメインへ移行する際は PAGES_BASE(または環境変数 PAGES_BASE)のみ変更。
"""
import os
import random

PAGES_BASE = os.environ.get("PAGES_BASE", "https://kokeniwa-japanese.pages.dev").rstrip("/")

# {n}=語数, {total}=総語数, {url}=一覧ページ
HOOKS = [
    "Still remember today's words? 🤔",
    "Quick check — can you recall these {n}?",
    "Review time! Do the meanings come to mind? ✍️",
    "Test yourself 👀 Got them all?",
    "One more look before you go 👇",
]
CTAS = [
    "Check the meanings & all {total} words here 👇\n{url}",
    "See the answers in the free flashcard set 👇\n{url}",
    "Review all {total} words for free 👇\n{url}",
    "Keep going with the free flashcards 👇\n{url}",
]


def build_referral(kind, meta):
    """meta(jp_vocab): {"slug","first_id","total","words":[...]}"""
    if kind == "jp_vocab":
        url = f"{PAGES_BASE}/vocab/{meta['slug']}/#w{meta['first_id']}"
        hook = random.choice(HOOKS).format(n=len(meta["words"]), total=meta["total"])
        cta = random.choice(CTAS).format(total=meta["total"], url=url)
        body = "\n".join(meta["words"])
        return f"{hook}\n\n{body}\n\n{cta}"
    raise ValueError(f"未知の誘導種別: {kind}")
