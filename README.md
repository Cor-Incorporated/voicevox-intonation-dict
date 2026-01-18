# VOICEVOX イントネーション辞書拡張プロジェクト

VOICEVOXの辞書機能を拡張し、イントネーション詳細（ピッチ・長さ）を保存できるツールです。

## 概要

- **VOICEVOX Engine**: 既存のDockerイメージ（0.25.1）を使用
- **拡張辞書サービス**: FastAPIベースの独自サービス
- **フロントエンド**: React/Next.js（今後実装予定）

## システム要件

### Docker を使用する場合

- Docker Desktop（起動済み）
- M4 Mac対応（ARM64/AMD64マルチアーキテクチャ）
- curl（動作確認用）

### ローカル開発環境

- Python 3.11 以上
- pip（Python パッケージマネージャー）
- VOICEVOX Engine（ポート 50021 で起動）
- curl（動作確認用）

### VOICEVOX Editor フォーク版と連携する場合

- 上記に加えて以下が必要
- Node.js 24.11.0
- nvm（Node.js バージョン管理ツール）
- npm（Node.js パッケージマネージャー）

## ディレクトリ構造

```
voicevox-intonation-dict/
├── README.md                      # このファイル
├── .env.example                   # 環境変数テンプレート
├── docker-compose.yml             # Docker構成
├── docs/                          # ドキュメント
├── reference/                     # 参照用リポジトリ
│   └── voicevox_engine/           # VOICEVOX Engine v0.25.1
├── server/                        # 拡張辞書サービス
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/                       # FastAPIアプリケーション
│       ├── main.py                # エントリポイント
│       ├── config.py              # 設定
│       ├── models/                # データモデル
│       ├── routers/               # APIエンドポイント
│       └── services/              # ビジネスロジック
├── client/                        # フロントエンド（今後実装）
└── data/                          # 永続化データ
    └── extended_dict.json         # 拡張辞書データ
```

## セットアップ手順

### Docker を使用する場合（推奨）

#### 1. 環境変数の設定（オプション）

```bash
cd voicevox-intonation-dict
cp .env.example .env
# 必要に応じて .env を編集
```

#### 2. Dockerコンテナの起動

```bash
# ビルドと起動
docker compose up -d --build

# ログ確認
docker compose logs -f
```

#### 3. 動作確認

#### VOICEVOX Engine

```bash
# バージョン確認
curl http://127.0.0.1:50021/version

# 話者一覧取得
curl http://127.0.0.1:50021/speakers
```

#### 拡張辞書サービス

```bash
# ヘルスチェック
curl http://127.0.0.1:8000/health

# 辞書全体取得
curl http://127.0.0.1:8000/api/v1/dictionary/

# VOICEVOX Engineバージョン（プロキシ経由）
curl http://127.0.0.1:8000/api/v1/dictionary/voicevox/version
```

#### APIドキュメント

ブラウザで以下にアクセス：

```
http://127.0.0.1:8000/docs
```

## APIエンドポイント

### 拡張辞書API

- `GET /api/v1/dictionary/` - 辞書全体を取得
- `POST /api/v1/dictionary/` - エントリを追加
- `GET /api/v1/dictionary/search?word={word}` - 単語で検索
- `DELETE /api/v1/dictionary/{word}` - エントリを削除

### VOICEVOX Engine プロキシAPI

- `GET /api/v1/dictionary/voicevox/version` - バージョン取得
- `GET /api/v1/dictionary/voicevox/speakers` - 話者一覧取得

## ポート一覧

| サービス | ポート | 用途 |
|---------|-------|------|
| VOICEVOX Engine | 50021 | 音声合成API |
| Extension Server | 8000 | 拡張辞書API |
| Client（今後） | 3000 | フロントエンドUI |

## 環境変数

`.env` ファイルで以下の環境変数を設定できます。`.env.example` をコピーして使用してください。

### VOICEVOX Engine 設定

| 変数名 | デフォルト値 | 説明 |
|-------|------------|------|
| `VOICEVOX_ENGINE_URL` | `http://localhost:50021` | VOICEVOX Engine の接続URL。Docker Compose 使用時は自動的にサービス名で解決されます。 |

### 拡張辞書サーバー設定

