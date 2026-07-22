# -*- coding: utf-8 -*-
"""Threads 自動投稿のオーケストレーター(kokeniwa-japanese / GitHub Actions から実行)。

処理の流れ(各アカウント):
  1. (前回投稿があり未リプライなら)サイト誘導リプライを前回投稿へぶら下げる
  2. 期限が近ければトークンをリフレッシュ
  3. カーソル位置の語彙(6語)を1件投稿
  4. 次回の誘導用に last_post を保存し、カーソルを進める
状態(トークン・カーソル・last_post)は Gist に保存。

コンテンツ種別(acc["content"]):
  jp_vocab : JLPT語彙を6語ずつ、レベルをローテーション(既定 n3→n2→n1)

環境変数:
  GH_GIST_TOKEN, GIST_ID  : Gist アクセス(gist_state.py が使用)
  PAGES_BASE              : (任意)誘導リンクのドメイン(format_referral.py が使用)
  DRY_RUN=1               : 実投稿せず内容を表示するだけ
  ACCOUNTS="jp"           : (任意)対象アカウントを限定
  REFRESH_BEFORE_DAYS=10  : (任意)期限が何日以内でリフレッシュするか
"""
import datetime as dt
import os
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gist_state
import threads_client as tc
import format_jp_vocab_post as fjp
from format_referral import build_referral

NOW = dt.datetime.now(dt.timezone.utc)
DRY_RUN = os.environ.get("DRY_RUN") == "1"
REFRESH_BEFORE = dt.timedelta(days=int(os.environ.get("REFRESH_BEFORE_DAYS", "10")))


def jp_vocab_pick(acc):
    """jp_vocab アカウント: ローテーションで次レベルの6語チャンクを返す。"""
    rotation = acc.get("rotation") or list(fjp.ROTATION)
    acc["rotation"] = rotation
    rot = int(acc.get("rot_index", 0)) % len(rotation)
    level = rotation[rot]
    words = fjp.load_words(level)
    cursors = acc.setdefault("cursors", {})
    cur = int(cursors.get(level, 0)) % len(words)
    rows = fjp.pick_chunk(words, cur)
    cursors[level] = (cur + fjp.WORDS_PER_POST) % len(words)
    acc["rot_index"] = (rot + 1) % len(rotation)
    text = fjp.build_post(level, rows)
    meta = {"slug": fjp.LEVELS[level]["slug"], "first_id": rows[0]["id"],
            "total": len(words), "words": [f"{r['jp']} ({r['romaji']})" for r in rows]}
    return {"posts": [text], "kind": "jp_vocab", "meta": meta,
            "label": f"jp_vocab:{level} cursor={cur}/{len(words)}"}


def build_current(acc):
    content_key = acc["content"]
    if content_key == "jp_vocab":
        return jp_vocab_pick(acc)
    raise ValueError(f"未知のコンテンツ種別: {content_key}")


def maybe_refresh(name, acc):
    if DRY_RUN:
        return False
    exp = acc.get("expires_at")
    need = True
    if exp:
        try:
            expires = dt.datetime.fromisoformat(exp)
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=dt.timezone.utc)
            need = (expires - NOW) <= REFRESH_BEFORE
        except ValueError:
            need = True
    if not need:
        return False
    try:
        res = tc.refresh_token(acc["token"])
        acc["token"] = res["access_token"]
        secs = int(res.get("expires_in", 60 * 24 * 3600))
        acc["expires_at"] = (NOW + dt.timedelta(seconds=secs)).isoformat()
        print(f"[{name}] トークンをリフレッシュ(新期限 {acc['expires_at']})")
        return True
    except tc.ThreadsError as e:
        print(f"[{name}] リフレッシュskip: {e}")
        return False


def do_referral(name, acc):
    lp = acc.get("last_post")
    if not lp or lp.get("replied"):
        return False
    text = build_referral(lp["kind"], lp["meta"])
    if DRY_RUN:
        print(f"[{name}] (DRY_RUN 誘導リプライ)\n  " + text.replace("\n", "\n  "))
        return False
    try:
        rid = tc.post_text(acc["user_id"], acc["token"], text, reply_to_id=lp["root_id"])
        lp["replied"] = True
        lp["reply_id"] = rid
        print(f"[{name}] 誘導リプライ完了 reply_id={rid}")
    except tc.ThreadsError as e:
        lp["replied"] = True
        print(f"[{name}] 誘導リプライskip: {e}")
    return True


def post_account(name, acc):
    cur = build_current(acc)
    label = f"[{name}] {cur['label']}"
    if DRY_RUN:
        print(f"{label} (DRY_RUN 投稿せず)")
        for i, p in enumerate(cur["posts"]):
            print(f"  --- part {i + 1} ---")
            print("  " + p.replace("\n", "\n  "))
    else:
        ids = tc.post_thread(acc["user_id"], acc["token"], cur["posts"])
        print(f"{label} 投稿完了 media_ids={ids}")
        acc["last_post"] = {
            "kind": cur["kind"], "meta": cur["meta"],
            "root_id": ids[0], "replied": False,
            "posted_at": NOW.isoformat(),
        }


def main():
    state = gist_state.load_state()
    accounts = state.get("accounts", {})
    only = os.environ.get("ACCOUNTS")
    targets = [a.strip() for a in only.split(",")] if only else list(accounts)

    changed = False
    errors = []
    for name in targets:
        acc = accounts.get(name)
        if not acc:
            print(f"[{name}] 状態に存在しないためskip")
            continue
        try:
            if do_referral(name, acc):
                changed = True
            if maybe_refresh(name, acc):
                changed = True
            post_account(name, acc)
            changed = True
        except Exception as e:
            errors.append(name)
            print(f"[{name}] 失敗: {e}")
            traceback.print_exc()

    if changed and not DRY_RUN:
        gist_state.save_state(state)
        print("状態を Gist へ保存しました")
    elif DRY_RUN:
        print("DRY_RUN のため Gist は更新しません")

    if errors:
        print(f"失敗したアカウント: {errors}")
        sys.exit(1)


if __name__ == "__main__":
    main()
