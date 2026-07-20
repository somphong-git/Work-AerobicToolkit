# ADR-0001: Use a `src/` package layout

## Status

Accepted — 2026-07-20

## Context

The project started with source directories at the repository root. As the
repository grows, that layout makes it easy for tests and scripts to import
unpackaged code accidentally.

## Decision

All importable product code lives under `src/aerobictoolkit/`. Tests, examples,
documentation, local data, and automation live outside the package.

## Consequences

Tests and examples must install the project or deliberately use the configured
test path. Packaging configuration is now a first-class repository concern,
but the import boundary is explicit and reusable clients can depend on one
package.
