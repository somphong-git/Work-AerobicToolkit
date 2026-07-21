# Roadmap

## Current: Sprint 2.6 — Energy Analysis

The current release adds perceptual intensity information for aerobic session
planning.

- [x] Calculate an explainable overall energy score from 1–10.
- [x] Classify very-low, low, moderate, high, and peak energy.
- [x] Generate configurable energy sections that default to 15 seconds.
- [x] Decode audio once when BPM and energy are requested together.
- [x] Include energy in cache, JSON, CSV, CLI, and batch workflows.
- [x] Keep energy opt-in for backward-compatible runtime performance.

## Next: musical-key analysis

The next sprint will detect musical key and expose Camelot/Open Key values for
harmonic playlist ordering. Library indexing, playlist optimization, and mix
rendering remain later milestones.

## Delivery rules

- Each sprint has an issue, acceptance criteria, changelog entry, and release
  notes.
- Versions follow semantic versioning and release tags use `vMAJOR.MINOR.PATCH`.
- GitHub Projects tracks work through Backlog, Sprint, Doing, Review, and Done.
