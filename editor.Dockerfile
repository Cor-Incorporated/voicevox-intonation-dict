# VOICEVOX Editor (Browser版) Dockerfile
# Multi-stage build: ビルド → nginx で配信

# Stage 1: Build
FROM node:24-slim AS builder

# pnpm をインストール
RUN corepack enable && corepack prepare pnpm@10.20.0 --activate

WORKDIR /app

# 依存関係のインストール（キャッシュ効率化のため先にpackage.jsonをコピー）
COPY editor/package.json editor/pnpm-lock.yaml editor/pnpm-workspace.yaml ./
COPY editor/.pnpmfile.cjs ./
COPY editor/eslint-plugin ./eslint-plugin/

# playwright と electron のダウンロードをスキップ（ブラウザビルドには不要）
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
ENV ELECTRON_SKIP_BINARY_DOWNLOAD=1

RUN pnpm install --frozen-lockfile --ignore-scripts

# ソースコードをコピー
COPY editor/ ./

# Docker用の環境変数設定
# エンジンURLはブラウザからアクセスするため localhost を使用
# (docker-compose で port 50021 がホストに公開されている前提)
ENV VITE_TARGET=browser
ENV VITE_DEFAULT_ENGINE_INFOS='[{"uuid":"074fc39e-678b-4c13-8916-ffca8d505d1d","name":"VOICEVOX Engine","executionEnabled":false,"executionFilePath":"","executionArgs":[],"host":"http://127.0.0.1:50021"}]'

# ブラウザ版をビルド
RUN pnpm run browser:build

# Stage 2: Production (nginx)
FROM nginx:alpine

# ビルド成果物をコピー
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx設定（SPA対応）
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location /api { \
        proxy_pass http://extension-server:8000; \
        proxy_http_version 1.1; \
        proxy_set_header Upgrade $http_upgrade; \
        proxy_set_header Connection "upgrade"; \
        proxy_set_header Host $host; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
