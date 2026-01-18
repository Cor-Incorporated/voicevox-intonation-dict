"""AudioQuery service for applying extended dictionary values.

This module provides services for modifying AudioQuery objects with
pitch and length values from extended dictionary entries.
"""

import copy
from typing import Any

from app.models.extended_dict import ExtendedDictEntry


class AudioQueryService:
    """Service for applying extended dictionary values to AudioQuery.

    This service provides methods to override pitch and length values
    in an AudioQuery based on extended dictionary entries. It validates
    mora count matches and supports partial application with offsets.
    """

    @staticmethod
    def _get_total_mora_count(audio_query: dict[str, Any]) -> int:
        """Get total mora count from AudioQuery.

        Args:
            audio_query: The AudioQuery dictionary.

        Returns:
            Total number of moras across all accent phrases.
        """
        total = 0
        for phrase in audio_query.get("accent_phrases", []):
            total += len(phrase.get("moras", []))
        return total

    @staticmethod
    def _deep_copy_query(audio_query: dict[str, Any]) -> dict[str, Any]:
        """Create a deep copy of AudioQuery to preserve immutability.

        Args:
            audio_query: The original AudioQuery dictionary.

        Returns:
            A deep copy of the AudioQuery.
        """
        return copy.deepcopy(audio_query)

    @staticmethod
    def apply_pitch_values(
        audio_query: dict[str, Any],
        pitch_values: list[float],
        start_mora_index: int = 0,
    ) -> dict[str, Any]:
        """Apply pitch values to AudioQuery moras.

        Args:
            audio_query: The AudioQuery to modify.
            pitch_values: List of pitch values to apply.
            start_mora_index: Starting mora index for application.

        Returns:
            Modified AudioQuery with updated pitch values.

        Raises:
            ValueError: If mora count does not match pitch_values length
                (when pitch_values is non-empty).
        """
        # Empty list means skip overwrite
        if not pitch_values:
            return AudioQueryService._deep_copy_query(audio_query)

        modified_query = AudioQueryService._deep_copy_query(audio_query)

        # Calculate available moras from start_mora_index
        total_moras = AudioQueryService._get_total_mora_count(modified_query)
        available_moras = total_moras - start_mora_index

        if len(pitch_values) != available_moras:
            raise ValueError(
                f"モーラ数が一致しません: "
                f"pitch_values={len(pitch_values)}, "
                f"available_moras={available_moras}"
            )

        # Apply pitch values
        mora_idx = 0
        value_idx = 0
        for phrase in modified_query.get("accent_phrases", []):
            for mora in phrase.get("moras", []):
                if mora_idx >= start_mora_index and value_idx < len(pitch_values):
                    mora["pitch"] = pitch_values[value_idx]
                    value_idx += 1
                mora_idx += 1

        return modified_query

    @staticmethod
    def apply_length_values(
        audio_query: dict[str, Any],
        length_values: list[float],
        start_mora_index: int = 0,
    ) -> dict[str, Any]:
        """Apply length values to AudioQuery moras.

        This method updates vowel_length values. Consonant_length is
        optionally updated proportionally if needed.

        Args:
            audio_query: The AudioQuery to modify.
            length_values: List of vowel length values to apply.
            start_mora_index: Starting mora index for application.

        Returns:
            Modified AudioQuery with updated length values.

        Raises:
            ValueError: If mora count does not match length_values length
                (when length_values is non-empty).
        """
        # Empty list means skip overwrite
        if not length_values:
            return AudioQueryService._deep_copy_query(audio_query)

        modified_query = AudioQueryService._deep_copy_query(audio_query)

        # Calculate available moras from start_mora_index
        total_moras = AudioQueryService._get_total_mora_count(modified_query)
        available_moras = total_moras - start_mora_index

        if len(length_values) != available_moras:
            raise ValueError(
                f"モーラ数が一致しません: "
                f"length_values={len(length_values)}, "
                f"available_moras={available_moras}"
            )

        # Apply length values
        mora_idx = 0
        value_idx = 0
        for phrase in modified_query.get("accent_phrases", []):
            for mora in phrase.get("moras", []):
                if mora_idx >= start_mora_index and value_idx < len(length_values):
                    mora["vowel_length"] = length_values[value_idx]
                    value_idx += 1
                mora_idx += 1

        return modified_query

    @staticmethod
    def apply_extended_dict(
        audio_query: dict[str, Any],
        entry: ExtendedDictEntry,
        match_result: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply extended dictionary entry to AudioQuery.

        This is the main integration method that applies both pitch and
        length values from an ExtendedDictEntry based on match results.

        Args:
            audio_query: The AudioQuery to modify.
            entry: The ExtendedDictEntry containing pitch/length values.
            match_result: Dictionary containing 'start_mora_index' and
                'end_mora_index' keys indicating where to apply values.

        Returns:
            Modified AudioQuery with updated values.

        Raises:
            ValueError: If mora count does not match values length.
        """
        start_mora_index = match_result.get("start_mora_index", 0)
        result = AudioQueryService._deep_copy_query(audio_query)

        # Apply pitch values if present
        if entry.pitch_values is not None and len(entry.pitch_values) > 0:
            result = AudioQueryService.apply_pitch_values(
                result, entry.pitch_values, start_mora_index
            )

        # Apply length values if present
        if entry.length_values is not None and len(entry.length_values) > 0:
            result = AudioQueryService.apply_length_values(
                result, entry.length_values, start_mora_index
            )

        return result

    @staticmethod
    def apply_partial_match(
        audio_query: dict[str, Any],
        entry: ExtendedDictEntry,
        accent_phrase_index: int,
        mora_start_index: int,
        mora_end_index: int,
    ) -> dict[str, Any]:
        """Apply extended dictionary entry to a specific range of moras.

        This method applies pitch and length values from an ExtendedDictEntry
        to a specific range of moras within a specific accent phrase. Used for
        partial matching where the dictionary word matches a portion of an
        accent phrase.

        Args:
            audio_query: The AudioQuery to modify.
            entry: The ExtendedDictEntry containing pitch/length values.
            accent_phrase_index: Index of the accent phrase to modify.
            mora_start_index: Starting mora index within the accent phrase (inclusive).
            mora_end_index: Ending mora index within the accent phrase (exclusive).

        Returns:
            Modified AudioQuery with updated values in the specified range.

        Raises:
            ValueError: If mora count does not match values length, or if indices are invalid.
        """
        result = AudioQueryService._deep_copy_query(audio_query)

        accent_phrases = result.get("accent_phrases", [])
        if accent_phrase_index >= len(accent_phrases):
            raise ValueError(f"Invalid accent_phrase_index: {accent_phrase_index}")

        moras = accent_phrases[accent_phrase_index].get("moras", [])
        target_mora_count = mora_end_index - mora_start_index

        if mora_start_index < 0 or mora_end_index > len(moras):
            raise ValueError(
                f"Invalid mora range: start={mora_start_index}, end={mora_end_index}, "
                f"available={len(moras)}"
            )

        # Apply pitch values if present
        if entry.pitch_values is not None and len(entry.pitch_values) > 0:
            if len(entry.pitch_values) != target_mora_count:
                raise ValueError(
                    f"モーラ数が一致しません: pitch_values={len(entry.pitch_values)}, "
                    f"target_moras={target_mora_count}"
                )
            for i, pitch in enumerate(entry.pitch_values):
                moras[mora_start_index + i]["pitch"] = pitch

        # Apply length values if present
        if entry.length_values is not None and len(entry.length_values) > 0:
            if len(entry.length_values) != target_mora_count:
                raise ValueError(
                    f"モーラ数が一致しません: length_values={len(entry.length_values)}, "
                    f"target_moras={target_mora_count}"
                )
            for i, length in enumerate(entry.length_values):
                moras[mora_start_index + i]["vowel_length"] = length

        return result
