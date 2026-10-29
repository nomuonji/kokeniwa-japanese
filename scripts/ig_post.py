# -*- coding: utf-8 -*-
"""Threads 投稿と同じ中身を、Instagram へカルーセル画像で投稿する(kokeniwa-japanese / auto_post.py から呼ぶ)。

Gist の状態で、Threads アカウントごとに対応する Instagram を持たせる:

    accounts.<name>.instagram = {
        "user_id": "...", "username": "...", "token": "...", "expires_at": "...",
        "enabled": true,
        "last_media_id": "...", "last_permalink": "...", "last_posted_at": "...",
        "last_error": null
    }

instagram が無い/enabled=false のアカウントは何もしない(既存の Threads 投稿に影響なし)。
連携は scripts/ig_link.py(ワークフロー「Instagram 連携」)で行う。
"""
import datetime as dt
import re
from pathlib import Path

import ig_cards
import ig_media_host
import instagram_client as ic

OUT_DIR = Path(__file__).resolve().parent.parent / "out" / "ig"

HASHTAGS = ("#learnjapanese #japanesevocabulary #JLPT #JLPT{lvl} #nihongo "
            "#japaneselanguage #studyjapanese #日本語")


def enabled(acc):
    ig = acc.get("instagram") or {}
    return bool(ig.get("enabled") and ig.get("token") and ig.get("user_id"))


def build_caption(acc, cur):
    """Threads の本文から Instagram 用キャプションを作る(英語話者向け)。"""
    total = cur["meta"]["total"]
    handle = acc.get("username")
    body = re.sub(r"\n+#\S+\s*$", "", cur["posts"][0].rstrip())  # Threads 用の単独タグを外す
    lines = [body, "",
             "👉 Swipe for readings and example sentences.",
             f"Free flashcards for all {total} words — link in bio."]
    if handle:
        lines += ["", f"Daily on Threads: @{handle}"]
    lines += ["", HASHTAGS.format(lvl=cur["level"].upper())]
    return "\n".join(lines)[:2200]


def render(name, acc, cur):
    slides = ig_cards.slides_for(acc, cur)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M")
    return ig_cards.save(slides, OUT_DIR / name, f"{name}-{stamp}")


def maybe_refresh(ig, now, before):
    exp = ig.get("expires_at")
    need = True
    if exp:
        try:
            expires = dt.datetime.fromisoformat(exp)
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=dt.timezone.utc)
            need = (expires - now) <= before
        except ValueError:
            need = True
    if not need:
        return False
    try:
        res = ic.refresh_token(ig["token"])
    except ic.InstagramError as e:
        print(f"  [instagram] リフレッシュskip: {e}")
        return False
    ig["token"] = res["access_token"]
    ig["expires_at"] = (now + dt.timedelta(seconds=int(res.get("expires_in", 60 * 86400)))).isoformat()
    print(f"  [instagram] トークンをリフレッシュ(新期限 {ig['expires_at']})")
    return True


def post(name, acc, cur, now, refresh_before, dry_run=False):
    """1アカウント分を Instagram へ投稿する。投稿しなかった場合は None。"""
    if not enabled(acc):
        if dry_run:  # 連携前でも見た目を確認できるように画像だけは作る
            paths = render(name, acc, cur)
            print(f"[{name}] (DRY_RUN Instagram未連携) 画像 {len(paths)} 枚 → {paths[0].parent}")
        return None
    ig = acc["instagram"]
    paths = render(name, acc, cur)
    caption = build_caption(acc, cur)
    if dry_run:
        print(f"[{name}] (DRY_RUN Instagram) 画像 {len(paths)} 枚 → {paths[0].parent}")
        print("  " + caption.replace("\n", "\n  "))
        return None
    maybe_refresh(ig, now, refresh_before)
    urls = ig_media_host.upload(paths, f"{name}/{paths[0].stem.rsplit('-', 1)[0]}")
    media_id = ic.publish_carousel(ig["user_id"], ig["token"], urls, caption)
    ig["last_media_id"] = media_id
    ig["last_permalink"] = ic.get_permalink(media_id, ig["token"])
    ig["last_posted_at"] = now.isoformat()
    ig["last_error"] = None
    print(f"[{name}] Instagram 投稿完了 media_id={media_id} {ig['last_permalink'] or ''}")
    return media_id
