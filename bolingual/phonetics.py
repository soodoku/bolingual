from __future__ import annotations

import re
import unicodedata
from collections.abc import Sequence
from functools import lru_cache

import cmudict

INDEPENDENT_VOWELS = {
    "अ": "a",
    "आ": "aa",
    "इ": "i",
    "ई": "ii",
    "उ": "u",
    "ऊ": "uu",
    "ऋ": "ri",
    "ॠ": "rii",
    "ऌ": "li",
    "ॡ": "lii",
    "ए": "e",
    "ऐ": "ai",
    "ओ": "o",
    "औ": "au",
    "ऑ": "o",
    "ऍ": "e",
    "ऒ": "o",
}

MATRAS = {
    "ा": "aa",
    "ि": "i",
    "ी": "ii",
    "ु": "u",
    "ू": "uu",
    "ृ": "ri",
    "ॄ": "rii",
    "ॢ": "li",
    "ॣ": "lii",
    "े": "e",
    "ै": "ai",
    "ो": "o",
    "ौ": "au",
    "ॉ": "o",
    "ॅ": "e",
    "ॆ": "e",
    "ॊ": "o",
}

CONSONANTS = {
    "क": "k",
    "ख": "kh",
    "ग": "g",
    "घ": "gh",
    "ङ": "ng",
    "च": "ch",
    "छ": "chh",
    "ज": "j",
    "झ": "jh",
    "ञ": "ny",
    "ट": "t",
    "ठ": "th",
    "ड": "d",
    "ढ": "dh",
    "ण": "n",
    "त": "t",
    "थ": "th",
    "द": "d",
    "ध": "dh",
    "न": "n",
    "प": "p",
    "फ": "ph",
    "ब": "b",
    "भ": "bh",
    "म": "m",
    "य": "y",
    "र": "r",
    "ल": "l",
    "व": "v",
    "श": "sh",
    "ष": "sh",
    "स": "s",
    "ह": "h",
    "ळ": "l",
    "क़": "q",
    "ख़": "x",
    "ग़": "gh",
    "ज़": "z",
    "ड़": "r",
    "ढ़": "rh",
    "फ़": "f",
    "ऱ": "r",
    "ऴ": "l",
}

DIACRITICS = {
    "ं": "n",
    "ँ": "n",
    "ः": "h",
    "़": "",
    "ऽ": "",
}

IGNORE_CHARS = {"\u200d", "\u200c", "।", "॥", "-", " ", "(", ")", ",", "."}
VIRAMA = "्"
NUKTA = "़"

TOKEN_GRAMS = sorted(
    [
        "ksh",
        "chh",
        "kh",
        "gh",
        "jh",
        "th",
        "dh",
        "ph",
        "bh",
        "sh",
        "zh",
        "ng",
        "ny",
        "rh",
        "aa",
        "ii",
        "uu",
        "ai",
        "au",
        "ri",
        "ae",
        "oi",
        "ar",
    ],
    key=len,
    reverse=True,
)

VOWEL_TOKENS = {"a", "aa", "ae", "i", "ii", "u", "uu", "e", "ai", "o", "au", "ri", "ar", "oi"}

ARPABET_MAP = {
    "AA": "aa",
    "AE": "ae",
    "AH": "a",
    "AO": "o",
    "AW": "au",
    "AY": "ai",
    "B": "b",
    "CH": "ch",
    "D": "d",
    "DH": "dh",
    "EH": "e",
    "ER": "ar",
    "EY": "e",
    "F": "f",
    "G": "g",
    "HH": "h",
    "IH": "i",
    "IY": "ii",
    "JH": "j",
    "K": "k",
    "L": "l",
    "M": "m",
    "N": "n",
    "NG": "ng",
    "OW": "o",
    "OY": "oi",
    "P": "p",
    "R": "r",
    "S": "s",
    "SH": "sh",
    "T": "t",
    "TH": "th",
    "UH": "u",
    "UW": "uu",
    "V": "v",
    "W": "v",
    "Y": "y",
    "Z": "z",
    "ZH": "zh",
}

