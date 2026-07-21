# Roadmap

## Current: Sprint 3.0 — Workout Session Model

The current release defines the workout structure consumed by future planners.

- [x] Define warm-up, cardio, peak, and cool-down phase identifiers.
- [x] Require every phase exactly once in the canonical order.
- [x] Model target duration, BPM range, and energy range per phase.
- [x] Validate invalid ranges at domain-object construction time.
- [x] Serialize and restore sessions through interface-neutral dictionaries.
- [x] Provide a tested 60-minute standard planning template.

## Next: workout-aware playlist planning

The next sprint will assign library candidates to phases and score ordering by
duration fit, BPM, energy, harmonic compatibility, and tags.

## Delivery rules

- Each sprint has an issue, acceptance criteria, changelog entry, and release
  notes.
- Versions follow semantic versioning and release tags use `vMAJOR.MINOR.PATCH`.
- GitHub Projects tracks work through Backlog, Sprint, Doing, Review, and Done.
