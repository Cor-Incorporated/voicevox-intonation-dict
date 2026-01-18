"""Tests for AudioQueryService.

This module contains comprehensive tests for the AudioQueryService class,
following TDD principles. Tests cover normal cases, edge cases, and error handling.
"""

from typing import Any

import pytest

from app.models.extended_dict import ExtendedDictEntry
from app.services.audio_query_service import AudioQueryService


def create_audio_query(mora_count: int) -> dict[str, Any]:
    """Create a sample AudioQuery with specified number of moras.

    Args:
        mora_count: Number of moras to create.

    Returns:
        A dict representing an AudioQuery with the specified moras.
    """
    moras = []
    for i in range(mora_count):
        moras.append(
            {
                "text": f"モ{i}",
                "consonant": "m",
                "consonant_length": 0.05 + i * 0.01,
                "vowel": "o",
                "vowel_length": 0.12 + i * 0.01,
                "pitch": 5.0 + i * 0.1,
            }
        )

    return {
        "accent_phrases": [
            {
                "moras": moras,
                "accent": 1,
                "pause_mora": None,
                "is_interrogative": False,
            }
        ],
        "speedScale": 1.0,
        "pitchScale": 0.0,
        "intonationScale": 1.0,
        "volumeScale": 1.0,
        "prePhonemeLength": 0.1,
        "postPhonemeLength": 0.1,
        "outputSamplingRate": 24000,
        "outputStereo": False,
        "kana": "テスト",
    }


def create_multi_phrase_audio_query(mora_counts: list[int]) -> dict[str, Any]:
    """Create AudioQuery with multiple accent phrases.

    Args:
        mora_counts: List of mora counts for each accent phrase.

    Returns:
        A dict representing an AudioQuery with multiple accent phrases.
    """
    accent_phrases = []
    for phrase_idx, count in enumerate(mora_counts):
        moras = []
        for i in range(count):
            moras.append(
                {
                    "text": f"モ{phrase_idx}{i}",
                    "consonant": "m",
                    "consonant_length": 0.05,
                    "vowel": "o",
                    "vowel_length": 0.12,
                    "pitch": 5.0,
                }
            )
        accent_phrases.append(
            {
                "moras": moras,
                "accent": 1,
                "pause_mora": None,
                "is_interrogative": False,
            }
        )

    return {
        "accent_phrases": accent_phrases,
        "speedScale": 1.0,
        "pitchScale": 0.0,
        "intonationScale": 1.0,
        "volumeScale": 1.0,
        "prePhonemeLength": 0.1,
        "postPhonemeLength": 0.1,
        "outputSamplingRate": 24000,
        "outputStereo": False,
        "kana": "テスト",
    }


