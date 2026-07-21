# Roadmap

## Current: Sprint 2.4 — Batch Analysis and Cache

The current release makes core analysis practical for a local music library.

- [x] Analyze every supported track in a directory.
- [x] Reuse unchanged results from a persistent cache.
- [x] Invalidate cache entries when a file or analysis profile changes.
- [x] Continue after per-track decoder or analysis failures.
- [x] Export complete UTF-8 JSON and Excel-friendly CSV reports.
- [x] Expose the workflow through a production-facing CLI command.

## Next: BPM confidence and beat-grid analysis

The next sprint will improve tempo reliability with confidence information,
tempo-range normalization, and beat timing. Energy analysis, playlist
optimization, and mix rendering remain later milestones.

## Delivery rules

- Each sprint has an issue, acceptance criteria, changelog entry, and release
  notes.
- Versions follow semantic versioning and release tags use `vMAJOR.MINOR.PATCH`.
- GitHub Projects tracks work through Backlog, Sprint, Doing, Review, and Done.
