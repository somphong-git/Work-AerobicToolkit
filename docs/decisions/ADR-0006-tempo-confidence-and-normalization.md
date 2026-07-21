# ADR-0006: Preserve raw tempo and publish normalized confidence

## Status

Accepted — 2026-07-21

## Context

Beat trackers commonly return half-time or double-time interpretations of the
same rhythm. Playlist and mixing decisions also need to distinguish a stable
tempo estimate from a weak one and need reusable beat positions.

## Decision

The engine preserves detector output as `raw_bpm` and normalizes it by powers
of two into a configurable range that defaults to 90–180 BPM. The target range
must span at least one octave. Beat positions are expanded or subsampled to
match the normalized tempo. Confidence is a 0–1 heuristic combining beat
regularity, frame-level tempo agreement, and beat evidence.

## Consequences

All interfaces receive the same BPM interpretation, confidence band, and beat
grid. Consumers can reject or review low-confidence tracks. Confidence is
explicitly not a statistical probability, and future detector improvements
can evolve behind the stable result contract and cache profile.
