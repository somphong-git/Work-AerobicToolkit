# User Guide

## Current capability

This release can scan local tracks, read their metadata, and estimate BPM. It
is not yet a finished DJ-mixing product.

```bash
python -m aerobictoolkit --version
python -m aerobictoolkit scan data/input
python -m aerobictoolkit analyze "data/input/your-track.mp3" --json
```

For metadata only, append `--no-bpm`. BPM estimation requires the optional
`analysis` installation group described in the installation guide.

## Local data directories

Place local source files under `data/input/`. Future outputs, reports, and
caches belong under `data/output/`, `data/reports/`, and `data/cache/`.
Contents of these directories are intentionally excluded from Git.
