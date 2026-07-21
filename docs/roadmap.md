# Roadmap

## Current: Sprint 2.8 — Library Index

The current release turns analyzed files into reusable local library data.

- [x] Persist tracks and complete analysis JSON in SQLite.
- [x] Update existing tracks without duplicating paths or losing tags.
- [x] Search title, artist, album, and path.
- [x] Filter by BPM, energy, Camelot key, mode, format, and multiple tags.
- [x] Add, remove, list, and search case-insensitive tags.
- [x] Expose the same catalog service through Python and CLI.

## Next: playlist planning

The next sprint will score candidate tracks and build workout-aware ordering
from BPM, energy, harmonic compatibility, tags, and phase constraints.

## Delivery rules

- Each sprint has an issue, acceptance criteria, changelog entry, and release
  notes.
- Versions follow semantic versioning and release tags use `vMAJOR.MINOR.PATCH`.
- GitHub Projects tracks work through Backlog, Sprint, Doing, Review, and Done.
