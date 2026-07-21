# ADR-0009: Use SQLite for the local music-library index

- Status: Accepted
- Date: 2026-07-21

## Context

The toolkit needs a durable catalog for every future interface. JSON reports
and analysis caches are snapshots, not a safe home for user tags or composable
search filters.

## Decision

Use Python's standard-library SQLite adapter behind `LibraryCatalog`. Store one
track per resolved path, denormalized analysis fields for common filters, the
complete analysis JSON for forward compatibility, and tags in a normalized
many-to-many relationship. Keep the default database under `data/library/` and
out of version control.

## Consequences

- Installation gains no database-server or Python-package dependency.
- Transactions, indexes, constraints, and parameterized SQL provide a stronger
  foundation than editing JSON files.
- Re-indexing refreshes derived analysis while preserving user tags.
- A future shared service can implement the same contracts with another store.
