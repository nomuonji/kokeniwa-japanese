# Threads アカウント プロフィール / 固定ポスト 案

対象: THREADS_USER_ID_JP / THREADS_ACCESS_TOKEN_JP のアカウント(english-learner から継続)。
サイトは英語話者向けの JLPT 語彙学習サイト `ja.kokeniwa.net`(Kokeniwa Japanese)。

Threads はプロフィール画像・bio・固定ポストを外部APIから変更する手段が無いため、
以下を本人がアプリ上で手動設定する前提の「文面・画像」だけをここに用意する。

## プロフィール画像

`site/static/profile/icon-1000.png`(1000x1000, 円形クロップ前提)/
`site/static/profile/icon-400.png`(400x400)を使用。
`scripts/build_profile_icon.py` で再生成できる(サイトのOGP画像と同じ「苔玉」の意匠)。

## 表示名(display name)

```
Kokeniwa Japanese 🌱
```

## ユーザーネーム候補

既存のハンドルをそのまま使う(変更不要)。もし変更する場合の候補:

```
kokeniwa_jp / kokeniwajapanese
```

## bio(プロフィール文、Threads は150文字程度が目安)

```
🌱 Learn Japanese, one word a day.
Free JLPT N1–N5 flashcards, quizzes & honest notes on Japanese culture.
👇 All words + quizzes, free
```

（リンクはプロフィールの外部リンク欄に `https://ja.kokeniwa.net` を設定。
Kindle書籍はbioに詰め込まず、固定ポスト③で個別に案内する。）

## 固定ポスト案(3本)

Threadsは投稿を最大3件までピン留めできる。用途の異なる3本を用意
(サイト紹介・使い方ガイド・Kindle書籍紹介)。

### 1. サイト紹介(トップに固定する筆頭候補)

```
Kokeniwa Japanese 🌱

Free JLPT vocabulary flashcards (N5→N1), grammar quizzes & honest essays on
Japanese culture — for English speakers. No sign-up, no paywall.

Start here 👇
https://ja.kokeniwa.net/vocab/
```

### 2. 使い方ガイド(今日から始める人向け)

```
New here? Here's how this account works 👇

3x a day, I post 6 JLPT words (rotating N3→N2→N1).
Each post gets a follow-up quiz reply so you can test yourself before checking the site.

Bookmark this thread and start with N5 basics:
https://ja.kokeniwa.net/vocab/n5/
```

### 3. Kindle書籍紹介(新規)

kokeniwa-english(姉妹サイト、英語学習者向け)で出している「名作で学ぶ英語多読シリーズ」
(シャーロック・ホームズ/自分だけの部屋/共産党宣言、一文ごとの日英対訳)を、
日本語学習者向けにも紹介する固定ポスト。既に知っている名作だからこそ、
日本語の文が推測しやすい――という多読の切り口で訴求する。

```
Already know Sherlock Holmes? Read it in Japanese. 🔍

3 public-domain classics, published sentence-by-sentence in English + Japanese
(Sherlock Holmes / A Room of One's Own / The Communist Manifesto).
You already know the plot — so the Japanese is much easier to guess.

All 3 are free with Kindle Unlimited 👇
https://ja.kokeniwa.net/books/
```

## 運用メモ

- 上記はテキスト案。実際の設定(プロフィール画像アップロード・bio貼付・ポスト作成→固定)は
  Threadsアプリ/Webから手動で行う(APIに profile 更新・pin 設定のエンドポイントが無いため)。
- 固定ポストは通常投稿として1回post_text()すれば良く、`scripts/auto_post.py` の外側で
  一度だけ手動投稿すれば足りる(自動投稿ローテーションには含めない)。
- Kindle書籍(/books/)はAmazonアソシエイトリンクを含むため、固定ポスト③を投稿する際も
  「広告を含む」ことが分かる書き方にしている(Threadsには広告表示の明示義務があるため、
  投稿本文内で購入導線であることが分かるようにする)。
