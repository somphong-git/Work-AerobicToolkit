# Roadmap

## Current: Sprint 2.5 — BPM Confidence and Beat Grid

The current release improves tempo reliability before playlist decisions are
built on top of analysis results.

- [x] Preserve raw BPM and normalize half-time/double-time estimates.
- [x] Support configurable one-octave tempo ranges.
- [x] Generate normalized beat positions in seconds.
- [x] Calculate confidence from regularity, tempo agreement, and beat evidence.
- [x] Expose low, medium, and high confidence levels.
- [x] Include tempo details in cache, JSON, CSV, CLI, and batch workflows.

## Next: energy analysis

The next sprint will derive perceptual energy and intensity sections for
warm-up, cardio, peak, and cool-down planning. Musical-key analysis, playlist
optimization, and mix rendering remain later milestones.

## Delivery rules

- Each sprint has an issue, acceptance criteria, changelog entry, and release
  notes.
- Versions follow semantic versioning and release tags use `vMAJOR.MINOR.PATCH`.
- GitHub Projects tracks work through Backlog, Sprint, Doing, Review, and Done.