SIMILARITY_GROUPS = [
    {"a", "aa", "ae", "e", "o", "ar"},
    {"i", "ii", "e", "y"},
    {"u", "uu", "o"},
    {"k", "q", "g"},
    {"t", "d"},
    {"th", "dh"},
    {"p", "b"},
    {"f", "ph"},
    {"v", "w", "b"},
    {"s", "sh", "z", "zh"},
    {"ch", "j"},
    {"r", "rh"},
    {"n", "ng", "ny", "m"},
]
SIMILAR_LOOKUP: dict[str, set[str]] = {}
for group in SIMILARITY_GROUPS:
    for token in group:
        SIMILAR_LOOKUP.setdefault(token, set()).update(group)


@lru_cache(maxsize=1)
def cmudict_entries() -> dict[str, list[list[str]]]:
    return cmudict.dict()


def clean_english(text: str) -> str:
    cleaned = re.sub(r"[^a-z']+", "", str(text).strip().lower().replace("’", "'"))
    return cleaned


def romanize_hindi(text: str) -> str:
    text = unicodedata.normalize("NFC", str(text))
    out: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char in IGNORE_CHARS:
            index += 1
            continue
        if char in INDEPENDENT_VOWELS:
            out.append(INDEPENDENT_VOWELS[char])
            index += 1
            continue
        if char in CONSONANTS:
            consonant = CONSONANTS[char]
            next_index = index + 1
            if next_index < len(text) and text[next_index] == NUKTA:
                next_index += 1
            vowel = "a"
            if next_index < len(text) and text[next_index] in MATRAS:
                vowel = MATRAS[text[next_index]]
                next_index += 1
            elif next_index < len(text) and text[next_index] == VIRAMA:
                vowel = ""
                next_index += 1
            out.append(consonant + vowel)
            index = next_index
            continue
        if char in MATRAS:
            out.append(MATRAS[char])
            index += 1
            continue
        if char in DIACRITICS:
            out.append(DIACRITICS[char])
            index += 1
            continue
        index += 1
    # Bias plain Hindi /ph/ toward English-facing /f/ because it helps matching common loans.
    return "".join(out).replace("ph", "f")


def coarse_latin(text: str) -> str:
    value = text.lower().replace("'", "")
    replacements = [
        ("aa", "a"),
        ("ii", "i"),
        ("uu", "u"),
        ("ae", "a"),
        ("ai", "e"),
        ("au", "o"),
        ("ee", "i"),
        ("oo", "u"),
        ("ou", "o"),
        ("ow", "o"),
        ("aw", "o"),
        ("ck", "k"),
        ("qu", "k"),
        ("x", "kh"),
    ]
    for source, target in replacements:
        value = value.replace(source, target)
    value = value.replace("w", "v").replace("y", "i")
    value = (
        value.replace("ch", "c")
        .replace("sh", "s")
        .replace("zh", "s")
        .replace("jh", "j")
        .replace("kh", "k")
        .replace("gh", "g")
        .replace("th", "t")
        .replace("dh", "d")
        .replace("bh", "b")
        .replace("rh", "r")
        .replace("ph", "f")
        .replace("ng", "n")
        .replace("ny", "n")
    )
    value = value.replace("c", "k").replace("z", "s").replace("q", "k")
    return re.sub(r"(.)\1+", r"\1", value)


@lru_cache(maxsize=50000)
def tokenize_latin(text: str) -> tuple[str, ...]:
    lowered = text.lower()
    tokens: list[str] = []
    index = 0
    while index < len(lowered):
        for gram in TOKEN_GRAMS:
            if lowered.startswith(gram, index):
                tokens.append(gram)
                index += len(gram)
                break
        else:
            if lowered[index].isalpha():
                tokens.append(lowered[index])
            index += 1
    return tuple(tokens)


