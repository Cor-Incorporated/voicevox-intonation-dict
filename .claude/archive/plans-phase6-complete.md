# Phase 6: UI改善 & VOICEVOXエディタ風機能（アーカイブ）

> アーカイブ日: 2026-01-17
> 状態: Phase 6 の一部は voicevox-editor フォークで実装済み

## 概要
- **バグ修正**: スライダー調整のリアルタイムプレビュー、辞書の重複登録防止
- **新機能**: VOICEVOXエディタ風のUI（ピッチ曲線、アクセント、話者選択）

---

## 実装済み（voicevox-editor フォーク）

### Task 6.1: バグ修正 - リアルタイムプレビュー ✅
- `/synthesize/preview` エンドポイント追加済み
- ExtendedDictionaryDialog.vue でスライダー変更時に即座にプレビュー可能

### Task 6.4: ピッチ曲線エディタ ✅
- Canvas でピッチ曲線を描画
- マウスドラッグでピッチ値を変更
- モーラ名を下に表示

### ExtendedDictionaryDialog.vue 実装内容
- 単語一覧表示
- ピッチ曲線エディタ（キャンバス）
- モーラ別スライダー（ピッチ・長さ）
- リアルタイムプレビュー再生
- 保存・削除機能

---

## 未実装（React版のみ対象）

### Task 6.2: バグ修正 - 辞書の重複登録防止
**React版**: 要修正（add_entry を upsert に変更）

### Task 6.3: 話者選択機能
**React版**: 実装途中

### Task 6.5: アクセント位置調整
**両方**: 未実装（将来検討）

---

## 注記

VOICEVOXエディターフォーク版（`/Users/teradakousuke/Developer/voicevox-editor`）に
拡張辞書機能を追加済み。React版 (`web/`) は開発継続するか要検討。
