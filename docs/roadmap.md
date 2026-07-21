# Roadmap

## Current: Sprint 2.7 — Musical Key Analysis

The current release adds harmonic metadata for compatible playlist ordering.

- [x] Detect all 12 roots in major and minor modes.
- [x] Publish confidence and low, medium, or high review guidance.
- [x] Map every result to Camelot and Open Key notation.
- [x] Suggest same, adjacent, and relative-mode wheel positions.
- [x] Bound CQT memory with a downsampled 60-second analysis segment.
- [x] Include key data in cache, JSON, CSV, CLI, and batch workflows.

## Next: music-library index

The next sprint will persist analyzed tracks in a searchable local catalog with
filtering by BPM, confidence, energy, key, format, and duration. Playlist
optimization and mix rendering remain later milestones.

## Delivery rules

- Each sprint has an issue, acceptance criteria, changelog entry, and release
  notes.
- Versions follow semantic versioning and release tags use `vMAJOR.MINOR.PATCH`.
- GitHub Projects tracks work through Backlog, Sprint, Doing, Review, and Done.
