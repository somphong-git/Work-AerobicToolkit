# User Guide

## Current capability

This release can scan local tracks, read metadata, estimate BPM, and analyze a
whole directory with persistent caching. It is not yet a finished DJ-mixing
product.

```bash
python -m aerobictoolkit --version
python -m aerobictoolkit scan data/input
python -m aerobictoolkit analyze "data/input/your-track.mp3" --json
```

For metadata only, append `--no-bpm`. BPM estimation requires the optional
`analysis` installation group described in the installation guide.

## Batch analysis

```bash
python -m aerobictoolkit batch data/input
```

The command continues when an individual track cannot be decoded. Successful
tracks and per-file errors are both included in the JSON and CSV reports under
`data/reports/`. Unchanged tracks are loaded from `data/cache/` on later runs.

Useful options:

```bash
python -m aerobictoolkit batch data/input --no-bpm
python -m aerobictoolkit batch data/input --no-cache
python -m aerobictoolkit batch data/input \
  --json-report data/reports/custom.json \
  --csv-report data/reports/custom.csv
```

## Local data directories

Place local source files under `data/input/`. Future outputs, reports, and
caches belong under `data/output/`, `data/reports/`, and `data/cache/`.
Contents of these directories are intentionally excluded from Git.