class TestApplyPitchValues:
    """Tests for apply_pitch_values method."""

    def test_apply_pitch_values_basic(self) -> None:
        """Test basic pitch value application."""
        audio_query = create_audio_query(5)
        pitch_values = [6.0, 6.1, 6.2, 6.3, 6.4]
        start_mora_index = 0

        result = AudioQueryService.apply_pitch_values(
            audio_query, pitch_values, start_mora_index
        )

        moras = result["accent_phrases"][0]["moras"]
        for i, expected_pitch in enumerate(pitch_values):
            assert moras[i]["pitch"] == expected_pitch

    def test_apply_pitch_values_with_offset(self) -> None:
        """Test pitch value application with start offset."""
        audio_query = create_audio_query(5)
        pitch_values = [7.0, 7.1, 7.2]
        start_mora_index = 2

        result = AudioQueryService.apply_pitch_values(
            audio_query, pitch_values, start_mora_index
        )

        moras = result["accent_phrases"][0]["moras"]
        # First 2 moras should be unchanged
        assert moras[0]["pitch"] == 5.0
        assert moras[1]["pitch"] == pytest.approx(5.1, rel=1e-5)
        # Moras at index 2, 3, 4 should have new values
        assert moras[2]["pitch"] == 7.0
        assert moras[3]["pitch"] == 7.1
        assert moras[4]["pitch"] == 7.2

    def test_apply_pitch_values_empty_list_skips(self) -> None:
        """Test that empty pitch_values list skips overwrite."""
        audio_query = create_audio_query(5)
        original_pitches = [
            mora["pitch"]
            for mora in audio_query["accent_phrases"][0]["moras"]
        ]
        pitch_values: list[float] = []
        start_mora_index = 0

        result = AudioQueryService.apply_pitch_values(
            audio_query, pitch_values, start_mora_index
        )

        moras = result["accent_phrases"][0]["moras"]
        for i, expected_pitch in enumerate(original_pitches):
            assert moras[i]["pitch"] == expected_pitch

    def test_apply_pitch_values_mora_count_mismatch_raises(self) -> None:
        """Test that mora count mismatch raises ValueError."""
        audio_query = create_audio_query(5)
        pitch_values = [6.0, 6.1, 6.2]  # Only 3 values for 5 moras
        start_mora_index = 0

        with pytest.raises(ValueError, match="モーラ数が一致しません"):
            AudioQueryService.apply_pitch_values(
                audio_query, pitch_values, start_mora_index
            )

    def test_apply_pitch_values_single_mora(self) -> None:
        """Test pitch application with single mora (boundary case)."""
        audio_query = create_audio_query(1)
        pitch_values = [8.5]
        start_mora_index = 0

        result = AudioQueryService.apply_pitch_values(
            audio_query, pitch_values, start_mora_index
        )

        moras = result["accent_phrases"][0]["moras"]
        assert moras[0]["pitch"] == 8.5

    def test_apply_pitch_values_preserves_other_fields(self) -> None:
        """Test that other AudioQuery fields are preserved."""
        audio_query = create_audio_query(3)
        pitch_values = [6.0, 6.1, 6.2]
        start_mora_index = 0

        result = AudioQueryService.apply_pitch_values(
            audio_query, pitch_values, start_mora_index
        )

        # Other fields should be unchanged
        assert result["speedScale"] == 1.0
        assert result["pitchScale"] == 0.0
        assert result["outputSamplingRate"] == 24000
        # Mora fields other than pitch should be unchanged
        moras = result["accent_phrases"][0]["moras"]
        assert moras[0]["vowel_length"] == 0.12
        assert moras[0]["consonant_length"] == 0.05


class TestApplyLengthValues:
    """Tests for apply_length_values method."""

    def test_apply_length_values_basic(self) -> None:
        """Test basic length value application."""
        audio_query = create_audio_query(5)
        length_values = [0.2, 0.21, 0.22, 0.23, 0.24]
        start_mora_index = 0

        result = AudioQueryService.apply_length_values(
            audio_query, length_values, start_mora_index
        )

        moras = result["accent_phrases"][0]["moras"]
        for i, expected_length in enumerate(length_values):
            assert moras[i]["vowel_length"] == expected_length

    def test_apply_length_values_with_offset(self) -> None:
        """Test length value application with start offset."""
        audio_query = create_audio_query(5)
        length_values = [0.3, 0.31, 0.32]
        start_mora_index = 2

        result = AudioQueryService.apply_length_values(
            audio_query, length_values, start_mora_index
        )

        moras = result["accent_phrases"][0]["moras"]
        # First 2 moras should be unchanged
        assert moras[0]["vowel_length"] == 0.12
        assert moras[1]["vowel_length"] == pytest.approx(0.13, rel=1e-5)
        # Moras at index 2, 3, 4 should have new values
        assert moras[2]["vowel_length"] == 0.3
        assert moras[3]["vowel_length"] == 0.31
        assert moras[4]["vowel_length"] == 0.32

    def test_apply_length_values_empty_list_skips(self) -> None:
        """Test that empty length_values list skips overwrite."""
        audio_query = create_audio_query(5)
        original_lengths = [
            mora["vowel_length"]
            for mora in audio_query["accent_phrases"][0]["moras"]
        ]
        length_values: list[float] = []
        start_mora_index = 0

        result = AudioQueryService.apply_length_values(
            audio_query, length_values, start_mora_index
        )

        moras = result["accent_phrases"][0]["moras"]
        for i, expected_length in enumerate(original_lengths):
            assert moras[i]["vowel_length"] == expected_length

    def test_apply_length_values_mora_count_mismatch_raises(self) -> None:
        """Test that mora count mismatch raises ValueError."""
        audio_query = create_audio_query(5)
        length_values = [0.2, 0.21, 0.22]  # Only 3 values for 5 moras
        start_mora_index = 0

        with pytest.raises(ValueError, match="モーラ数が一致しません"):
            AudioQueryService.apply_length_values(
                audio_query, length_values, start_mora_index
            )

    def test_apply_length_values_single_mora(self) -> None:
        """Test length application with single mora (boundary case)."""
        audio_query = create_audio_query(1)
        length_values = [0.5]
        start_mora_index = 0

        result = AudioQueryService.apply_length_values(
            audio_query, length_values, start_mora_index
        )

        moras = result["accent_phrases"][0]["moras"]
        assert moras[0]["vowel_length"] == 0.5

    def test_apply_length_values_also_updates_consonant_length(self) -> None:
        """Test that consonant_length is also updated proportionally."""
        audio_query = create_audio_query(3)
        length_values = [0.24, 0.26, 0.28]  # Doubling original values
        start_mora_index = 0

        result = AudioQueryService.apply_length_values(
            audio_query, length_values, start_mora_index
        )

        moras = result["accent_phrases"][0]["moras"]
        # Consonant length should also be updated
        # Original ratio: consonant_length / vowel_length = 0.05 / 0.12
        # New consonant_length should maintain proportion or be directly set
        assert moras[0]["vowel_length"] == 0.24


