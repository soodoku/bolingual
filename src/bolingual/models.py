from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from rapidfuzz.distance import JaroWinkler

from .phonetics import (
    coarse_match_key_for_english,
    coarse_match_key_for_hindi,
    english_pron_tokens,
    hindi_variants,
    weighted_similarity,
)


@dataclass
class CandidateIndex:
    vocabulary: list[str]
    orth_keys: dict[str, str]
    pron_tokens: dict[str, tuple[str, ...]]

    @classmethod
    def from_words(cls, words: Iterable[str]) -> CandidateIndex:
        unique_words = sorted(set(words))
        return cls(
            vocabulary=unique_words,
            orth_keys={word: coarse_match_key_for_english(word) for word in unique_words},
            pron_tokens={word: english_pron_tokens(word) for word in unique_words},
        )

    def orthographic_ranking(self, hindi_text: str) -> list[tuple[float, str]]:
        query_key = coarse_match_key_for_hindi(hindi_text)
        ranking = [
            (JaroWinkler.similarity(query_key, self.orth_keys[word]), word)
            for word in self.vocabulary
        ]
        ranking.sort(reverse=True)
        return ranking

    def phonetic_ranking(
        self,
        hindi_text: str,
        candidates: Iterable[str],
        schwa_cost: float = 0.3,
    ) -> list[tuple[float, str]]:
        variants = hindi_variants(hindi_text)
        ranking: list[tuple[float, str]] = []
        for word in candidates:
            if not variants or not self.pron_tokens[word]:
                score = 0.0
            else:
                score = max(
                    weighted_similarity(variant, self.pron_tokens[word], schwa_cost=schwa_cost)
                    for variant in variants
                )
            ranking.append((score, word))
        ranking.sort(reverse=True)
        return ranking

    def hybrid_ranking(
        self,
        hindi_text: str,
        top_k: int = 50,
        alpha: float = 0.5,
        schwa_cost: float = 0.3,
    ) -> dict[str, list[tuple[float, str]]]:
        orthographic = self.orthographic_ranking(hindi_text)
        shortlist = [word for _, word in orthographic[:top_k]]
        phonetic = self.phonetic_ranking(hindi_text, shortlist, schwa_cost=schwa_cost)
        orth_dict = {word: score for score, word in orthographic[:top_k]}
        hybrid = [
            (alpha * orth_dict[word] + (1.0 - alpha) * score, word) for score, word in phonetic
        ]
        hybrid.sort(reverse=True)
        return {
            "orthographic": orthographic,
            "phonetic": phonetic,
            "hybrid": hybrid,
        }
