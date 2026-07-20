# Architecture

## Purpose

Work-AerobicToolkit is being designed as one reusable engine with multiple
future delivery channels: CLI, desktop application, web dashboard, REST API,
plugins, AI agents, and mobile apps.

## Current boundary

All reusable Python code belongs in `src/aerobictoolkit/`. The current package
layout establishes stable ownership boundaries before feature development:

```text
src/aerobictoolkit/
├── analysis/   Track inspection and derived metrics
├── audio/      Audio I/O and signal-processing adapters
├── playlist/   Playlist domain operations
├── mixing/     Mix planning and rendering
├── export/     File and report export adapters
├── dashboard/  Dashboard integration boundary
├── config/     Package configuration assets and settings boundary
├── utils/      Small shared utilities
└── cli.py      Command-line adapter
```

## Design rules

1. Product rules must live in the reusable package, never in an interface.
2. The CLI, web, desktop, API, plugin, and agent layers will call the same
   application-facing API.
3. `data/` is local runtime data, not source code. Its contents are ignored by
   Git except for directory placeholders.
4. Optional audio dependencies will be added only when an approved feature
   requires them.
5. Public contracts are documented and tested before adding another interface.

## Dependency direction

```text
Future interfaces → aerobictoolkit package → standard library / approved adapters
```

An interface may depend on the engine; the engine must not depend on a specific
interface. This keeps future clients replaceable and testable.

See the decision records in [decisions](decisions/) for enduring choices.
