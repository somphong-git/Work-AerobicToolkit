# Roadmap

## Current: Sprint 2.9 — Library Import, Export, and Backup

The current release makes library metadata portable and recoverable.

- [x] Export all indexed metadata and tags to versioned JSON.
- [x] Export Excel-compatible UTF-8 CSV without corrupting tag separators.
- [x] Import JSON and CSV with field validation and actionable row errors.
- [x] Update matching paths and merge tags without duplicating tracks.
- [x] Create consistent SQLite backups through the engine API.
- [x] Expose transfer operations through Python and CLI.

## Next: playlist planning

The next sprint will score candidate tracks and build workout-aware ordering
from BPM, energy, harmonic compatibility, tags, and phase constraints.

## Delivery rules

- Each sprint has an issue, acceptance criteria, changelog entry, and release
  notes.
- Versions follow semantic versioning and release tags use `vMAJOR.MINOR.PATCH`.
- GitHub Projects tracks work through Backlog, Sprint, Doing, Review, and Done.
