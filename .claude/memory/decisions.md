# decisions.md - 意思決定記録

## 2026-01-17: アーキテクチャ決定

### 決定: 外部ミドルウェア方式（B案）を採用

**背景**:
- VOICEVOX Engine の改変は避けたい
- 既存の Engine API をそのまま活用できる方式が望ましい

**選択肢**:
- A案: VOICEVOX Engine 内部を改変
- B案: 外部ミドルウェア方式（FastAPI で AudioQuery を加工）

**決定理由**:
- Engine のアップデートに追従しやすい
- 既存エコシステムとの互換性を維持
- 開発の独立性が高い

**結果**:
- `extension-server` (FastAPI) が VOICEVOX Engine の前段に位置
- AudioQuery 生成 → 加工 → 音声合成 のフローを外部から制御

---

## 2026-01-17: データ構造決定

### 決定: 拡張辞書のデータ構造

```python
ExtendedDictEntry:
  - word: str           # 表記（ずんだもん）
  - pronunciation: str  # 読み（ズンダモン）
  - accent_type: int    # アクセント型
  - pitch_values: list  # モーラごとのピッチ
  - length_values: list # モーラごとの長さ
```

**決定理由**:
- VOICEVOX の AudioQuery 構造と直接対応
- 上書きロジックがシンプルになる
- 将来の拡張性も考慮

---

## 2026-01-18: Editor連携時のJSON変換

### 決定: AudioQuery の双方向キー名変換を実装

**背景**:
- VOICEVOX Editor 内部は camelCase（`accentPhrases`, `pauseMora`）
- サーバー API（Python/FastAPI）は snake_case（`accent_phrases`, `pause_mora`）
- 拡張辞書 API と通信するとき、キー名の不一致で辞書適用が効かない問題が発生

**解決策**:
- **リクエスト時**: `AudioQueryToJSON()` で camelCase → snake_case
- **レスポンス時**: `AudioQueryFromJSON()` で snake_case → camelCase

**実装箇所** (`voicevox-editor/src/store/audio.ts`):

```typescript
// リクエスト送信前（FETCH_AUDIO_QUERY, COMMAND_CHANGE_AUDIO_TEXT）
const queryForServer = AudioQueryToJSON(originalQuery);
const result = await extendedDictApi.applyDictionary(queryForServer, text, styleId);

// レスポンス受信後
const convertedQuery = AudioQueryFromJSON(result.audio_query);
```

**学び**:
- OpenAPI 生成コードには `*FromJSON` / `*ToJSON` 変換関数が用意されている
- 外部 API との通信時はこれらを使って双方向変換を行う必要がある
- Editor 内部の型と OpenAPI 型が微妙に異なる場合は `as any` で回避

---

## 今後の決定事項（保留）

- [ ] 複数話者対応時のデータ構造
- [x] フロントエンド技術選定 → React + Vite（Vue.js から移行検討なし、既存を活用）
- [ ] 本番デプロイ方式
