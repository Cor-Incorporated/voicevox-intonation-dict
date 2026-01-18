# AGENTS.md - VOICEVOX イントネーション辞書拡張プロジェクト

## プロジェクト概要

VOICEVOXの辞書機能を拡張し、イントネーション詳細（ピッチ・長さ）を保存・適用できるツール。

### 解決する課題
- 固有名詞や専門用語のイントネーションを毎回手動で調整する非効率性
- VOICEVOXの辞書機能ではピッチ値・長さ値を保存できない制限

### 技術スタック
- **Backend**: FastAPI (Python 3.12+)
- **Database**: SQLite（開発）/ PostgreSQL（本番想定）
- **Container**: Docker Compose
- **External**: VOICEVOX Engine API (localhost:50021)

---

## ワークフロー（Solo Mode）

```
/plan-with-agent → Plans.md 作成
       ↓
    /work → 実装実行
       ↓
   /review → セルフレビュー
       ↓
   テスト・動作確認
```

---

## ディレクトリ構成

```
voicevox-intonation-dict/
├── server/                    # FastAPI サーバー
│   ├── app/
│   │   ├── main.py           # エントリポイント
│   │   ├── config.py         # 設定
│   │   ├── models/           # Pydantic モデル
│   │   ├── routers/          # API ルーター
│   │   └── services/         # ビジネスロジック
│   ├── tests/                # テスト
│   ├── Dockerfile
│   └── requirements.txt
├── client/                    # フロントエンド（将来）
├── data/                      # データファイル
├── reference/                 # 参照用 VOICEVOX Engine ソース
├── docs/                      # ドキュメント
├── docker-compose.yml
├── Plans.md                   # タスク管理
├── CLAUDE.md                  # Claude Code 設定
└── AGENTS.md                  # 本ファイル
```

---

## API エンドポイント

### 拡張辞書 API (port 8000)
- `GET /api/v1/dictionary/` - 辞書一覧取得
- `POST /api/v1/dictionary/` - 辞書エントリ追加
- `GET /api/v1/dictionary/{id}` - 特定エントリ取得
- `DELETE /api/v1/dictionary/{id}` - エントリ削除

### 拡張合成 API (port 8000) - 未実装
- `POST /api/v1/synthesize` - 拡張辞書適用で音声合成

### VOICEVOX Engine API (port 50021)
- `POST /audio_query` - AudioQuery 生成
- `POST /synthesis` - 音声合成

---

## 開発コマンド

```bash
# 起動
docker compose up -d

# ログ確認
docker compose logs -f extension-server

# 停止
docker compose down

# テスト（ローカル）
cd server && python -m pytest tests/
```

---

## マーカー凡例

| マーカー | 状態 | 説明 |
|---------|------|------|
| `cc:TODO` | 未着手 | Claude Code が実行予定 |
| `cc:WIP` | 作業中 | 実装中 |
| `cc:blocked` | ブロック | 依存タスク待ち |
