#!/usr/bin/env bash
# Downloads the corpus: the Python documentation sources (reStructuredText) from CPython.
# Result: data/python-docs/**/*.rst  (~560 files, ~15 MB). data/ is in .gitignore.
set -euo pipefail
TMP=$(mktemp -d)
git clone -q --depth 1 --filter=blob:none --sparse https://github.com/python/cpython.git "$TMP/cpython"
git -C "$TMP/cpython" sparse-checkout set Doc
mkdir -p data/python-docs
(cd "$TMP/cpython/Doc" && find . -name '*.rst' -exec cp --parents {} "$OLDPWD/data/python-docs/" \;)
git -C "$TMP/cpython" rev-parse --short HEAD > data/python-docs/CPYTHON_COMMIT
rm -rf "$TMP"
echo "corpus ready: $(find data/python-docs -name '*.rst' | wc -l) files in data/python-docs"
