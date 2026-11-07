import inspect
import json
from pathlib import Path

from findex.corpus import iter_documents
from findex.tokenize import tokenize


def toks(s: str) -> list[str]:
    return list(tokenize(s))


def test_is_generator() -> None:
    assert inspect.isgeneratorfunction(tokenize)
    assert inspect.isgeneratorfunction(iter_documents)


def test_mixed_case_and_casefold() -> None:
    assert toks("Python PYTHON python") == ["python"] * 3
    assert toks("Straße") == toks("STRASSE") == ["strasse"]


def test_cyrillic() -> None:
    assert toks("Привіт, Світе! Їжак і ґанок") == ["привіт", "світе", "їжак", "і", "ґанок"]


def test_combining_accent_nfc() -> None:
    assert toks("café") == toks("café") == ["café"]


def test_punctuation_and_hyphens() -> None:
    assert toks("Hello, world... well-known!") == ["hello", "world", "well", "known"]


def test_apostrophes() -> None:
    assert toks("don't п'ять п’ять 'quoted'") == ["don't", "п'ять", "п'ять", "quoted"]


def test_digits() -> None:
    assert toks("Python 3.12 and 2026") == ["python", "3", "12", "and", "2026"]


def test_underscores() -> None:
    assert toks("__init__ ______ snake_case") == ["__init__", "snake_case"]


def test_empty() -> None:
    assert toks("") == []
    assert toks("   ...  —  ") == []


def test_iter_documents_is_lazy_and_reads_jsonl(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("Title A\nbody", encoding="utf-8")
    (tmp_path / "b.jsonl").write_text(
        json.dumps({"url": "u1", "title": "T1", "text": "x"}) + "\nnot json\n", encoding="utf-8"
    )
    (tmp_path / "bad.txt").write_bytes(b"ok \xff\xfe bytes")
    docs = iter_documents(tmp_path)
    first = next(docs)
    assert (first.doc_id, first.title) == (0, "Title A")
    rest = list(docs)
    assert [d.path for d in rest] == ["u1", str(tmp_path / "bad.txt")]
    assert [d.doc_id for d in rest] == [1, 2]
