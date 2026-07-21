# ADR-0012: Begin playlist generation with deterministic rules

- Status: Accepted
- Date: 2026-07-21

## Context

Workout sessions now define phase constraints and the library supplies analyzed
tracks. The first generator must be understandable, reproducible, and safe to
use from every interface before introducing optimization or AI ranking.

## Decision

Require positive duration plus BPM and energy for candidate tracks. Filter each
phase by its domain envelope, allocate phases with fewer candidates first, and
never reuse a resolved track path. Select greedily using BPM fit at 45%, energy
fit at 35%, and remaining-duration fit at 20%. Order intensity upward through
peak and downward in cool-down.

Publish component scores, timeline positions, duration differences,
completeness, and warnings. Use deterministic title/path tie breakers. Do not
include musical-key or transition optimization in Sprint 3.1.

## Consequences

- Identical inputs and rules produce identical playlists.
- Users and future interfaces can explain every selection.
- Scarcity-first allocation reduces, but does not mathematically eliminate,
  suboptimal greedy choices.
- Incomplete libraries return a partial result with warnings instead of hiding
  the shortfall or silently relaxing phase constraints.
