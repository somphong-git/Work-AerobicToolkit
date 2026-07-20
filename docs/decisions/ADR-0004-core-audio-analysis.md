# ADR-0004: Keep audio analysis behind stable result contracts

## Status

Accepted — 2026-07-20

## Context

Every future interface needs consistent track descriptions and BPM estimates.
Audio decoders and signal-processing libraries are implementation details that
must not leak into the CLI, desktop app, web dashboard, API, plugins, agents,
or mobile clients.

## Decision

The `analysis` package exposes immutable `TrackMetadata` and `TrackAnalysis`
models plus `read_track_metadata`, `estimate_bpm`, and `analyze_track` service
functions. Mutagen is the metadata adapter. Librosa is an optional BPM adapter
loaded only when BPM estimation is requested.

## Consequences

Clients receive serializable, stable values and can skip expensive BPM work.
Future adapters may replace the implementation without changing the public
contract. A missing optional BPM dependency produces an actionable error.