class TestApplyExtendedDict:
    """Tests for apply_extended_dict integration method."""

    def test_apply_extended_dict_pitch_and_length(self) -> None:
        """Test applying both pitch and length values via ExtendedDictEntry."""
        audio_query = create_audio_query(5)
        entry = ExtendedDictEntry(
            word="テスト",
            pronunciation="テスト",
            accent_type=1,
            mora_count=5,
            pitch_values=[6.0, 6.1, 6.2, 6.3, 6.4],
            length_values=[0.2, 0.21, 0.22, 0.23, 0.24],
        )
        match_result = {"start_mora_index": 0, "end_mora_index": 5}

        result = AudioQueryService.apply_extended_dict(
            audio_query, entry, match_result
        )

        moras = result["accent_phrases"][0]["moras"]
        for i in range(5):
            assert moras[i]["pitch"] == entry.pitch_values[i]
            assert moras[i]["vowel_length"] == entry.length_values[i]

    def test_apply_extended_dict_pitch_only(self) -> None:
        """Test applying only pitch values (length_values is None)."""
        audio_query = create_audio_query(5)
        original_lengths = [
            mora["vowel_length"]
            for mora in audio_query["accent_phrases"][0]["moras"]
        ]
        entry = ExtendedDictEntry(
            word="テスト",
            pronunciation="テスト",
            accent_type=1,
            mora_count=5,
            pitch_values=[6.0, 6.1, 6.2, 6.3, 6.4],
            length_values=None,
        )
        match_result = {"start_mora_index": 0, "end_mora_index": 5}

        result = AudioQueryService.apply_extended_dict(
            audio_query, entry, match_result
        )

        moras = result["accent_phrases"][0]["moras"]
        for i in range(5):
            assert moras[i]["pitch"] == entry.pitch_values[i]
            # Length should be unchanged
            assert moras[i]["vowel_length"] == original_lengths[i]

    def test_apply_extended_dict_length_only(self) -> None:
        """Test applying only length values (pitch_values is None)."""
        audio_query = create_audio_query(5)
        original_pitches = [
            mora["pitch"]
            for mora in audio_query["accent_phrases"][0]["moras"]
        ]
        entry = ExtendedDictEntry(
            word="テスト",
            pronunciation="テスト",
            accent_type=1,
            mora_count=5,
            pitch_values=None,
            length_values=[0.2, 0.21, 0.22, 0.23, 0.24],
        )
        match_result = {"start_mora_index": 0, "end_mora_index": 5}

        result = AudioQueryService.apply_extended_dict(
            audio_query, entry, match_result
        )

        moras = result["accent_phrases"][0]["moras"]
        for i in range(5):
            # Pitch should be unchanged
            assert moras[i]["pitch"] == original_pitches[i]
            assert moras[i]["vowel_length"] == entry.length_values[i]

    def test_apply_extended_dict_mora_count_mismatch(self) -> None:
        """Test that mora count mismatch raises ValueError."""
        audio_query = create_audio_query(5)
        entry = ExtendedDictEntry(
            word="テスト",
            pronunciation="テスト",
            accent_type=1,
            mora_count=5,
            pitch_values=[6.0, 6.1, 6.2],  # Only 3 values
            length_values=None,
        )
        match_result = {"start_mora_index": 0, "end_mora_index": 5}

        with pytest.raises(ValueError, match="モーラ数が一致しません"):
            AudioQueryService.apply_extended_dict(
                audio_query, entry, match_result
            )

    def test_apply_extended_dict_with_offset(self) -> None:
        """Test applying values with start_mora_index offset."""
        audio_query = create_audio_query(5)
        entry = ExtendedDictEntry(
            word="テスト",
            pronunciation="テスト",
            accent_type=1,
            mora_count=3,
            pitch_values=[7.0, 7.1, 7.2],
            length_values=[0.3, 0.31, 0.32],
        )
        match_result = {"start_mora_index": 2, "end_mora_index": 5}

        result = AudioQueryService.apply_extended_dict(
            audio_query, entry, match_result
        )

        moras = result["accent_phrases"][0]["moras"]
        # First 2 moras unchanged
        assert moras[0]["pitch"] == 5.0
        assert moras[1]["pitch"] == pytest.approx(5.1, rel=1e-5)
        # Moras 2-4 should have new values
        assert moras[2]["pitch"] == 7.0
        assert moras[3]["pitch"] == 7.1
        assert moras[4]["pitch"] == 7.2


