"""Streaming tokenizer.

Policy (documented in README too):
- Unicode NFC normalization first, then str.casefold() (not lower()).
- A token is a run of word characters (\\w: letters, digits, underscore, any script).
- Apostrophes INSIDE a word are kept: "don't", "п'ять" are one token.
  Typographic apostrophes (’ U+2019, ʼ U+02BC) are mapped to ASCII ' first.
- Hyphens split words: "well-known" -> "well", "known".
- Digits are kept as tokens: "Python 3.12" -> "python", "3", "12".
- Tokens made only of underscores (rst/markdown decoration "____") are dropped;
  identifiers like "__init__" are kept.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterator

TOKEN_RE = re.compile(r"\w+(?:'\w+)*")
_APOSTROPHES = str.maketrans({"’": "'", "ʼ": "'"})


def normalize(text: str) -> str:
    return unicodedata.normalize("NFC", text).translate(_APOSTROPHES).casefold()


def tokenize_with_offsets(text: str) -> Iterator[tuple[str, int]]:
    """Yield (token, start offset in the normalized text). Positions are for Lab 3."""
    for m in TOKEN_RE.finditer(normalize(text)):  # finditer: lazy, no list of matches
        tok = m.group()
        if tok.strip("_"):
            yield tok, m.start()


def tokenize(text: str) -> Iterator[str]:
    for tok, _ in tokenize_with_offsets(text):
        yield tok
