# Roadmap

## Current: Sprint 3.1 — Rule-Based Playlist Generator

The current release fills a workout session from analyzed library tracks.

- [x] Require duration, BPM, and energy metadata for candidate tracks.
- [x] Score BPM fit, energy fit, and remaining duration fit explicitly.
- [x] Allocate scarce phases first and never reuse a track.
- [x] Order intensity upward and then downward for cool-down.
- [x] Publish timeline positions, duration gaps, completeness, and warnings.
- [x] Generate through both the Python API and CLI.

## Next: harmonic and transition planning

The next sprint will improve within-phase ordering with Camelot compatibility,
tempo-step limits, transition scores, and explainable fallback rules.

## Delivery rules

- Each sprint has an issue, acceptance criteria, changelog entry, and release
  notes.
- Versions follow semantic versioning and release tags use `vMAJOR.MINOR.PATCH`.
- GitHub Projects tracks work through Backlog, Sprint, Doing, Review, and Done.
