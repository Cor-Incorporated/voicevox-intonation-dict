# =============================================================================
# VOICEVOX Intonation Dictionary - Makefile
# =============================================================================
# プロジェクトの開発・テスト・ビルド・デプロイを管理するMakefile
#
# 使い方: make [ターゲット]
# ヘルプ: make help
# =============================================================================

# デフォルトシェル
SHELL := /bin/bash

# ディレクトリ設定
ROOT_DIR := $(shell pwd)
SERVER_DIR := $(ROOT_DIR)/server
WEB_DIR := $(ROOT_DIR)/web

# Python設定
PYTHON := python3
PIP := pip3

# Node.js設定
NPM := npm

# Docker設定
DOCKER_COMPOSE := docker compose

# =============================================================================
# .PHONY ターゲット宣言
# =============================================================================
.PHONY: help dev dev-server dev-web test test-server test-web \
        lint lint-server lint-web build docker-up docker-down docker-build clean

# =============================================================================
# デフォルトターゲット
# =============================================================================
.DEFAULT_GOAL := help

# =============================================================================
# ヘルプ
# =============================================================================
## help: 利用可能なコマンド一覧を表示
help:
	@echo ""
	@echo "VOICEVOX Intonation Dictionary - Makefile"
	@echo "=========================================="
	@echo ""
	@echo "利用可能なコマンド:"
	@echo ""
	@echo "  開発:"
	@echo "    make dev          - 開発サーバー起動（FastAPI + Web 同時起動）"
	@echo "    make dev-server   - バックエンドのみ起動（FastAPI）"
	@echo "    make dev-web      - フロントエンドのみ起動（React）"
	@echo ""
	@echo "  テスト:"
	@echo "    make test         - 全テスト実行（バックエンド + フロントエンド）"
	@echo "    make test-server  - バックエンドテスト（pytest）"
	@echo "    make test-web     - フロントエンドテスト"
	@echo ""
	@echo "  リント:"
	@echo "    make lint         - 全リンター実行"
	@echo "    make lint-server  - Python lint（ruff）"
	@echo "    make lint-web     - TypeScript lint（eslint）"
	@echo ""
	@echo "  ビルド:"
	@echo "    make build        - 本番ビルド（フロントエンド）"
	@echo ""
	@echo "  Docker:"
	@echo "    make docker-up    - Dockerコンテナ起動"
	@echo "    make docker-down  - Dockerコンテナ停止"
	@echo "    make docker-build - Dockerイメージビルド"
	@echo ""
	@echo "  その他:"
	@echo "    make clean        - キャッシュ・一時ファイルをクリア"
	@echo ""

# =============================================================================
# 開発サーバー
# =============================================================================
## dev: 開発サーバー起動（FastAPI + Web 同時起動）
## バックエンドとフロントエンドを同時に起動します
dev:
	@echo "==> 開発サーバーを起動しています..."
	@trap 'kill 0' SIGINT; \
	$(MAKE) dev-server & \
	$(MAKE) dev-web & \
	wait

## dev-server: バックエンドのみ起動（FastAPI）
## ポート8000でFastAPIサーバーを起動します
dev-server:
	@echo "==> FastAPIサーバーを起動しています..."
	cd $(SERVER_DIR) && $(PYTHON) -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

## dev-web: フロントエンドのみ起動（React）
## ポート3000でReact開発サーバーを起動します
dev-web:
	@echo "==> React開発サーバーを起動しています..."
	cd $(WEB_DIR) && $(NPM) run dev

# =============================================================================
# テスト
# =============================================================================
## test: 全テスト実行（バックエンド + フロントエンド）
test: test-server test-web
	@echo "==> 全テスト完了"

## test-server: バックエンドテスト（pytest）
## pytestを使用してバックエンドのユニットテストを実行します
test-server:
	@echo "==> バックエンドテストを実行しています..."
	cd $(SERVER_DIR) && $(PYTHON) -m pytest -v

## test-web: フロントエンドテスト
## フロントエンドのテストを実行します
test-web:
	@echo "==> フロントエンドテストを実行しています..."
	cd $(WEB_DIR) && $(NPM) test

# =============================================================================
# リント
# =============================================================================
## lint: 全リンター実行
lint: lint-server lint-web
	@echo "==> 全リント完了"

## lint-server: Python lint（ruff）
## ruffを使用してPythonコードの静的解析を実行します
lint-server:
	@echo "==> Python lint（ruff）を実行しています..."
	cd $(SERVER_DIR) && $(PYTHON) -m ruff check .
	cd $(SERVER_DIR) && $(PYTHON) -m ruff format --check .

## lint-web: TypeScript lint（eslint）
## eslintを使用してTypeScriptコードの静的解析を実行します
lint-web:
	@echo "==> TypeScript lint（eslint）を実行しています..."
	cd $(WEB_DIR) && $(NPM) run lint

# =============================================================================
# ビルド
# =============================================================================
## build: 本番ビルド
## フロントエンドの本番用ビルドを作成します
build:
	@echo "==> 本番ビルドを実行しています..."
	cd $(WEB_DIR) && $(NPM) run build
	@echo "==> ビルド完了: $(WEB_DIR)/dist"

# =============================================================================
# Docker
# =============================================================================
## docker-up: Dockerコンテナ起動
## docker-compose.ymlを使用してコンテナを起動します
docker-up:
	@echo "==> Dockerコンテナを起動しています..."
	$(DOCKER_COMPOSE) up -d
	@echo "==> Dockerコンテナが起動しました"

## docker-down: Dockerコンテナ停止
## 実行中のDockerコンテナを停止・削除します
docker-down:
	@echo "==> Dockerコンテナを停止しています..."
	$(DOCKER_COMPOSE) down
	@echo "==> Dockerコンテナを停止しました"

## docker-build: Dockerイメージビルド
## Dockerイメージを再ビルドします
docker-build:
	@echo "==> Dockerイメージをビルドしています..."
	$(DOCKER_COMPOSE) build
	@echo "==> Dockerイメージのビルドが完了しました"

# =============================================================================
# クリーンアップ
# =============================================================================
## clean: キャッシュ・一時ファイルをクリア
## Python/Node.jsのキャッシュファイルを削除します
clean:
	@echo "==> キャッシュをクリアしています..."
	# Python キャッシュ削除
	find $(SERVER_DIR) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find $(SERVER_DIR) -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find $(SERVER_DIR) -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find $(SERVER_DIR) -type f -name "*.pyc" -delete 2>/dev/null || true
	find $(ROOT_DIR) -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	# Node.js キャッシュ削除
	rm -rf $(WEB_DIR)/node_modules/.cache 2>/dev/null || true
	rm -rf $(WEB_DIR)/dist 2>/dev/null || true
	rm -rf $(WEB_DIR)/.next 2>/dev/null || true
	@echo "==> キャッシュのクリアが完了しました"
