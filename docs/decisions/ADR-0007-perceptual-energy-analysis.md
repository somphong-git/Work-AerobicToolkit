# ADR-0007: Publish explainable perceptual energy

## Status

Accepted — 2026-07-21

## Context

Aerobic playlist planning needs more than BPM. Two tracks at the same tempo can
feel very different because of loudness, transient activity, and spectral
content. Interfaces need one consistent score and a timeline of changes.

## Decision

Energy is an opt-in engine capability scored from 1–10. The first calibration
weights RMS loudness at 55%, onset activity at 30%, and spectral brightness at
15%. The engine also creates fixed-duration sections, defaulting to 15 seconds,
and publishes all component metrics. BPM and energy share one audio decode when
requested together.

## Consequences

Future playlist clients can model warm-up, cardio, peak, and cool-down phases
using the same values. The score is explainable and recalibratable but is not a
LUFS measurement or a universal statement about musical intensity. The cache
profile and schema change whenever interpretation would otherwise become stale.