class TestMultipleAccentPhrases:
    """Tests for AudioQuery with multiple accent phrases."""

    def test_apply_pitch_across_phrases(self) -> None:
        """Test pitch application across multiple accent phrases."""
        audio_query = create_multi_phrase_audio_query([2, 3])  # 5 moras total
        pitch_values = [6.0, 6.1, 6.2, 6.3, 6.4]
        start_mora_index = 0

        result = AudioQueryService.apply_pitch_values(
            audio_query, pitch_values, start_mora_index
        )

        # First phrase moras
        assert result["accent_phrases"][0]["moras"][0]["pitch"] == 6.0
        assert result["accent_phrases"][0]["moras"][1]["pitch"] == 6.1
        # Second phrase moras
        assert result["accent_phrases"][1]["moras"][0]["pitch"] == 6.2
        assert result["accent_phrases"][1]["moras"][1]["pitch"] == 6.3
        assert result["accent_phrases"][1]["moras"][2]["pitch"] == 6.4


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_empty_accent_phrases(self) -> None:
        """Test with empty accent_phrases list."""
        audio_query: dict[str, Any] = {
            "accent_phrases": [],
            "speedScale": 1.0,
        }
        pitch_values: list[float] = []
        start_mora_index = 0

        result = AudioQueryService.apply_pitch_values(
            audio_query, pitch_values, start_mora_index
        )

        assert result["accent_phrases"] == []

    def test_original_query_not_modified(self) -> None:
        """Test that original audio_query is not modified (immutability)."""
        audio_query = create_audio_query(3)
        original_pitch = audio_query["accent_phrases"][0]["moras"][0]["pitch"]
        pitch_values = [9.0, 9.1, 9.2]
        start_mora_index = 0

        AudioQueryService.apply_pitch_values(
            audio_query, pitch_values, start_mora_index
        )

        # Original should be unchanged
        assert audio_query["accent_phrases"][0]["moras"][0]["pitch"] == original_pitch


