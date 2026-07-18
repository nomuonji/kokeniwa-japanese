# 教材データ生成 進捗台帳

計画: `C:\Users\youph\.claude\plans\english-fancy-allen.md` 参照。
バッチ追記は `python scripts/append_batch.py <set_key> <batch.jsonl>`(idなし行を渡す)、
検証は `python scripts/validate_data.py`。

## 目標と現在値

| セット | 目標 | 現在 | 状態 |
|---|---|---|---|
| n5 | 800 | 803 | ✅完了 |
| n4 | 600 | 600 | ✅完了 |
| n3 | 800 | 171 | 未着手 |
| n2 | 900 | 182 | 未着手 |
| n1 | 1000 | 193 | 未着手 |
| themed_travel | 250 | 0 | 未着手 |
| themed_food | 250 | 0 | 未着手 |
| themed_anime | 250 | 0 | 未着手 |
| themed_business | 250 | 0 | 未着手 |
| themed_onomatopoeia | 250 | 0 | 未着手 |
| quiz | 150 | 0 | 未着手 |

## 実施済みチャンク

### n4(600語・完了)
- 既存110語: ビジネス・手続き語彙
- 追加チャンク: 自他動詞ペア/形容詞・副詞/仕事・学校名詞/自然・社会・生活/料理・家・衣・趣味/敬語・コミュニケーション・感情/IT・メディア・数量/医療・身体・用事/社会・家族・人生行事/学習・交通・人
### n5(803語・完了)
- 既存110語: 色・形容詞基本・位置・家族・場所・乗り物・家・物・動詞基本・時間
- 追加チャンク: 数と助数詞/曜日・時間表現/食べ物・飲み物/体・健康・人/動詞(移動・日常)/形容詞(い・な)/自然・天気・場所/日用品・衣類・趣味/副詞・する名詞・学校/方向・施設・家庭用品/指示語・気持ち・挨拶/交通・旅行・買い物/動物・健康・接続詞/色・残り基本語

## 残タスクメモ

- 既存~1,000行の example_ja/example_en バックフィル(N5/N4の既存行は例文あり、要確認)
- Phase 3: テーマ別セット+vocab home 2セクション化+ナビ整理
- Phase 4: クイズテンプレート(English の reading.py 移植)
- Phase 5: カード裏例文(build_json + vocab-grid.js)
- Phase 6: Anki(English の build_anki.py 移植)
- Phase 7: example必須化+ホーム更新