@lru_cache(maxsize=50000)
def hindi_variants(text: str) -> tuple[tuple[str, ...], ...]:
    base = list(tokenize_latin(romanize_hindi(text)))
    variants: list[tuple[str, ...]] = []
    seen: set[tuple[str, ...]] = set()

    def add(candidate: Sequence[str]) -> None:
        key = tuple(candidate)
        if key and key not in seen:
            seen.add(key)
            variants.append(key)

    add(base)
    if base and base[-1] == "a":
        add(base[:-1])
    medial = [
        token
        for idx, token in enumerate(base)
        if not (
            token == "a"
            and idx > 0
            and idx + 1 < len(base)
            and base[idx - 1] not in VOWEL_TOKENS
            and base[idx + 1] not in VOWEL_TOKENS
        )
    ]
    add(medial)
    if medial and medial[-1] == "a":
        add(medial[:-1])
    add([token for idx, token in enumerate(base) if not (token == "a" and idx > 0)])
    return tuple(variants)


@lru_cache(maxsize=100000)
def arpabet_to_tokens(pronunciation: tuple[str, ...]) -> tuple[str, ...]:
    out: list[str] = []
    for phone in pronunciation:
        stripped = re.sub(r"\d", "", phone)
        mapped = ARPABET_MAP.get(stripped)
        if mapped is not None:
            out.append(mapped)
    return tuple(out)


@lru_cache(maxsize=50000)
def spelling_to_tokens(word: str) -> tuple[str, ...]:
    return tokenize_latin(coarse_latin(word))


@lru_cache(maxsize=50000)
def english_pron_tokens(word: str) -> tuple[str, ...]:
    entries = cmudict_entries().get(word)
    if entries:
        tokens = arpabet_to_tokens(tuple(entries[0]))
        if tokens:
            return tokens
    return spelling_to_tokens(word)


@lru_cache(maxsize=100000)
def substitution_cost(left: str, right: str) -> float:
    if left == right:
        return 0.0
    if right in SIMILAR_LOOKUP.get(left, set()):
        return 0.35
    if left in VOWEL_TOKENS and right in VOWEL_TOKENS:
        return 0.45
    if left.rstrip("h") == right.rstrip("h"):
        return 0.25
    if left and right and left[0] == right[0]:
        return 0.5
    return 1.0


@lru_cache(maxsize=500000)
def weighted_similarity(
    left: tuple[str, ...], right: tuple[str, ...], schwa_cost: float = 0.3
) -> float:
    left_len = len(left)
    right_len = len(right)
    dp: list[list[float]] = [[0.0] * (right_len + 1) for _ in range(left_len + 1)]
    for left_idx in range(1, left_len + 1):
        dp[left_idx][0] = dp[left_idx - 1][0] + (schwa_cost if left[left_idx - 1] == "a" else 1.0)
    for right_idx in range(1, right_len + 1):
        dp[0][right_idx] = dp[0][right_idx - 1] + (
            schwa_cost if right[right_idx - 1] == "a" else 1.0
        )
    for left_idx in range(1, left_len + 1):
        left_token = left[left_idx - 1]
        for right_idx in range(1, right_len + 1):
            right_token = right[right_idx - 1]
            deletion = dp[left_idx - 1][right_idx] + (schwa_cost if left_token == "a" else 1.0)
            insertion = dp[left_idx][right_idx - 1] + (schwa_cost if right_token == "a" else 1.0)
            substitution = dp[left_idx - 1][right_idx - 1] + substitution_cost(
                left_token, right_token
            )
            dp[left_idx][right_idx] = min(deletion, insertion, substitution)
    normalizer = max(
        sum(schwa_cost if token == "a" else 1.0 for token in left),
        sum(schwa_cost if token == "a" else 1.0 for token in right),
        1.0,
    )
    return 1.0 - (dp[left_len][right_len] / normalizer)


def max_phonetic_similarity(hindi_text: str, english_word: str, schwa_cost: float = 0.3) -> float:
    english_tokens = english_pron_tokens(english_word)
    return max(
        weighted_similarity(variant, english_tokens, schwa_cost=schwa_cost)
        for variant in hindi_variants(hindi_text)
    )


def coarse_match_key_for_hindi(text: str) -> str:
    return coarse_latin(romanize_hindi(text))


def coarse_match_key_for_english(word: str) -> str:
    return coarse_latin(word)
