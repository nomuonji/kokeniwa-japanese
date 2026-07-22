# -*- coding: utf-8 -*-
"""日本語(JLPT)アカウントを Gist 状態へ一度だけ登録する(準備用)。

方針(ユーザー確認済み):
  - JP データは再構築され id/並びが旧 english-learner と一致しないため、
    進捗は引き継がず cursor=0(最初から)で開始する。
  - ローテーションは n3 → n2 → n1(現状踏襲)。

認証情報は english-learner/.env の THREADS_USER_ID_JP / THREADS_ACCESS_TOKEN_JP を使う。

前提: JP 専用の Gist を作成し、GH_GIST_TOKEN / GIST_ID を環境変数(または
kokeniwa-japanese/.env)に用意しておくこと。EN 用 Gist とは別にすること。

使い方:
    # 確認(Gist は変更しない)
    python scripts/seed_state.py --english-learner ../english-learner
    # 実行(Gist に書き込む)
    GH_GIST_TOKEN=... GIST_ID=... python scripts/seed_state.py \
        --english-learner ../english-learner --commit
"""
import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gist_state  # noqa: E402
import format_jp_vocab_post as fjp  # noqa: E402

ACCOUNT_NAME = "jp"


def load_dotenv(path):
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--english-learner", default="../english-learner")
    ap.add_argument("--commit", action="store_true", help="実際に Gist へ書き込む")
    args = ap.parse_args()

    load_dotenv(HERE.parent / ".env")  # あれば GH_GIST_TOKEN / GIST_ID を読む

    el = Path(args.english_learner).resolve()
    el_env = {}
    for line in (el / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            el_env[k.strip()] = v.strip()
    user_id = el_env["THREADS_USER_ID_JP"]
    token = el_env["THREADS_ACCESS_TOKEN_JP"]
    expires_at = el_env.get("THREADS_TOKEN_JP_EXPIRES_AT") or \
        (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=50)).isoformat()

    account = {
        "content": "jp_vocab",
        "user_id": user_id,
        "token": token,
        "expires_at": expires_at,
        "rotation": list(fjp.ROTATION),  # n3, n2, n1
        "rot_index": 0,
        "cursors": {lv: 0 for lv in fjp.ROTATION},  # 最初から
    }

    print(f"=== {ACCOUNT_NAME} アカウント(投入内容) ===")
    print(json.dumps(dict(account, token=token[:8] + "…(masked)"), ensure_ascii=False, indent=2))

    if not args.commit:
        print("\n(--commit 未指定のため Gist は変更しません)")
        return

    state = gist_state.load_state() if _gist_has_state() else {"accounts": {}}
    accounts = state.setdefault("accounts", {})
    accounts[ACCOUNT_NAME] = account
    gist_state.save_state(state)
    print(f"\nGist に {ACCOUNT_NAME} を登録しました。")


def _gist_has_state():
    """空の Gist(まだ threads_state.json が無い)場合に load を避ける。"""
    try:
        gist_state.load_state()
        return True
    except Exception:
        return False


if __name__ == "__main__":
    main()
