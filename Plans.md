# Plans.md - タスク管理

## 現在のフェーズ: Phase 7 - ドキュメント・テスト整備 ✅ 完了

**目標**: 誰でもどんな環境でも使えるようにする（Docker + ローカル両対応）

---

## ✅ 完了済みフェーズ

| フェーズ | 内容 | アーカイブ |
|---------|------|----------|
| Phase 1-3 | MVP（AudioQuery上書き、マッチング、拡張合成API） | `.claude/archive/plans-mvp-complete.md` |
| Phase 4 | マッチング改善（部分一致、表記照合） | `.claude/archive/plans-phase4-complete.md` |
| Phase 5 | 辞書編集UI（React版） | `.claude/archive/plans-phase5-complete.md` |
| Phase 6 | UI改善 & VOICEVOXエディタ統合 | `.claude/archive/plans-phase6-complete.md` |
| Phase 7 | ドキュメント・テスト整備 | 本ファイル |

**バックエンドテスト**: 80+ tests pass（pytest）
**フロントエンドテスト**: 15 tests pass（Vitest）

---

## Phase 7: ドキュメント・テスト整備 ✅ 完了

### ✅ Task 7.1: README.md 整備（バックエンド）

- [x] ローカル開発環境のセットアップ手順（Python venv）
- [x] テストの実行方法（pytest）
- [x] voicevox-editor（フォーク版）との連携セクション
- [x] 環境変数の詳細説明

**成果物**: `README.md` 更新済み（494行）

---

### ✅ Task 7.2: 辞書API テスト追加
**ファイル**: `server/tests/test_dictionary.py`

| テストケース | 入力 | 結果 |
|-------------|------|------|
| 一覧取得（空） | GET /dictionary/ | ✅ |
| 一覧取得（データあり） | GET /dictionary/ | ✅ |
| 新規登録 | POST + 有効エントリ | ✅ |
| 上書き登録（upsert） | POST + 既存word | ✅ |
| 削除 | DELETE /{word} | ✅ |
| 空のword | POST + `{"word": ""}` | ✅ |
| 存在しないword削除 | DELETE /存在しない | ✅ |

**成果物**: 14 tests pass

---

### ✅ Task 7.3: プレビューAPI テスト追加
**ファイル**: `server/tests/test_preview.py`

| テストケース | 入力 | 結果 |
|-------------|------|------|
| プレビュー合成 | POST + AudioQuery | ✅ |
| 空のAudioQuery | POST + `{}` | ✅ |
| VOICEVOX未起動 | POST + 有効Query | ✅ |

**成果物**: 10 tests pass

---

### ✅ Task 7.4: Makefile 作成

- [x] `make dev` - 開発サーバー起動
- [x] `make test` - テスト実行
- [x] `make lint` - リンター実行

**成果物**: `Makefile`（14 targets）

---

### ✅ Task 7.5: CI/CD 設定
**ファイル**: `.github/workflows/ci.yml`

- [x] Push/PR時に自動テスト
- [x] Python lint（ruff）+ pytest
- [x] TypeScript lint（eslint）

**成果物**: GitHub Actions CI workflow

---

### ✅ Task 7.6: voicevox-editor ドキュメント
**リポジトリ**: `/Users/teradakousuke/Developer/voicevox-editor`

- [x] EXTENDED_DICTIONARY.md 作成
- [x] セットアップ手順（Node.js 24.11.0 + nvm）
- [x] バックエンド連携方法

**成果物**: `EXTENDED_DICTIONARY.md`（400+ lines）

---

### ✅ Task 7.7: voicevox-editor コンポーネントテスト
**ファイル**: `tests/unit/components/Dialog/ExtendedDictionaryDialog.spec.ts`

| テストケース | 操作 | 結果 |
|-------------|------|------|
| 初期表示 | ダイアログ開く | ✅ |
| 単語選択 | リストクリック | ✅ |
| 発音取得 | ボタンクリック | ✅ |
| スライダー操作 | 値変更 | ✅ |
| 保存 | ボタンクリック | ✅ |
| 削除 | ボタンクリック | ✅ |
| エラーハンドリング | API失敗 | ✅ |
| キャンセル | ボタンクリック | ✅ |

**成果物**: 15 tests pass

---

### ✅ Task 7.8: 拡張辞書適用バグ修正（2026-01-18 追加）
**リポジトリ**: `/Users/teradakousuke/Developer/voicevox-editor`

**問題**: Editor で辞書登録済みの単語（ずんだもん）を入力しても、ピッチ・長さが反映されない

**原因**: Editor（TypeScript）とServer（Python）間の JSON キー名規則の不一致
- Editor 内部: `accentPhrases`（camelCase）
- Server API: `accent_phrases`（snake_case）

**解決策**: `audio.ts` で双方向変換を実装
- リクエスト送信時: `AudioQueryToJSON()` で camelCase → snake_case
- レスポンス受信時: `AudioQueryFromJSON()` で snake_case → camelCase

**変更ファイル**:
- `voicevox-editor/src/store/audio.ts` - 変換処理追加（1010行目、2047行目）

**成果物**: 拡張辞書適用が正常動作

---

## Phase 7 成功基準 ✅ 達成

1. **ドキュメント**: README.md だけでセットアップ可能 ✅
2. **テスト**: 辞書API + プレビューAPI のテスト追加 ✅
3. **CI/CD**: Push時に自動テスト実行 ✅
4. **環境**: `make dev` で起動可能 ✅
5. **バグ修正**: 拡張辞書適用が正常動作 ✅

---

## 作成されたファイル一覧

### バックエンド (voicevox-intonation-dict)
- `README.md` - 更新（セットアップ手順追加）
- `Makefile` - 新規作成
- `.github/workflows/ci.yml` - 新規作成
- `server/tests/test_dictionary.py` - 新規作成
- `server/tests/test_preview.py` - 新規作成
- `server/tests/test_audio_query_service.py` - 新規作成
- `server/tests/test_matcher.py` - 新規作成

### フロントエンド (voicevox-editor)
- `EXTENDED_DICTIONARY.md` - 新規作成
- `tests/unit/components/Dialog/ExtendedDictionaryDialog.spec.ts` - 新規作成

---

## 技術参考

- [VOICEVOX Engine API仕様](https://voicevox.github.io/voicevox_engine/api/)
- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [Vitest公式ドキュメント](https://vitest.dev/)
