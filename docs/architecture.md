# Architecture

## Purpose

Work-AerobicToolkit is being designed as one reusable engine with multiple
future delivery channels: CLI, desktop application, web dashboard, REST API,
plugins, AI agents, and mobile apps.

## Current boundary

All reusable Python code belongs in `src/aerobictoolkit/`. The current package
layout establishes stable ownership boundaries before feature development:

```text
src/aerobictoolkit/
├── analysis/   Track inspection and derived metrics
├── library/    Persistent catalog, search, filters, and tags
├── audio/      Audio I/O and signal-processing adapters
├── playlist/   Playlist domain operations
├── mixing/     Mix planning and rendering
├── export/     File and report export adapters
├── dashboard/  Dashboard integration boundary
├── config/     Package configuration assets and settings boundary
├── utils/      Small shared utilities
└── cli.py      Command-line adapter
```

## Design rules

1. Product rules must live in the reusable package, never in an interface.
2. The CLI, web, desktop, API, plugin, and agent layers will call the same
   application-facing API.
3. `data/` is local runtime data, not source code. Its contents are ignored by
   Git except for directory placeholders.
4. Optional audio dependencies will be added only when an approved feature
   requires them.
5. Public contracts are documented and tested before adding another interface.

## Batch analysis flow

```text
Directory scanner -> cache lookup -> track analyzer -> batch result
                                             |              |
                                             v              v
                                      isolated errors   JSON / CSV
```

The cache fingerprints each source file by absolute path, size, modification
time, and analysis profile. Cache failures become warnings; track failures are
captured individually so one damaged file does not stop the directory job.

## Tempo analysis flow

```text
Audio -> onset envelope -> raw tempo + beat frames
                              |              |
                              v              v
                     octave normalization   beat grid
                              \              /
                               confidence score
```

Raw detector output is retained alongside normalized BPM. Confidence combines
beat-grid regularity, frame-level tempo agreement, and evidence size. These are
engine values, so every future interface receives the same interpretation.

## Energy analysis flow

```text
Decoded audio -> RMS loudness (55%)
              -> onset activity (30%)  -> score 1–10 -> section timeline
              -> spectral brightness (15%)
```

Tempo and energy share one decoded mono signal when requested together. Energy
is opt-in and uses calibrated signal heuristics rather than LUFS. The engine
publishes the component metrics so later calibration remains explainable.

## Musical-key analysis flow

```text
Decoded audio -> middle 60 seconds -> 22.05 kHz -> harmonic CQT chromagram
                                                    |
                                                    v
                                      24 major/minor profile correlations
                                                    |
                                                    v
                                  key + confidence + Camelot + Open Key
```

The key adapter uses librosa's 12-bin Constant-Q chromagram and Krumhansl
major/minor profiles. Keeping the working segment bounded prevents large WAV
files from exhausting memory while tempo, energy, and key still share the
original decode operation.

## Library index flow

```text
Directory -> batch analysis/cache -> LibraryCatalog -> SQLite
                                              |
                                              v
                              search / filters / user tags
```

Track paths are unique and analysis refreshes use upserts. Tags use separate
many-to-many tables so re-analysis never overwrites user organization. SQLite
is a local persistence adapter behind public engine contracts; the CLI is only
one consumer of those contracts.

## Library transfer boundary

```text
LibraryCatalog -> versioned JSON / UTF-8 CSV -> another LibraryCatalog
       |
       +------ SQLite online backup -------> recoverable catalog copy
```

Export formats carry portable metadata and tags, while a backup preserves the
entire database. Import validates records before passing them through the same
catalog upsert boundary used by future interfaces. File-format schema versions
are independent from the internal SQLite schema version.

## Workout-session domain

```text
WorkoutSession
  -> warm-up   (duration + BPM/energy envelope)
  -> cardio    (duration + BPM/energy envelope)
  -> peak      (duration + BPM/energy envelope)
  -> cool-down (duration + BPM/energy envelope)
```

The playlist domain owns phase identity, canonical order, constraints, and
serialization. It does not yet select tracks or render audio. This separation
lets future planning strategies evolve while every interface shares the same
validated workout blueprint.

## Rule-based playlist flow

```text
WorkoutSession + LibraryTrack[]
           -> required-metadata filter
           -> scarcity-first phase allocation
           -> BPM 45% + energy 35% + duration 20%
           -> intensity ordering
           -> GeneratedPlaylist + timeline + warnings
```

Generation is deterministic and auditable. The first release uses greedy rules
rather than claiming global optimization. Result contracts retain score
components and duration gaps so later algorithms can be compared without
changing interface adapters.

## Dependency direction

```text
Future interfaces → aerobictoolkit package → standard library / approved adapters
```

An interface may depend on the engine; the engine must not depend on a specific
interface. This keeps future clients replaceable and testable.

See the decision records in [decisions](decisions/) for enduring choices.
