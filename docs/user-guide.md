# User Guide

## Current capability

This release can scan local tracks, normalize BPM, grade tempo confidence,
produce a beat grid, and analyze a whole directory with persistent caching. It
is not yet a finished DJ-mixing product.

```bash
python -m aerobictoolkit --version
python -m aerobictoolkit scan data/input
python -m aerobictoolkit analyze "data/input/your-track.mp3" --json
```

For metadata only, append `--no-bpm`. BPM estimation requires the optional
`analysis` installation group described in the installation guide.

## BPM confidence and beat grid

The `bpm` field is normalized into 90–180 BPM by multiplying or dividing the
raw estimate by two. `raw_bpm` preserves the detector output. The confidence
score is a 0–1 heuristic based on beat regularity, tempo agreement over time,
and the amount of beat evidence; it is not a statistical probability.

- `high`: 0.80–1.00
- `medium`: 0.50–0.79
- `low`: below 0.50

The JSON result includes every detected beat position in seconds. CSV reports
include the confidence level, beat count, first beat, and serialized beat grid.

```bash
python -m aerobictoolkit analyze "data/input/your-track.wav" --json
python -m aerobictoolkit batch data/input --min-bpm 100 --max-bpm 200
```

The maximum must be at least twice the minimum so every positive tempo has an
unambiguous octave-normalized value.

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