| 変数名 | デフォルト値 | 説明 |
|-------|------------|------|
| `EXTENSION_SERVER_PORT` | `8000` | 拡張辞書サーバーのリッスンポート。 |
| `DATA_DIR` | `./data` | 辞書データファイル（`extended_dict.json`）を保存するディレクトリパス。 |

### 開発環境設定

| 変数名 | デフォルト値 | 説明 |
|-------|------------|------|
| `DEBUG` | `true` | デバッグモードの有効化。本番環境では `false` に設定してください。 |

### 設定例

```bash
# 開発環境
VOICEVOX_ENGINE_URL=http://localhost:50021
EXTENSION_SERVER_PORT=8000
DATA_DIR=./data
DEBUG=true

# 本番環境
VOICEVOX_ENGINE_URL=http://voicevox-engine:50021
EXTENSION_SERVER_PORT=8000
DATA_DIR=/var/data/voicevox-dict
DEBUG=false
```

### 注意事項

- Docker Compose を使用する場合、`VOICEVOX_ENGINE_URL` は `http://voicevox-engine:50021` に自動設定されます（サービス名による名前解決）。
- ローカル開発の場合は `http://localhost:50021` を使用してください。
- `DATA_DIR` は相対パスまたは絶対パスで指定できます。Docker Compose 使用時はボリュームマウントに注意してください。

### ローカル開発環境（Docker 不使用）

Docker を使用せずに開発する場合の手順です。

#### 前提条件

- Python 3.11 以上
- VOICEVOX Engine が別途起動している（ポート 50021）

#### 1. Python 仮想環境のセットアップ

```bash
cd voicevox-intonation-dict/server

# 仮想環境を作成
python3 -m venv venv

# 仮想環境を有効化
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 依存パッケージをインストール
pip install -r requirements.txt

# 開発用パッケージをインストール（テスト実行に必要）
pip install pytest pytest-asyncio httpx
```

#### 2. 環境変数の設定

```bash
cd ..  # プロジェクトルートに戻る
cp .env.example .env

# .env ファイルを編集（必要に応じて）
# VOICEVOX_ENGINE_URL=http://localhost:50021
# EXTENSION_SERVER_PORT=8000
# DATA_DIR=./data
# DEBUG=true
```

#### 3. VOICEVOX Engine の起動

別のターミナルで VOICEVOX Engine を起動してください。

```bash
# Docker で起動する場合
docker run -d -p 50021:50021 --name voicevox-engine \
  --platform linux/amd64 \
  voicevox/voicevox_engine:cpu-ubuntu20.04-0.25.1

# 起動確認
curl http://127.0.0.1:50021/version
```

#### 4. 拡張辞書サーバーの起動

```bash
cd server

# uvicorn で起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# または環境変数を指定して起動
VOICEVOX_ENGINE_URL=http://localhost:50021 \
DATA_DIR=../data \
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 5. 動作確認

別のターミナルから以下を実行してください。

```bash
# ヘルスチェック
curl http://127.0.0.1:8000/health

# 辞書全体取得
curl http://127.0.0.1:8000/api/v1/dictionary/

# APIドキュメント
open http://127.0.0.1:8000/docs
```

#### 6. テストの実行

```bash
cd server

# 仮想環境が有効化されていることを確認
# source venv/bin/activate

# すべてのテストを実行
pytest

# 詳細な出力で実行
pytest -v

# 特定のテストファイルを実行
pytest tests/test_synthesis.py

# カバレッジレポート付きで実行（pytest-cov が必要）
pip install pytest-cov
pytest --cov=app --cov-report=html

# カバレッジレポートを確認
open htmlcov/index.html
```

#### テスト構成

- `tests/test_synthesis.py` - 音声合成エンドポイントのテスト
- `tests/test_audio_query_service.py` - AudioQuery 処理ロジックのテスト
- `tests/test_matcher.py` - 辞書マッチング機能のテスト

テストは VOICEVOX Engine をモックしているため、Engine が起動していなくても実行できます。

## 開発

### Docker を使用する場合

#### コンテナの停止

```bash
docker compose down
```

#### コンテナの再起動

```bash
docker compose restart
```

#### ログ確認

```bash
# すべてのサービス
docker compose logs -f

