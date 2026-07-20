# Roadmap

## Current: Sprint 2.2 — Repository Modernization

The immediate goal is a professional, contributor-ready repository before any
new audio or mixing capability is developed.

- [x] Move source code to the `src/` package layout.
- [x] Consolidate local runtime files under `data/`.
- [x] Configure packaging, Ruff, and pytest.
- [x] Add documentation, contributor standards, and security guidance.
- [x] Add GitHub issue forms, pull-request template, Dependabot, and workflows.
- [x] Add build, lint, format, release, and documentation scripts.

## Next: engine discovery sprint

The next sprint will begin only after an issue defines a narrow, testable
outcome. Candidate work includes a stable track metadata model and a
well-specified scanner contract. BPM analysis, energy analysis, playlist
optimization, and mix rendering remain explicitly deferred.

## Delivery rules

- Each sprint has an issue, acceptance criteria, changelog entry, and release
  notes.
- Versions follow semantic versioning and release tags use `vMAJOR.MINOR.PATCH`.
- GitHub Projects tracks work through Backlog, Sprint, Doing, Review, and Done.
