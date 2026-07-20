# Roadmap

## Current: Sprint 2.3 — Core Audio Analysis

The immediate goal is a reusable, testable audio-analysis boundary for all
future clients.

- [x] Define immutable metadata and analysis result models.
- [x] Read supported local track metadata and duration.
- [x] Estimate BPM through an optional audio-analysis adapter.
- [x] Expose scan and analyze workflows through the CLI.
- [x] Cover engine behavior with automated tests.

## Next: playlist intelligence sprint

The next sprint will begin only after an issue defines a narrow, testable
outcome. Candidate work includes energy analysis, BPM confidence, and playlist
optimization. Mix rendering remains explicitly deferred.

## Delivery rules

- Each sprint has an issue, acceptance criteria, changelog entry, and release
  notes.
- Versions follow semantic versioning and release tags use `vMAJOR.MINOR.PATCH`.
- GitHub Projects tracks work through Backlog, Sprint, Doing, Review, and Done.
