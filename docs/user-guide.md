# User Guide

## Current capability

This release can scan local tracks, normalize BPM, grade tempo and key
confidence, produce beat and energy timelines, and analyze a whole directory
with persistent caching. It is not yet a finished DJ-mixing product.

## Local music library

Build the full analysis catalog or use `--no-bpm` for a fast metadata-only
index:

```powershell
python -m aerobictoolkit library index data/input --energy --key
python -m aerobictoolkit library search "dance" --min-bpm 125 --tag cardio
python -m aerobictoolkit library search --mode minor --camelot 8A --json
```

Search supports BPM, energy, Camelot key, mode, format, and repeatable tag
filters. Multiple tags use AND semantics. Add or remove labels with `library
tag` and `library untag`; re-indexing updates analysis but preserves labels.

## Import, export, and backup

```powershell
python -m aerobictoolkit library export data/reports/library.json
python -m aerobictoolkit library export data/reports/library.csv
python -m aerobictoolkit library import data/reports/library.json
python -m aerobictoolkit library backup data/output/catalog-backup.sqlite3
```

Choose another source or destination catalog with `--database PATH`. Exported
metadata includes paths, descriptive metadata, searchable analysis values, and
tags. JSON includes a schema version for machine integrations; CSV uses a BOM
for Excel and stores tags as a JSON array. Import merges tags and updates a
track when its resolved path already exists.

Backup differs from export: it copies the complete SQLite catalog and is the
recommended recovery artifact. Test a backup without replacing the active
catalog using `library search --database PATH`.

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

## Energy score and timeline

Energy analysis is opt-in and returns an overall score from 1–10 plus sections
that default to 15 seconds:

```bash
python -m aerobictoolkit analyze "data/input/your-track.wav" --energy --json
python -m aerobictoolkit batch data/input --energy
python -m aerobictoolkit batch data/input --energy \
  --energy-section-seconds 10
```

Energy levels are `very-low` (1–2), `low` (3–4), `moderate` (5–6), `high`
(7–8), and `peak` (9–10). The score combines RMS loudness, onset activity, and
spectral brightness. It is intended for relative workout programming and is
not a broadcast loudness or LUFS measurement.

## Musical key and harmonic compatibility

```bash
python -m aerobictoolkit analyze "data/input/your-track.wav" --key --json
python -m aerobictoolkit batch data/input --key
```

The result includes conventional key notation, Camelot, Open Key, confidence,
and four compatible wheel positions:

- the same Camelot position;
- the previous and next number in the same mode;
- the relative major or minor at the same number.

For example, `8A` (A minor / `1m`) is compatible with `8A`, `7A`, `9A`, and
`8B`. Low-confidence results should be reviewed by ear before rendering a mix.
Key detection analyzes a downsampled 60-second middle segment to bound memory
use on studio-quality WAV files.

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