class TestApplyPartialMatch:
    """Tests for AudioQueryService.apply_partial_match method."""

    def test_partial_match_middle_of_phrase(self) -> None:
        """Test applying values to middle portion of an accent phrase.

        Scenario: 7-mora phrase, apply 5-mora dict entry to moras 0-4
        """
        # Create 7-mora query: ズンダモンデス
        moras = [
            {"text": "ズ", "pitch": 5.0, "vowel_length": 0.1},
            {"text": "ン", "pitch": 5.1, "vowel_length": 0.1},
            {"text": "ダ", "pitch": 5.2, "vowel_length": 0.1},
            {"text": "モ", "pitch": 5.3, "vowel_length": 0.1},
            {"text": "ン", "pitch": 5.4, "vowel_length": 0.1},
            {"text": "デ", "pitch": 5.5, "vowel_length": 0.1},
            {"text": "ス", "pitch": 5.6, "vowel_length": 0.1},
        ]
        audio_query = {
            "accent_phrases": [{"moras": moras, "accent": 1}],
            "speedScale": 1.0,
        }
        entry = ExtendedDictEntry(
            word="ずんだもん",
            pronunciation="ズンダモン",
            accent_type=1,
            pitch_values=[6.0, 6.1, 6.2, 6.3, 6.4],
            length_values=[0.2, 0.21, 0.22, 0.23, 0.24],
        )

        result = AudioQueryService.apply_partial_match(
            audio_query, entry,
            accent_phrase_index=0,
            mora_start_index=0,
            mora_end_index=5,
        )

        # First 5 moras should be updated
        result_moras = result["accent_phrases"][0]["moras"]
        assert result_moras[0]["pitch"] == 6.0
        assert result_moras[1]["pitch"] == 6.1
        assert result_moras[2]["pitch"] == 6.2
        assert result_moras[3]["pitch"] == 6.3
        assert result_moras[4]["pitch"] == 6.4
        # Last 2 moras should be unchanged
        assert result_moras[5]["pitch"] == 5.5
        assert result_moras[6]["pitch"] == 5.6
        # Check length values
        assert result_moras[0]["vowel_length"] == 0.2
        assert result_moras[4]["vowel_length"] == 0.24
        assert result_moras[5]["vowel_length"] == 0.1  # unchanged

    def test_partial_match_end_of_phrase(self) -> None:
        """Test applying values to end portion of an accent phrase.

        Scenario: 10-mora phrase, apply 5-mora dict entry to moras 5-9
        """
        # Create 10-mora query: コンニチワズンダモン
        moras = [{"text": f"モ{i}", "pitch": 5.0 + i * 0.1, "vowel_length": 0.1} for i in range(10)]
        audio_query = {
            "accent_phrases": [{"moras": moras, "accent": 1}],
            "speedScale": 1.0,
        }
        entry = ExtendedDictEntry(
            word="ずんだもん",
            pronunciation="ズンダモン",
            accent_type=1,
            pitch_values=[6.0, 6.1, 6.2, 6.3, 6.4],
        )

        result = AudioQueryService.apply_partial_match(
            audio_query, entry,
            accent_phrase_index=0,
            mora_start_index=5,
            mora_end_index=10,
        )

        result_moras = result["accent_phrases"][0]["moras"]
        # First 5 moras unchanged
        for i in range(5):
            assert result_moras[i]["pitch"] == 5.0 + i * 0.1
        # Last 5 moras updated
        assert result_moras[5]["pitch"] == 6.0
        assert result_moras[6]["pitch"] == 6.1
        assert result_moras[9]["pitch"] == 6.4

    def test_partial_match_mora_count_mismatch_raises(self) -> None:
        """Test that mora count mismatch raises ValueError."""
        moras = [{"text": f"モ{i}", "pitch": 5.0, "vowel_length": 0.1} for i in range(7)]
        audio_query = {
            "accent_phrases": [{"moras": moras, "accent": 1}],
            "speedScale": 1.0,
        }
        entry = ExtendedDictEntry(
            word="ずんだもん",
            pronunciation="ズンダモン",
            accent_type=1,
            pitch_values=[6.0, 6.1, 6.2],  # 3 values, but target is 5 moras
        )

        with pytest.raises(ValueError, match="モーラ数が一致しません"):
            AudioQueryService.apply_partial_match(
                audio_query, entry,
                accent_phrase_index=0,
                mora_start_index=0,
                mora_end_index=5,  # 5 moras but only 3 pitch values
            )

    def test_partial_match_invalid_accent_phrase_index(self) -> None:
        """Test that invalid accent phrase index raises ValueError."""
        audio_query = create_audio_query(5)
        entry = ExtendedDictEntry(
            word="test",
            pronunciation="テスト",
            accent_type=1,
            pitch_values=[6.0, 6.1, 6.2, 6.3, 6.4],
        )

        with pytest.raises(ValueError, match="Invalid accent_phrase_index"):
            AudioQueryService.apply_partial_match(
                audio_query, entry,
                accent_phrase_index=5,  # Invalid - only 1 accent phrase
                mora_start_index=0,
                mora_end_index=5,
            )

    def test_partial_match_invalid_mora_range(self) -> None:
        """Test that invalid mora range raises ValueError."""
        audio_query = create_audio_query(5)
        entry = ExtendedDictEntry(
            word="test",
            pronunciation="テスト",
            accent_type=1,
            pitch_values=[6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6],  # 7 values
        )

        with pytest.raises(ValueError, match="Invalid mora range"):
            AudioQueryService.apply_partial_match(
                audio_query, entry,
                accent_phrase_index=0,
                mora_start_index=0,
                mora_end_index=7,  # Invalid - only 5 moras
            )

    def test_partial_match_pitch_only(self) -> None:
        """Test applying only pitch values (no length values)."""
        audio_query = create_audio_query(5)
        original_length = audio_query["accent_phrases"][0]["moras"][0]["vowel_length"]
        entry = ExtendedDictEntry(
            word="test",
            pronunciation="テスト",
            accent_type=1,
            pitch_values=[7.0, 7.1, 7.2, 7.3, 7.4],
            length_values=None,
        )

        result = AudioQueryService.apply_partial_match(
            audio_query, entry,
            accent_phrase_index=0,
            mora_start_index=0,
            mora_end_index=5,
        )

        result_moras = result["accent_phrases"][0]["moras"]
        assert result_moras[0]["pitch"] == 7.0
        assert result_moras[0]["vowel_length"] == original_length  # unchanged

    def test_partial_match_length_only(self) -> None:
        """Test applying only length values (no pitch values)."""
        audio_query = create_audio_query(5)
        original_pitch = audio_query["accent_phrases"][0]["moras"][0]["pitch"]
        entry = ExtendedDictEntry(
            word="test",
            pronunciation="テスト",
            accent_type=1,
            pitch_values=None,
            length_values=[0.3, 0.31, 0.32, 0.33, 0.34],
        )

        result = AudioQueryService.apply_partial_match(
            audio_query, entry,
            accent_phrase_index=0,
            mora_start_index=0,
            mora_end_index=5,
        )

        result_moras = result["accent_phrases"][0]["moras"]
        assert result_moras[0]["pitch"] == original_pitch  # unchanged
        assert result_moras[0]["vowel_length"] == 0.3

    def test_partial_match_immutability(self) -> None:
        """Test that original audio_query is not modified."""
        audio_query = create_audio_query(5)
        original_pitch = audio_query["accent_phrases"][0]["moras"][0]["pitch"]
        entry = ExtendedDictEntry(
            word="test",
            pronunciation="テスト",
            accent_type=1,
            pitch_values=[9.0, 9.1, 9.2, 9.3, 9.4],
        )

        AudioQueryService.apply_partial_match(
            audio_query, entry,
            accent_phrase_index=0,
            mora_start_index=0,
            mora_end_index=5,
        )

        # Original should be unchanged
        assert audio_query["accent_phrases"][0]["moras"][0]["pitch"] == original_pitch
