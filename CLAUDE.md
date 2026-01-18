# CLAUDE.md - Claude Code 設定

## プロジェクト情報

- **プロジェクト名**: voicevox-intonation-dict
- **言語**: Python 3.12+
- **フレームワーク**: FastAPI
- **パッケージ管理**: pip (requirements.txt)

---

## 実行コマンド

```bash
# サーバー起動（Docker）
docker compose up -d

# ログ確認
docker compose logs -f extension-server

# テスト実行
cd server && python -m pytest tests/ -v

# 型チェック
cd server && python -m mypy app/

# APIドキュメント確認
# http://127.0.0.1:8000/docs
```

---

## コーディング規約

### Python
- **型ヒント必須**: すべての関数に型アノテーション
- **docstring**: Google スタイル
- **非同期**: FastAPI ルーターは `async def` を使用
- **命名規則**:
  - 関数・変数: `snake_case`
  - クラス: `PascalCase`
  - 定数: `UPPER_SNAKE_CASE`

### API 設計
- RESTful 原則に従う
- レスポンスは Pydantic モデルで定義
- エラーは HTTPException で適切なステータスコードと共に返す

---

## 重要なデータ構造

### AudioQuery（VOICEVOX）
```python
{
  "accent_phrases": [
    {
      "moras": [
        {
          "text": "ズ",
          "consonant": "z",
          "consonant_length": 0.05,  # 上書き対象
          "vowel": "u",
          "vowel_length": 0.12,      # 上書き対象
          "pitch": 5.62              # 上書き対象
        }
      ],
      "accent": 3
    }
  ]
}
```

### ExtendedDictEntry（拡張辞書）
```python
{
  "word": "ずんだもん",
  "pronunciation": "ズンダモン",
  "accent_type": 3,
  "pitch_values": [5.2, 5.8, 5.5, 5.3, 4.8],
  "length_values": [0.12, 0.08, 0.15, 0.10, 0.12]
}
```

---

## 注意事項

- VOICEVOX Engine は Docker で起動（port 50021）
- 拡張サーバーは port 8000
- 既存の VOICEVOX Engine は改変しない（外部ミドルウェア方式）
- テストデータには「ずんだもん」を使用
