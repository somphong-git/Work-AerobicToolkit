# User Guide

## Current capability

This release is a repository foundation, not a finished DJ-mixing product. The
available command validates that the package is installed:

```bash
python -m aerobictoolkit --version
python -m aerobictoolkit --help
```

The examples directory contains a basic file-scanning example and placeholders
that make the upcoming BPM and playlist learning paths visible without claiming
that those features exist.

## Local data directories

Place local source files under `data/input/`. Future outputs, reports, and
caches belong under `data/output/`, `data/reports/`, and `data/cache/`.
Contents of these directories are intentionally excluded from Git.
