# ADR-0005: Cache batch analysis outside the source tree

## Status

Accepted — 2026-07-21

## Context

BPM analysis is expensive enough that repeatedly processing an unchanged music
library would make every interface feel slow. A damaged track must also not
prevent reports for the rest of a directory.

## Decision

Batch analysis returns one immutable result containing successful tracks,
per-track errors, cache state, and cache warnings. The local JSON cache lives
under `data/cache/` by default and uses path, file size, modification time, and
analysis profile as its fingerprint. Reports are independent adapters under
the `export` package and default to `data/reports/`.

## Consequences

CLI and future interfaces can run the same batch service and render its result
differently. Changed files are recalculated, corrupted caches are ignored with
a warning, and partial results remain exportable when individual tracks fail.
