"""
Dictionary matcher service for finding word matches in AudioQuery.

This module provides functionality to match dictionary entries against
AudioQuery pronunciation data.

Two matching modes are supported:
1. Exact match (find_matches): Dictionary word must match entire accent phrase
2. Partial match with text filter (find_matches_with_text): Dictionary word
   can match a portion of an accent phrase, with input text filtering
"""

from dataclasses import dataclass
from typing import Any

from app.models.extended_dict import ExtendedDictEntry


@dataclass
class MatchResult:
    """Result of a successful dictionary match.

    Attributes:
        entry: The matched dictionary entry containing word and pronunciation.
        accent_phrase_index: Index of the accent phrase within AudioQuery.accent_phrases.
        mora_start_index: Starting mora index within the accent phrase (inclusive).
        mora_end_index: Ending mora index within the accent phrase (exclusive).
    """

    entry: ExtendedDictEntry
    accent_phrase_index: int
    mora_start_index: int
    mora_end_index: int


class DictionaryMatcher:
    """Matcher for finding dictionary entries in AudioQuery data.

    This class provides methods to extract pronunciation from AudioQuery
    and find matches against dictionary entries.

    Two matching modes:
    1. find_matches(): Exact match - dictionary word must match entire accent phrase
    2. find_matches_with_text(): Partial match with text filter - dictionary word
       can match a portion of an accent phrase, filtered by input text

    Words that span multiple accent phrases are not matched in either mode.
    """

    def extract_pronunciation(self, audio_query: dict[str, Any]) -> str:
        """Extract concatenated pronunciation from AudioQuery.

        Extracts all mora texts from all accent phrases and concatenates
        them into a single katakana string. Pause moras are not included.

        Args:
            audio_query: AudioQuery dictionary containing accent_phrases.

        Returns:
            Concatenated katakana pronunciation string.

        Example:
            >>> matcher = DictionaryMatcher()
            >>> query = {
            ...     "accent_phrases": [
            ...         {"moras": [{"text": "コ"}, {"text": "ン"}], "accent": 1}
            ...     ]
            ... }
            >>> matcher.extract_pronunciation(query)
            'コン'
        """
        pronunciation_parts: list[str] = []

        for accent_phrase in audio_query.get("accent_phrases", []):
            for mora in accent_phrase.get("moras", []):
                text = mora.get("text", "")
                if text:
                    pronunciation_parts.append(text)

        return "".join(pronunciation_parts)

    def find_matches(
        self,
        audio_query: dict[str, Any],
        entries: list[ExtendedDictEntry],
    ) -> list[MatchResult]:
        """Find all dictionary entries that match in the AudioQuery.

        Searches for exact matches of dictionary entry pronunciations
        within the AudioQuery's accent phrases. A match occurs when
        an accent phrase's concatenated mora texts exactly equals
        a dictionary entry's pronunciation.

        Only complete accent phrase matches are considered valid.
        Partial matches (where dictionary word is a substring of
        the accent phrase or vice versa) are not allowed.

        Args:
            audio_query: AudioQuery dictionary containing accent_phrases.
            entries: List of dictionary entries to match against.

        Returns:
            List of MatchResult objects for all found matches.
            Empty list if no matches are found.

        Example:
            >>> matcher = DictionaryMatcher()
            >>> query = {
            ...     "accent_phrases": [
            ...         {"moras": [{"text": "ズ"}, {"text": "ン"}, {"text": "ダ"},
            ...                    {"text": "モ"}, {"text": "ン"}], "accent": 3}
            ...     ]
            ... }
            >>> entries = [ExtendedDictEntry(word="ずんだもん",
            ...                               pronunciation="ズンダモン",
            ...                               accent_type=3)]
            >>> results = matcher.find_matches(query, entries)
            >>> len(results)
            1
        """
        if not entries:
            return []

        accent_phrases = audio_query.get("accent_phrases", [])
        if not accent_phrases:
            return []

        # Build a mapping of pronunciation -> entry for faster lookup
        pronunciation_to_entries: dict[str, list[ExtendedDictEntry]] = {}
        for entry in entries:
            pronunciation = entry.pronunciation
            if pronunciation not in pronunciation_to_entries:
                pronunciation_to_entries[pronunciation] = []
            pronunciation_to_entries[pronunciation].append(entry)

        results: list[MatchResult] = []

        # Check each accent phrase for exact matches
        for phrase_index, accent_phrase in enumerate(accent_phrases):
            moras = accent_phrase.get("moras", [])
            if not moras:
                continue

            # Build the pronunciation for this accent phrase
            phrase_pronunciation = "".join(
                mora.get("text", "") for mora in moras
            )

            # Check if this pronunciation exactly matches any dictionary entry
            if phrase_pronunciation in pronunciation_to_entries:
                for entry in pronunciation_to_entries[phrase_pronunciation]:
                    results.append(
                        MatchResult(
                            entry=entry,
                            accent_phrase_index=phrase_index,
                            mora_start_index=0,
                            mora_end_index=len(moras),
                        )
                    )

        return results

    def find_matches_with_text(
        self,
        audio_query: dict[str, Any],
        entries: list[ExtendedDictEntry],
        input_text: str,
    ) -> list[MatchResult]:
        """Find dictionary entries using partial matching with text filtering.

        This method supports partial matching within accent phrases, where a
        dictionary word can match a substring of an accent phrase's pronunciation.
        Input text filtering is used to prevent false matches - only entries
        whose 'word' field appears in the input text are considered.

        Algorithm:
        1. Filter entries: Only consider entries where entry.word is in input_text
        2. For each accent phrase, search for entry.pronunciation as substring
        3. If found, record the match with exact mora indices

        Words split across accent phrase boundaries are NOT matched.

        Args:
            audio_query: AudioQuery dictionary containing accent_phrases.
            entries: List of dictionary entries to match against.
            input_text: Original input text for filtering (prevents false matches).

        Returns:
            List of MatchResult objects for all found matches.
            Empty list if no matches are found.

        Example:
            >>> matcher = DictionaryMatcher()
            >>> query = {
            ...     "accent_phrases": [
            ...         {"moras": [{"text": "ズ"}, {"text": "ン"}, {"text": "ダ"},
            ...                    {"text": "モ"}, {"text": "ン"}, {"text": "デ"},
            ...                    {"text": "ス"}], "accent": 3}
            ...     ]
            ... }
            >>> entries = [ExtendedDictEntry(word="ずんだもん",
            ...                               pronunciation="ズンダモン",
            ...                               accent_type=3)]
            >>> results = matcher.find_matches_with_text(query, entries, "ずんだもんです")
            >>> len(results)
            1
            >>> results[0].mora_start_index
            0
            >>> results[0].mora_end_index
            5
        """
        if not entries or not input_text:
            return []

        accent_phrases = audio_query.get("accent_phrases", [])
        if not accent_phrases:
            return []

        # Step 1: Filter entries - only those whose word appears in input text
        filtered_entries = [e for e in entries if e.word in input_text]
        if not filtered_entries:
            return []

        results: list[MatchResult] = []

        # Step 2: For each accent phrase, search for partial matches
        for phrase_index, accent_phrase in enumerate(accent_phrases):
            moras = accent_phrase.get("moras", [])
            if not moras:
                continue

            # Build mora texts list for this accent phrase
            mora_texts = [mora.get("text", "") for mora in moras]
            phrase_pronunciation = "".join(mora_texts)

            # Step 3: Search for each filtered entry's pronunciation
            for entry in filtered_entries:
                pronunciation = entry.pronunciation
                if not pronunciation:
                    continue

                # Find all occurrences of pronunciation in this phrase
                search_start = 0
                while True:
                    # Find position in concatenated string
                    pos = phrase_pronunciation.find(pronunciation, search_start)
                    if pos == -1:
                        break

                    # Convert character position to mora index
                    # Each mora text is typically 1 character, but we need to be precise
                    mora_start = 0
                    char_count = 0
                    for i, text in enumerate(mora_texts):
                        if char_count == pos:
                            mora_start = i
                            break
                        char_count += len(text)

                    # Calculate mora end index
                    mora_end = mora_start
                    match_char_count = 0
                    for i in range(mora_start, len(mora_texts)):
                        match_char_count += len(mora_texts[i])
                        mora_end = i + 1
                        if match_char_count >= len(pronunciation):
                            break

                    # Verify the match length matches the pronunciation length
                    matched_pronunciation = "".join(mora_texts[mora_start:mora_end])
                    if matched_pronunciation == pronunciation:
                        results.append(
                            MatchResult(
                                entry=entry,
                                accent_phrase_index=phrase_index,
                                mora_start_index=mora_start,
                                mora_end_index=mora_end,
                            )
                        )

                    # Move search position past this match
                    search_start = pos + len(pronunciation)

        return results
