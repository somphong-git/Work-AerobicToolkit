# ADR-0008: Publish musical key in standard and DJ-wheel notation

## Status

Accepted — 2026-07-21

## Context

Harmonic playlist ordering needs a stable key contract that musicians and DJs
can both understand. Full-song CQT processing on studio WAV files can consume
enough memory to terminate a local analysis process.

## Decision

The engine analyzes the middle 60 seconds, resampled to at most 22.05 kHz. It
extracts a 12-bin Constant-Q chromagram and correlates its mean pitch profile
against Krumhansl major and minor templates. Results include conventional key,
confidence, Camelot, Open Key, and same/adjacent/relative-mode compatibility.

Librosa documents `chroma_cqt` as a Constant-Q chromagram with 12 configurable
chroma bins: <https://librosa.org/doc/latest/generated/librosa.feature.chroma_cqt.html>.

## Consequences

All clients can sort and filter harmonically without implementing wheel maps.
Memory use is bounded and BPM, energy, and key share one original decode. The
detector represents the dominant segment key; modulating tracks and low-
confidence results still require listening or a future section-key model.
