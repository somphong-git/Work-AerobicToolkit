# ADR-0002: Keep one reusable engine boundary

## Status

Accepted — 2026-07-20

## Context

The project is expected to serve multiple delivery channels over time: CLI,
desktop, web, REST API, plugins, AI agents, and mobile applications.

## Decision

Business rules and future audio workflows will be implemented in the reusable
`aerobictoolkit` package. Interfaces will adapt inputs and outputs around that
package rather than reimplementing behavior.

## Consequences

The first interface may be small, but it must not become the only place where
domain behavior exists. This increases initial design discipline while reducing
duplication across future clients.
