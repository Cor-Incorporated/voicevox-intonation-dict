# 実装品質保護ルール

## 絶対禁止事項

### 形骸化実装の禁止
- **`pass` だけの空実装を残さない**
- **`# TODO` を書いて放置しない（同一セッション内で完了）**
- **ハードコードで動作確認だけしてコミットしない**

### モック濫用の禁止
- **本来の処理をモックで置き換えてテストをパスさせない**
- **外部依存のモックは最小限に**

---

## 実装チェックリスト

### 関数を実装したら
- [ ] 型ヒントがついている
- [ ] docstring がある（複雑な場合）
- [ ] エラーハンドリングがある
- [ ] テストがある（または手動確認済み）

### API エンドポイントを実装したら
- [ ] レスポンスモデルが定義されている
- [ ] エラーレスポンスが適切
- [ ] `/docs` で動作確認済み

---

## コード品質基準

### 関数の長さ
- 1関数は50行以内を目安
- 長くなる場合は分割を検討

### 循環的複雑度
- if/for のネストは3階層まで
- 深くなる場合は早期リターンやヘルパー関数で対応

### 命名
- 略語は避ける（`dict_entry` > `de`）
- 動詞で始める関数名（`apply_pitch()` > `pitch_applier()`）

---

## 禁止パターン

```python
# ❌ NG: 空実装
def apply_extended_dict(self, audio_query, entry):
    pass

# ❌ NG: ハードコード
def get_speaker_id(self):
    return 1  # 常に1を返す

# ❌ NG: エラー握りつぶし
try:
    result = risky_operation()
except Exception:
    pass  # 何も起きていない顔
```

---

## 許可パターン

```python
# ✅ OK: 完全な実装
def apply_extended_dict(
    self,
    audio_query: dict,
    entry: ExtendedDictEntry,
    match_result: MatchResult
) -> dict:
    """
    AudioQueryの該当箇所をエントリのピッチ・長さで上書きする。

    Args:
        audio_query: VOICEVOX の AudioQuery
        entry: 拡張辞書エントリ
        match_result: マッチング結果（位置情報）

    Returns:
        上書き後の AudioQuery

    Raises:
        ValueError: モーラ数が一致しない場合
    """
    # 実装...
    return modified_query

# ✅ OK: 適切なエラーハンドリング
try:
    response = await client.post(url)
    response.raise_for_status()
except httpx.RequestError as e:
    logger.error(f"VOICEVOX Engine connection failed: {e}")
    raise HTTPException(status_code=503, detail="Engine unavailable")
```
