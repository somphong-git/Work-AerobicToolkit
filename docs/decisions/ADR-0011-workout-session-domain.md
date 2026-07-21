# ADR-0011: Model workout structure before playlist generation

- Status: Accepted
- Date: 2026-07-21

## Context

Automatic playlist planning needs a stable definition of the workout it is
planning for. If phase names, order, durations, or intensity rules live inside
one scoring algorithm or interface, future clients can produce incompatible
sessions.

## Decision

Define `WorkoutSession`, `WorkoutPhase`, and `WorkoutPhaseType` in the playlist
domain. A complete session contains warm-up, cardio, peak, and cool-down once
in canonical order. Every phase has a positive target duration plus validated
BPM and 1–10 energy envelopes. Provide dictionary serialization and a standard
60-minute factory.

Do not add track assignment, scoring, transitions, persistence, or audio
rendering to these models in Sprint 3.0.

## Consequences

- All interfaces and future planners share one validated workout contract.
- Invalid phase order and intensity ranges fail at construction time.
- Planning algorithms can be replaced without changing session identity.
- The initial preset is a configurable music-planning default, not medical
  guidance.
