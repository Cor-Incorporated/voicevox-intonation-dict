# Plans.md - タスク管理

## 現在のフェーズ: Phase 9 - CI/CD 修正 & リリース準備 `cc:WIP`

**目標**: CI テストを通過させ、初回リリースを作成する

---

## ✅ 完了済みフェーズ

| フェーズ | 内容 | アーカイブ |
|---------|------|----------|
| Phase 1-3 | MVP（AudioQuery上書き、マッチング、拡張合成API） | `.claude/archive/plans-mvp-complete.md` |
| Phase 4 | マッチング改善（部分一致、表記照合） | `.claude/archive/plans-phase4-complete.md` |
| Phase 5 | 辞書編集UI（React版） | `.claude/archive/plans-phase5-complete.md` |
| Phase 6 | UI改善 & VOICEVOXエディタ統合 | `.claude/archive/plans-phase6-complete.md` |
| Phase 7 | ドキュメント・テスト整備 | `.claude/archive/plans-phase7-complete.md` |
| Phase 8 | 配布準備（Docker, GitHub Actions） | 下記参照 |

**テスト状況**: バックエンド 80+ tests / フロントエンド 15 tests

---

## Phase 8: 配布準備 ✅ 完了

### 配布構成

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
        │ voicevox-editor-extended     │
        │ (GitHub Releases からDL)      │
        │ - Windows: .exe              │
        │ - macOS: .dmg                │
        └──────────────────────────────┘
```

---

### Task 8.1: docker-compose.yml 簡素化 ✅ 完了

**成果物**:
- `docker-compose.yml`（配布用）- Editor サービス削除、シンプル化
- `docker-compose.dev.yml`（開発用）- ホットリロード対応

---

### Task 8.2: Editor ビルド用 GitHub Actions ✅ 完了

**ファイル**: `voicevox-editor/.github/workflows/build-extended.yml`

| ターゲット | アーティファクト |
|-----------|-----------------|
| Windows x64 | `.exe` (NSIS Web Installer) |
| macOS x64 | `.dmg` |
| macOS ARM64 | `.dmg` |

**特徴**:
- Engine をバンドルしない軽量ビルド
- タグプッシュで GitHub Releases に自動アップロード

---

### Task 8.3: セットアップガイド更新 ✅ 完了

**README.md に追加**:
- 🚀 クイックスタート（3ステップ）セクション
- 🏗️ アーキテクチャ図
- 🔧 トラブルシューティング強化

---

### Task 8.4: Extension Server 接続先確認 ✅ 完了

**確認結果**:
- デフォルト接続先: `http://localhost:8000/api/v1`
- ファイル: `voicevox-editor/src/infrastructures/extendedDictApi.ts:55`
- 現状で問題なし（変更不要）

---

## Phase 8 成功基準 ✅ 達成

1. **Docker**: `docker compose up -d` で Engine + Server が起動 ✅
2. **Editor**: GitHub Actions でビルド設定完了（Releases は次回タグプッシュで作成） ✅
3. **接続**: Editor → Extension Server → Engine の連携が動作 ✅（既存実装で確認済み）
4. **ドキュメント**: README を読むだけでセットアップ完了 ✅

---

---

## Phase 9: CI/CD 修正 & リリース準備 `cc:WIP`

### 問題点（CI 失敗の原因）

| Job | エラー内容 |
|-----|-----------|
| **lint** | `ExtendedDictionaryDialog.vue` のフォーマットエラー（カンマ、shorthand、イベント名） |
| **unit-test** | `ExtendedDictionaryDialog.vue:250` で `TypeError: Cannot read properties of undefined (reading 'getters')` |
| **e2e-test** | メニュー名変更による「読み方＆アクセント辞書」テスト失敗 |

---

### Task 9.1: lint エラー修正 ✅ 完了

**修正内容**:
- [x] `pnpm run lint --fix` で自動修正（35 件）
- [x] 手動修正:
  - `extendedDictApi.ts`: `response.json()` に型アサーション追加
  - `ExtendedDictionaryPanel.vue`: `nextTick()` に `void` 追加
  - `audio.ts`: `AudioQueryToJSON` の戻り値に型アサーション追加

---

### Task 9.2: unit-test エラー修正 ✅ 完了

**修正内容**:
- [x] `ExtendedDictionaryDialog.vue`: `store?.getters?.` で防御的処理
- [x] テストファイル: `CharacterButton` をスタブ化（store 依存回避）
- [x] テストファイル: `eslint-disable` コメント追加（`no-non-null-assertion`, `unbound-method`）

**結果**: ExtendedDictionaryDialog テスト 15/15 通過

---

### Task 9.3: e2e テスト更新 ✅ 完了

**修正内容**:
- [x] `辞書ダイアログ.spec.ts`: 「読み方＆アクセント辞書」→「辞書管理」に更新
  - `openDictDialog()` 関数
  - テスト名
  - ダイアログ閉じる時のヘッダーロケーター

---

### Task 9.4: ドキュメント補完 ✅ 完了

**修正内容**:

1. **voicevox-editor/README.md**:
   - [x] 拡張版であることの説明を追加
   - [x] イントネーション辞書機能の説明
   - [x] クイックスタート手順
   - [x] macOS での署名回避手順

2. **voicevox-intonation-dict/README.md**:
   - [x] 使い方を「辞書管理」→「イントネーション」タブに更新
   - [x] macOS での署名回避手順を追加

---

### Task 9.5: 初回リリース作成 `cc:TODO`

**手順**:
- [x] CI が通過することを確認 ✅ (2026-01-18 全テスト成功)
- [ ] タグをプッシュ（`git tag v1.0.0 && git push upstream v1.0.0`）
- [ ] GitHub Releases が自動生成されることを確認

---

## Phase 9 成功基準

1. **CI**: lint, unit-test, e2e-test（全プラットフォーム）が通過 ✅
2. **ドキュメント**: 先方が README だけで完全にセットアップ可能
3. **リリース**: GitHub Releases にバイナリが公開

---

## 技術参考

- [VOICEVOX Engine API仕様](https://voicevox.github.io/voicevox_engine/api/)
- [electron-builder 公式](https://www.electron.build/)
