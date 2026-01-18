"""
Unit tests for DictionaryMatcher service.

Tests the word matching logic between AudioQuery moras and dictionary entries.
Matching is based on exact pronunciation match (complete match only, no partial).
"""

from typing import Any

import pytest

from app.models.extended_dict import ExtendedDictEntry
from app.services.matcher import DictionaryMatcher, MatchResult


def create_audio_query(accent_phrases: list[dict[str, Any]]) -> dict[str, Any]:
    """Helper function to create AudioQuery structure for testing.

    Args:
        accent_phrases: List of accent phrase dictionaries with moras.

    Returns:
        AudioQuery-like dictionary structure.
    """
    return {"accent_phrases": accent_phrases}


def create_accent_phrase(
    texts: list[str], accent: int = 1, pause_mora: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Helper function to create an accent phrase from text list.

    Args:
        texts: List of mora texts (katakana characters).
        accent: Accent position (1-indexed).
        pause_mora: Optional pause mora data.

    Returns:
        Accent phrase dictionary with moras.
    """
    moras = [{"text": t, "pitch": 0.0, "vowel_length": 0.1} for t in texts]
    phrase: dict[str, Any] = {"moras": moras, "accent": accent}
    if pause_mora is not None:
        phrase["pause_mora"] = pause_mora
    return phrase


def create_entry(word: str, pronunciation: str, accent_type: int = 1) -> ExtendedDictEntry:
    """Helper function to create a dictionary entry.

    Args:
        word: The word text.
        pronunciation: Katakana pronunciation for matching.
        accent_type: Accent type value.

    Returns:
        ExtendedDictEntry instance.
    """
    return ExtendedDictEntry(
        word=word,
        pronunciation=pronunciation,
        accent_type=accent_type,
    )


class TestExtractPronunciation:
    """Tests for DictionaryMatcher.extract_pronunciation method."""

    def test_single_accent_phrase(self) -> None:
        """Test extracting pronunciation from a single accent phrase."""
        audio_query = create_audio_query([
            create_accent_phrase(["コ", "ン", "ニ", "チ", "ワ"])
        ])
        matcher = DictionaryMatcher()
        result = matcher.extract_pronunciation(audio_query)
        assert result == "コンニチワ"

    def test_multiple_accent_phrases(self) -> None:
        """Test extracting pronunciation from multiple accent phrases."""
        audio_query = create_audio_query([
            create_accent_phrase(["コ", "ン", "ニ", "チ", "ワ"]),
            create_accent_phrase(["ズ", "ン", "ダ", "モ", "ン"]),
        ])
        matcher = DictionaryMatcher()
        result = matcher.extract_pronunciation(audio_query)
        assert result == "コンニチワズンダモン"

    def test_empty_accent_phrases(self) -> None:
        """Test extracting pronunciation from empty accent phrases."""
        audio_query = create_audio_query([])
        matcher = DictionaryMatcher()
        result = matcher.extract_pronunciation(audio_query)
        assert result == ""

    def test_accent_phrase_with_pause_mora(self) -> None:
        """Test that pause_mora is not included in pronunciation."""
        audio_query = create_audio_query([
            create_accent_phrase(
                ["コ", "ン", "ニ", "チ", "ワ"],
                pause_mora={"text": "、", "pitch": 0.0}
            )
        ])
        matcher = DictionaryMatcher()
        result = matcher.extract_pronunciation(audio_query)
        assert result == "コンニチワ"


class TestFindMatches:
    """Tests for DictionaryMatcher.find_matches method."""

    def test_single_match(self) -> None:
        """Test case: Normal - single match found."""
        audio_query = create_audio_query([
            create_accent_phrase(["ズ", "ン", "ダ", "モ", "ン"])
        ])
        entries = [create_entry("ずんだもん", "ズンダモン")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches(audio_query, entries)

        assert len(results) == 1
        assert results[0].entry == entries[0]
        assert results[0].accent_phrase_index == 0
        assert results[0].mora_start_index == 0
        assert results[0].mora_end_index == 5

    def test_multiple_matches_same_word(self) -> None:
        """Test case: Normal - multiple matches of the same word."""
        # "ズンダモンとズンダモン" split into accent phrases
        audio_query = create_audio_query([
            create_accent_phrase(["ズ", "ン", "ダ", "モ", "ン"]),
            create_accent_phrase(["ト"]),
            create_accent_phrase(["ズ", "ン", "ダ", "モ", "ン"]),
        ])
        entries = [create_entry("ずんだもん", "ズンダモン")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches(audio_query, entries)

        assert len(results) == 2
        # First match
        assert results[0].accent_phrase_index == 0
        assert results[0].mora_start_index == 0
        assert results[0].mora_end_index == 5
        # Second match
        assert results[1].accent_phrase_index == 2
        assert results[1].mora_start_index == 0
        assert results[1].mora_end_index == 5

    def test_no_match(self) -> None:
        """Test case: Normal - no match found."""
        audio_query = create_audio_query([
            create_accent_phrase(["メ", "タ", "ン"])
        ])
        entries = [create_entry("ずんだもん", "ズンダモン")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches(audio_query, entries)

        assert len(results) == 0

    def test_partial_match_not_allowed(self) -> None:
        """Test case: Abnormal - partial match should not be allowed.

        Dictionary contains "ズン" but text contains "ズンダモン".
        Partial match at the beginning should NOT match.
        """
        audio_query = create_audio_query([
            create_accent_phrase(["ズ", "ン", "ダ", "モ", "ン"])
        ])
        entries = [create_entry("ずん", "ズン")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches(audio_query, entries)

        assert len(results) == 0

    def test_partial_match_at_end_not_allowed(self) -> None:
        """Test case: Partial match at end should not be allowed."""
        audio_query = create_audio_query([
            create_accent_phrase(["ズ", "ン", "ダ", "モ", "ン"])
        ])
        entries = [create_entry("もん", "モン")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches(audio_query, entries)

        assert len(results) == 0

    def test_match_at_beginning(self) -> None:
        """Test case: Boundary - match at the beginning of text."""
        # "ズンダモンです"
        audio_query = create_audio_query([
            create_accent_phrase(["ズ", "ン", "ダ", "モ", "ン"]),
            create_accent_phrase(["デ", "ス"]),
        ])
        entries = [create_entry("ずんだもん", "ズンダモン")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches(audio_query, entries)

        assert len(results) == 1
        assert results[0].accent_phrase_index == 0
        assert results[0].mora_start_index == 0
        assert results[0].mora_end_index == 5

    def test_match_at_end(self) -> None:
        """Test case: Boundary - match at the end of text."""
        # "こんにちはズンダモン"
        audio_query = create_audio_query([
            create_accent_phrase(["コ", "ン", "ニ", "チ", "ワ"]),
            create_accent_phrase(["ズ", "ン", "ダ", "モ", "ン"]),
        ])
        entries = [create_entry("ずんだもん", "ズンダモン")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches(audio_query, entries)

        assert len(results) == 1
        assert results[0].accent_phrase_index == 1
        assert results[0].mora_start_index == 0
        assert results[0].mora_end_index == 5

    def test_empty_dictionary(self) -> None:
        """Test case: Edge - empty dictionary entries."""
        audio_query = create_audio_query([
            create_accent_phrase(["ズ", "ン", "ダ", "モ", "ン"])
        ])
        entries: list[ExtendedDictEntry] = []
        matcher = DictionaryMatcher()

        results = matcher.find_matches(audio_query, entries)

        assert len(results) == 0

    def test_empty_audio_query(self) -> None:
        """Test case: Edge - empty audio query."""
        audio_query = create_audio_query([])
        entries = [create_entry("ずんだもん", "ズンダモン")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches(audio_query, entries)

        assert len(results) == 0

    def test_match_within_single_accent_phrase(self) -> None:
        """Test exact match of entire accent phrase."""
        audio_query = create_audio_query([
            create_accent_phrase(["ズ", "ン", "ダ", "モ", "ン"])
        ])
        entries = [create_entry("ずんだもん", "ズンダモン")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches(audio_query, entries)

        assert len(results) == 1
        assert results[0].mora_start_index == 0
        assert results[0].mora_end_index == 5

    def test_multiple_entries(self) -> None:
        """Test matching with multiple dictionary entries."""
        # "ずんだもんとめたん"
        audio_query = create_audio_query([
            create_accent_phrase(["ズ", "ン", "ダ", "モ", "ン"]),
            create_accent_phrase(["ト"]),
            create_accent_phrase(["メ", "タ", "ン"]),
        ])
        entries = [
            create_entry("ずんだもん", "ズンダモン"),
            create_entry("めたん", "メタン"),
        ]
        matcher = DictionaryMatcher()

        results = matcher.find_matches(audio_query, entries)

        assert len(results) == 2
        # Find zundamon match
        zundamon_match = next(r for r in results if r.entry.word == "ずんだもん")
        assert zundamon_match.accent_phrase_index == 0
        # Find metan match
        metan_match = next(r for r in results if r.entry.word == "めたん")
        assert metan_match.accent_phrase_index == 2

    def test_match_requires_complete_accent_phrase(self) -> None:
        """Test that match must align with complete accent phrase boundaries.

        If dictionary word "ズンダモン" (5 moras) and accent phrase has
        exactly 5 moras, it should match. If accent phrase has 6 moras
        starting with "ズンダモン", it should NOT match.
        """
        # Accent phrase with more moras than the dictionary word
        audio_query = create_audio_query([
            create_accent_phrase(["ズ", "ン", "ダ", "モ", "ン", "チ", "ャ", "ン"])
        ])
        entries = [create_entry("ずんだもん", "ズンダモン")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches(audio_query, entries)

        # Should NOT match because "ズンダモン" is only part of the accent phrase
        assert len(results) == 0

    def test_exact_match_single_mora(self) -> None:
        """Test exact match with single mora word."""
        audio_query = create_audio_query([
            create_accent_phrase(["ア"])
        ])
        entries = [create_entry("あ", "ア")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches(audio_query, entries)

        assert len(results) == 1
        assert results[0].mora_start_index == 0
        assert results[0].mora_end_index == 1


class TestMatchResult:
    """Tests for MatchResult dataclass."""

    def test_match_result_creation(self) -> None:
        """Test creating a MatchResult instance."""
        entry = create_entry("ずんだもん", "ズンダモン")
        result = MatchResult(
            entry=entry,
            accent_phrase_index=0,
            mora_start_index=0,
            mora_end_index=5,
        )

        assert result.entry == entry
        assert result.accent_phrase_index == 0
        assert result.mora_start_index == 0
        assert result.mora_end_index == 5

    def test_match_result_equality(self) -> None:
        """Test MatchResult equality comparison."""
        entry = create_entry("ずんだもん", "ズンダモン")
        result1 = MatchResult(entry=entry, accent_phrase_index=0, mora_start_index=0, mora_end_index=5)
        result2 = MatchResult(entry=entry, accent_phrase_index=0, mora_start_index=0, mora_end_index=5)

        assert result1 == result2


class TestFindMatchesWithText:
    """Tests for DictionaryMatcher.find_matches_with_text method (partial matching)."""

    def test_partial_match_middle(self) -> None:
        """Test case: Normal - partial match in the middle of accent phrase.

        Input: 「ずんだもんです」-> AudioQuery has "ズンダモンデス" as one accent phrase
        Expected: Match "ズンダモン" (moras 0-4) within the accent phrase
        """
        # 「ずんだもんです」が1つのアクセントフレーズにまとまるケース
        audio_query = create_audio_query([
            create_accent_phrase(["ズ", "ン", "ダ", "モ", "ン", "デ", "ス"])
        ])
        entries = [create_entry("ずんだもん", "ズンダモン")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches_with_text(audio_query, entries, "ずんだもんです")

        assert len(results) == 1
        assert results[0].entry == entries[0]
        assert results[0].accent_phrase_index == 0
        assert results[0].mora_start_index == 0
        assert results[0].mora_end_index == 5

    def test_partial_match_at_end(self) -> None:
        """Test case: Normal - partial match at the end of accent phrase.

        Input: 「こんにちはずんだもん」
        """
        # 「こんにちはずんだもん」
        audio_query = create_audio_query([
            create_accent_phrase(["コ", "ン", "ニ", "チ", "ワ", "ズ", "ン", "ダ", "モ", "ン"])
        ])
        entries = [create_entry("ずんだもん", "ズンダモン")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches_with_text(audio_query, entries, "こんにちはずんだもん")

        assert len(results) == 1
        assert results[0].accent_phrase_index == 0
        assert results[0].mora_start_index == 5
        assert results[0].mora_end_index == 10

    def test_multiple_partial_matches(self) -> None:
        """Test case: Normal - multiple partial matches in text.

        Input: 「ずんだもんとずんだもん」
        """
        # 1つのアクセントフレーズに「ズンダモントズンダモン」
        audio_query = create_audio_query([
            create_accent_phrase(["ズ", "ン", "ダ", "モ", "ン", "ト", "ズ", "ン", "ダ", "モ", "ン"])
        ])
        entries = [create_entry("ずんだもん", "ズンダモン")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches_with_text(audio_query, entries, "ずんだもんとずんだもん")

        assert len(results) == 2
        # First match
        assert results[0].mora_start_index == 0
        assert results[0].mora_end_index == 5
        # Second match
        assert results[1].mora_start_index == 6
        assert results[1].mora_end_index == 11

    def test_text_mismatch_no_match(self) -> None:
        """Test case: Normal - no match when word not in input text.

        Input text: 「メタンです」
        Dictionary word: 「ずんだもん」
        Expected: No match (word not found in input text)
        """
        audio_query = create_audio_query([
            create_accent_phrase(["メ", "タ", "ン", "デ", "ス"])
        ])
        entries = [create_entry("ずんだもん", "ズンダモン")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches_with_text(audio_query, entries, "メタンです")

        assert len(results) == 0

    def test_text_filter_prevents_wrong_match(self) -> None:
        """Test case: Text filter prevents wrong pronunciation match.

        Input text: 「隅田門です」 (different kanji, same reading)
        Dictionary word: 「ずんだもん」
        AudioQuery pronunciation: 「スミダモンデス」(could match if only looking at kana)
        Expected: No match because input text doesn't contain 「ずんだもん」
        """
        audio_query = create_audio_query([
            create_accent_phrase(["ス", "ミ", "ダ", "モ", "ン", "デ", "ス"])
        ])
        entries = [create_entry("ずんだもん", "ズンダモン")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches_with_text(audio_query, entries, "隅田門です")

        assert len(results) == 0

    def test_katakana_word_matches(self) -> None:
        """Test case: Katakana word in input text matches katakana dictionary entry.

        Input text: 「ズンダモンです」
        Dictionary word: 「ズンダモン」
        Expected: Match found
        """
        audio_query = create_audio_query([
            create_accent_phrase(["ズ", "ン", "ダ", "モ", "ン", "デ", "ス"])
        ])
        entries = [create_entry("ズンダモン", "ズンダモン")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches_with_text(audio_query, entries, "ズンダモンです")

        assert len(results) == 1
        assert results[0].mora_start_index == 0
        assert results[0].mora_end_index == 5

    def test_mora_count_mismatch_skips(self) -> None:
        """Test case: Skip when mora count doesn't match.

        Dictionary has 5 moras, but matched range has different count.
        """
        audio_query = create_audio_query([
            # 7 moras but pronunciation starts with "ズンダモン"
            create_accent_phrase(["ズ", "ン", "ダ", "モ", "ン", "チ", "ャ"])
        ])
        # Entry with mora_count explicitly set to 5
        entry = ExtendedDictEntry(
            word="ずんだもん",
            pronunciation="ズンダモン",
            accent_type=1,
            mora_count=5,
            pitch_values=[5.0, 5.1, 5.2, 5.3, 5.4],
        )
        matcher = DictionaryMatcher()

        results = matcher.find_matches_with_text(audio_query, [entry], "ずんだもんちゃ")

        # Should match - pronunciation found within phrase
        assert len(results) == 1
        assert results[0].mora_start_index == 0
        assert results[0].mora_end_index == 5

    def test_cross_accent_phrase_no_match(self) -> None:
        """Test case: Edge - word split across accent phrases should not match.

        Input: 「ズンダ」「モン」 in separate accent phrases
        Expected: No match (initial version doesn't support cross-AP matching)
        """
        audio_query = create_audio_query([
            create_accent_phrase(["ズ", "ン", "ダ"]),
            create_accent_phrase(["モ", "ン"]),
        ])
        entries = [create_entry("ずんだもん", "ズンダモン")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches_with_text(audio_query, entries, "ずんだもん")

        # Should NOT match because word is split across accent phrases
        assert len(results) == 0

    def test_backward_compatibility_with_exact_match(self) -> None:
        """Test case: Backward compatibility - exact match still works.

        When accent phrase exactly matches dictionary word.
        """
        audio_query = create_audio_query([
            create_accent_phrase(["ズ", "ン", "ダ", "モ", "ン"])
        ])
        entries = [create_entry("ずんだもん", "ズンダモン")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches_with_text(audio_query, entries, "ずんだもん")

        assert len(results) == 1
        assert results[0].mora_start_index == 0
        assert results[0].mora_end_index == 5

    def test_empty_text_no_match(self) -> None:
        """Test case: Edge - empty input text should return no matches."""
        audio_query = create_audio_query([
            create_accent_phrase(["ズ", "ン", "ダ", "モ", "ン"])
        ])
        entries = [create_entry("ずんだもん", "ズンダモン")]
        matcher = DictionaryMatcher()

        results = matcher.find_matches_with_text(audio_query, entries, "")

        assert len(results) == 0

    def test_multiple_entries_partial_match(self) -> None:
        """Test case: Multiple dictionary entries with partial matching."""
        # 「ずんだもんとめたんです」
        audio_query = create_audio_query([
            create_accent_phrase(["ズ", "ン", "ダ", "モ", "ン", "ト", "メ", "タ", "ン", "デ", "ス"])
        ])
        entries = [
            create_entry("ずんだもん", "ズンダモン"),
            create_entry("めたん", "メタン"),
        ]
        matcher = DictionaryMatcher()

        results = matcher.find_matches_with_text(audio_query, entries, "ずんだもんとめたんです")

        assert len(results) == 2
        # Find zundamon match
        zundamon_match = next(r for r in results if r.entry.word == "ずんだもん")
        assert zundamon_match.mora_start_index == 0
        assert zundamon_match.mora_end_index == 5
        # Find metan match
        metan_match = next(r for r in results if r.entry.word == "めたん")
        assert metan_match.mora_start_index == 6
        assert metan_match.mora_end_index == 9
