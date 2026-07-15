# Kotsukotsu Japanese

英語話者向けの日本語（JLPT）語彙学習サイト。`../English`（English Hub）の姉妹プロジェクトで、
同じ静的サイト生成の仕組みとフラッシュカード一覧UIを流用している。UIは英語。

- JLPT N5〜N1 の語彙 ＋ サバイバルフレーズをフラッシュカードで学習
- 各カードは 表(日本語)⇄裏(英語の意味＋かな・ローマ字) を個別に反転
- 静的生成（Python標準ライブラリのみ）→ `dist/` を Cloudflare Pages が配信

ビルドと公開の手順は [docs/セットアップ_サイト公開.md](docs/セットアップ_サイト公開.md) を参照。

```
python site/build_site.py          # dist/ を生成
python -m http.server 8790 --directory dist   # ローカル確認
```

元データは旧 `english-learner/japanese/` から移行（`data/*.jsonl`）。english-learner 自体は変更していない。
