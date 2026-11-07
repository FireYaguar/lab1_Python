"""Corpus statistics in one streaming pass.

    python -m findex.stats data/ [--limit N] [--top 50] [--eager]

--eager is the deliberately bad version (Lab 1, M4): everything goes into lists first.
"""

from __future__ import annotations

import argparse
import logging
import time
import tracemalloc
from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from itertools import islice
from pathlib import Path

from findex.corpus import Document, iter_documents
from findex.tokenize import tokenize


@dataclass(slots=True)
class CorpusStats:
    documents: int
    tokens: int
    counts: Counter[str]

    @property
    def vocabulary(self) -> int:
        return len(self.counts)


def compute_stats(docs: Iterable[Document]) -> CorpusStats:
    """Lazy: one document in memory at a time; only the Counter (the sink) grows."""
    counts: Counter[str] = Counter()
    n_docs = 0
    for doc in docs:
        n_docs += 1
        counts.update(tokenize(doc.text))
    return CorpusStats(n_docs, counts.total(), counts)


def compute_stats_eager(docs: Iterable[Document]) -> CorpusStats:
    """Eager on purpose: all documents in a list, all tokens in lists of lists."""
    all_docs = list(docs)
    all_tokens = [list(tokenize(d.text)) for d in all_docs]
    counts: Counter[str] = Counter()
    for toks in all_tokens:
        counts.update(toks)
    return CorpusStats(len(all_docs), sum(len(t) for t in all_tokens), counts)


def measure[T](fn: Callable[[], T]) -> tuple[T, float, int]:
    """Run fn under tracemalloc; return (result, elapsed seconds, peak bytes)."""
    tracemalloc.start()
    t0 = time.perf_counter()
    try:
        result = fn()
        elapsed = time.perf_counter() - t0
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return result, elapsed, peak


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="python -m findex.stats", description=__doc__)
    ap.add_argument("root", type=Path, help="corpus directory or .jsonl file")
    ap.add_argument("--limit", type=int, default=None, help="only the first N documents")
    ap.add_argument("--top", type=int, default=50)
    ap.add_argument("--eager", action="store_true", help="list-based version, for comparison")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

    compute = compute_stats_eager if args.eager else compute_stats

    def run() -> CorpusStats:
        docs = islice(iter_documents(args.root), args.limit)  # lazy --limit
        return compute(docs)

    stats, elapsed, peak = measure(run)
    print(f"mode:        {'eager' if args.eager else 'lazy'}")
    print(f"documents:   {stats.documents:,}")
    print(f"tokens:      {stats.tokens:,}")
    print(f"vocabulary:  {stats.vocabulary:,}")
    print(f"elapsed:     {elapsed:.2f} s")
    print(f"peak memory: {peak / 2**20:.1f} MiB (tracemalloc)")
    print(f"\ntop-{args.top} terms:")
    for rank, (term, n) in enumerate(stats.counts.most_common(args.top), 1):
        print(f"{rank:>3}. {term:<20} {n:,}")


if __name__ == "__main__":
    main()