# 特定のサービス
docker compose logs -f extension-server
docker compose logs -f voicevox-engine
```

#### コンテナ内に入る

```bash
docker compose exec extension-server bash
```

### ローカル開発の場合

#### サーバーの停止

サーバーが起動しているターミナルで `Ctrl+C` を押してください。

#### 仮想環境の無効化

```bash
deactivate
```

#### コードの変更

uvicorn は `--reload` オプション付きで起動しているため、コードを変更すると自動的に再読み込みされます。

## VOICEVOX Editor フォーク版との連携

このプロジェクトは、VOICEVOX Editor のフォーク版と連携して動作します。

### フォーク版リポジトリ

- **ロケーション**: `/Users/teradakousuke/Developer/voicevox-editor`
- **用途**: 拡張辞書機能を統合した VOICEVOX Editor

### 必要な環境

- Node.js 24.11.0
- nvm（Node.js バージョン管理）

### セットアップ手順

#### 1. nvm のインストール（未インストールの場合）

```bash
# macOS/Linux
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# インストール確認
nvm --version
```

#### 2. Node.js 24.11.0 のインストール

```bash
# Node.js 24.11.0 をインストール
nvm install 24.11.0

# デフォルトバージョンに設定
nvm alias default 24.11.0

# バージョン確認
node --version  # v24.11.0 と表示されることを確認
```

#### 3. VOICEVOX Editor フォーク版のセットアップ

```bash
cd /Users/teradakousuke/Developer/voicevox-editor

# Node.js バージョンを切り替え（プロジェクトディレクトリで実行）
nvm use 24.11.0

# 依存パッケージをインストール
npm install

# 開発サーバーを起動
npm run electron:serve
```

#### 4. 統合動作確認

1. **拡張辞書サーバーを起動**（このプロジェクト）

   ```bash
   cd /Users/teradakousuke/Developer/voicevox-intonation-dict

   # Docker の場合
   docker compose up -d

   # ローカル開発の場合
   cd server
   source venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **VOICEVOX Editor を起動**

   ```bash
   cd /Users/teradakousuke/Developer/voicevox-editor
   nvm use 24.11.0
   npm run electron:serve
   ```

3. **動作確認**

   - VOICEVOX Editor が起動したら、拡張辞書機能が利用できることを確認します
   - エディタ内で辞書登録・編集・音声合成が正しく動作するかテストします

### トラブルシューティング

#### Node.js バージョンが異なる場合

```bash
# 現在のバージョンを確認
node --version

# 24.11.0 に切り替え
nvm use 24.11.0

# .nvmrc ファイルがある場合
nvm use
```

#### Editor が拡張辞書サーバーに接続できない場合

```bash
# 拡張辞書サーバーが起動しているか確認
curl http://127.0.0.1:8000/health

# ポート 8000 が使用中か確認
lsof -i :8000

# Editor の接続設定を確認（環境変数または設定ファイル）
# EXTENSION_DICT_URL=http://localhost:8000
```

## M4 Mac対応について

- VOICEVOX Engine: `platform: linux/amd64` を指定（Rosetta 2経由で実行）
- 拡張サーバー: マルチアーキテクチャビルドで ARM64 ネイティブ対応
- 両アーキテクチャで動作確認済み
- VOICEVOX Editor: Node.js 24.11.0 で ARM64 ネイティブ動作

## トラブルシューティング

### コンテナが起動しない

```bash
# ログを確認
docker compose logs

# 完全クリーンアップして再ビルド
docker compose down -v
docker compose up -d --build
```

### ポートが使用中

他のプロセスが50021または8000ポートを使用している可能性があります。

```bash
# ポート使用状況を確認
lsof -i :50021
lsof -i :8000
```

### VOICEVOX Engineに接続できない

```bash
# ヘルスチェック確認
docker compose ps
curl http://127.0.0.1:50021/version
```

## 参考リンク

- [VOICEVOX Engine GitHub](https://github.com/VOICEVOX/voicevox_engine)
- [VOICEVOX Engine API仕様](https://voicevox.github.io/voicevox_engine/api/)
- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)

## ライセンス

このプロジェクトは独自の拡張機能です。VOICEVOX Engineは別ライセンスです。

---

**プロジェクト管理**: Cor.Inc  
**作成日**: 2026年1月17日
