# テスト品質保護ルール

## 絶対禁止事項

### テスト改ざん禁止
- **テストをパスさせるためだけにアサーションを変更しない**
- **失敗するテストを削除・コメントアウトしない**
- **テストの期待値を実装に合わせて書き換えない**

### 正しい対応
1. テストが失敗した場合 → **実装を修正**
2. テストの仕様が間違っている場合 → **ユーザーに確認してから修正**
3. 仕様変更でテストを変える必要がある場合 → **変更理由を明記**

---

## テスト作成ルール

### 必須テストケース
- 正常系: 期待通りの入力で期待通りの出力
- 異常系: 不正な入力でエラーが発生
- 境界値: 配列の空・1要素・大量要素

### テスト構造
```python
def test_機能名_条件_期待結果():
    # Arrange（準備）
    input_data = ...

    # Act（実行）
    result = function(input_data)

    # Assert（検証）
    assert result == expected
```

---

## 禁止パターン

```python
# ❌ NG: 常にパスするテスト
def test_always_pass():
    assert True

# ❌ NG: テストしていないテスト
def test_placeholder():
    pass

# ❌ NG: 実装に合わせた期待値
def test_wrong():
    result = buggy_function()
    assert result == "wrong_output"  # バグった結果を正解にしている
```

---

## 許可パターン

```python
# ✅ OK: 具体的な期待値
def test_apply_pitch_values():
    audio_query = sample_query()
    entry = ExtendedDictEntry(pitch_values=[5.0, 5.5, 5.2])

    result = service.apply_extended_dict(audio_query, entry)

    assert result["accent_phrases"][0]["moras"][0]["pitch"] == 5.0
    assert result["accent_phrases"][0]["moras"][1]["pitch"] == 5.5

# ✅ OK: エラーケースの検証
def test_mismatch_mora_count_raises():
    audio_query = sample_query()  # 3モーラ
    entry = ExtendedDictEntry(pitch_values=[5.0, 5.5])  # 2値

    with pytest.raises(ValueError, match="mora count mismatch"):
        service.apply_extended_dict(audio_query, entry)
```
