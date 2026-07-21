# ADR-0010: Version portable library transfers independently

- Status: Accepted
- Date: 2026-07-21

## Context

Users need editable CSV, machine-readable JSON, and disaster-recovery backups.
These serve different purposes. Treating an SQLite file or internal analysis
cache as the interchange contract would couple future interfaces to storage
details and make format evolution unsafe.

## Decision

Provide a versioned JSON envelope and a matching flat CSV representation for
portable metadata. CSV uses UTF-8 with BOM and encodes tags as a JSON array.
Import identifies tracks by resolved path, updates metadata, and merges tags.
Provide a separate SQLite online-backup operation for full recovery.

The transfer schema version and database schema version evolve independently.

## Consequences

- Desktop, web, API, plugins, and agents can share one documented transfer
  contract without reading internal tables.
- CSV remains practical for spreadsheets while preserving commas in tag names.
- JSON can gain explicitly versioned migrations later.
- A metadata export is portable but not a byte-for-byte database backup.
