# VOICEVOX Editor Extended v1.0.0 - ローカルテストガイド

このドキュメントでは、VOICEVOX Editor Extended をローカル環境でテストする手順を説明します。

---

## 概要

VOICEVOX Editor Extended は、イントネーション辞書機能を搭載した VOICEVOX Editor の拡張版です。

**構成**:
```
┌──────────────────────────────────────────────────┐
│ Docker Compose (docker compose up -d)            │
│ ┌─────────────────┐  ┌─────────────────┐         │
│ │ VOICEVOX Engine │  │ Extension Server│         │
│ │   (port 50021)  │  │   (port 8000)   │         │
│ └─────────────────┘  └─────────────────┘         │
└──────────────────────────────────────────────────┘
                      ↑ HTTP API
        ┌──────────────────────────────┐
        │ VOICEVOX Editor Extended     │
        │ (GitHub Releases からDL)      │
        └──────────────────────────────┘
```

---

## 必要な環境

- **Docker** (Docker Desktop または Docker Engine)
- **Git**
- **OS**: Windows 10/11、macOS (Intel または Apple Silicon)

---

## セットアップ手順

### Step 1: バックエンドの起動

```bash
# リポジトリをクローン
git clone https://github.com/Cor-Incorporated/voicevox-intonation-dict
cd voicevox-intonation-dict

# Docker Compose で起動
docker compose up -d
```

**起動確認**:
```bash
# ログを確認（エラーがないことを確認）
docker compose logs -f

# ヘルスチェック
curl http://127.0.0.1:50021/version  # VOICEVOX Engine
curl http://127.0.0.1:8000/health    # Extension Server
```

**期待される出力**:
- Engine: `{"version": "..."}` のような JSON
- Server: `{"status": "ok"}` のような JSON

### Step 2: Editor のダウンロード

GitHub Releases からダウンロード:
**https://github.com/Cor-Incorporated/voicevox-editor-extended/releases/tag/v1.0.0**

| OS | ファイル |
|----|---------|
| Windows x64 | `VOICEVOX.Web.Setup.1.0.0.exe` |
| macOS ARM64 (Apple Silicon) | `VOICEVOX-1.0.0-arm64.dmg` |
| macOS x64 (Intel) | `VOICEVOX-1.0.0.dmg` |

### Step 3: Editor のインストールと起動

#### Windows
1. `VOICEVOX.Web.Setup.1.0.0.exe` を実行
2. インストーラーの指示に従ってインストール
3. スタートメニューから「VOICEVOX」を起動

#### macOS
1. `.dmg` ファイルを開く
2. VOICEVOX.app を Applications フォルダにドラッグ
3. **重要**: 初回起動時は以下の手順で署名回避が必要:
   - Finder で Applications フォルダを開く
   - VOICEVOX.app を **右クリック** → 「開く」を選択
   - 「開く」ボタンをクリック（警告が表示される場合）

または Terminal で:
```bash
xattr -cr /Applications/VOICEVOX.app
```

---

## 機能テスト手順

### 1. 基本的な音声合成

1. Editor を起動
2. テキスト欄に「ずんだもん」と入力
3. 再生ボタンをクリック
4. 音声が再生されることを確認

### 2. イントネーション辞書機能

1. **辞書管理ダイアログを開く**
   - メニュー「設定」→「辞書管理」をクリック
   - 「イントネーション」タブを選択

2. **辞書エントリを追加**
   - 「追加」ボタンをクリック
   - 単語: 任意の単語（例: 「テスト」）
   - 読み: カタカナで入力（例: 「テスト」）
   - アクセント位置を調整
   - ピッチ/長さを調整（スライダーまたは数値入力）
   - 「保存」をクリック

3. **辞書の適用を確認**
   - テキスト欄に登録した単語を入力
   - 再生して、ピッチ/長さが変更されていることを確認

### 3. 辞書のインポート/エクスポート

1. 辞書管理ダイアログで「エクスポート」をクリック
2. JSON ファイルが保存されることを確認
3. 別の環境で「インポート」からファイルを読み込み

---

## トラブルシューティング

### バックエンドに接続できない

**症状**: Editor 起動時に「エンジンに接続できません」と表示される

**解決策**:
1. Docker コンテナが起動しているか確認:
   ```bash
   docker compose ps
   ```
2. ポートが正しく開いているか確認:
   ```bash
   curl http://127.0.0.1:50021/version
   ```
3. ファイアウォールがブロックしていないか確認

### macOS で「開発元を確認できない」と表示される

**解決策**:
- 右クリック →「開く」で起動
- または Terminal で `xattr -cr /Applications/VOICEVOX.app`

### Windows で「WindowsによってPCが保護されました」と表示される

**解決策**:
- 「詳細情報」をクリック
- 「実行」をクリック

### 辞書が適用されない

**症状**: 辞書を登録したが、音声合成に反映されない

**解決策**:
1. Extension Server が起動しているか確認:
   ```bash
   curl http://127.0.0.1:8000/health
   ```
2. 辞書が正しく保存されているか確認:
   ```bash
   curl http://127.0.0.1:8000/api/v1/dictionary/
   ```

---

## 停止方法

```bash
# バックエンドを停止
cd voicevox-intonation-dict
docker compose down
```

---

## 技術的な詳細

### API エンドポイント

| エンドポイント | 説明 |
|---------------|------|
| `GET /api/v1/dictionary/` | 辞書一覧を取得 |
| `POST /api/v1/dictionary/` | 辞書エントリを追加 |
| `DELETE /api/v1/dictionary/{word}` | 辞書エントリを削除 |
| `POST /api/v1/synthesize/apply` | AudioQuery に辞書を適用 |

### 辞書データ形式

```json
{
  "word": "ずんだもん",
  "pronunciation": "ズンダモン",
  "accent_type": 3,
  "mora_count": 5,
  "pitch_values": [5.2, 5.8, 5.5, 5.3, 4.8],
  "length_values": [0.12, 0.08, 0.15, 0.10, 0.12],
  "speaker_id": 1
}
```

---

## サポート

問題が発生した場合は、以下のリポジトリに Issue を作成してください:

- **Editor 関連**: https://github.com/Cor-Incorporated/voicevox-editor-extended/issues
- **バックエンド関連**: https://github.com/Cor-Incorporated/voicevox-intonation-dict/issues

---

## リリース情報

- **バージョン**: v1.0.0
- **リリース日**: 2026-01-18
- **リリースページ**: https://github.com/Cor-Incorporated/voicevox-editor-extended/releases/tag/v1.0.0
