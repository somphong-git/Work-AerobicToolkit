"""Batch orchestration for directory-level audio analysis."""

from __future__ import annotations

from pathlib import Path

from .cache import AnalysisCache
from .energy import DEFAULT_ENERGY_SECTION_SECONDS
from .models import BatchAnalysisResult, BatchTrackAnalysis, TrackAnalysisError
from .scanner import scan_music
from .service import (
    DEFAULT_MAX_BPM,
    DEFAULT_MIN_BPM,
    _validate_tempo_range,
    analyze_track,
)


def analyze_directory(
    directory: str | Path,
    *,
    include_bpm: bool = True,
    include_energy: bool = False,
    cache_path: str | Path | None = None,
    min_bpm: float = DEFAULT_MIN_BPM,
    max_bpm: float = DEFAULT_MAX_BPM,
    energy_section_seconds: float = DEFAULT_ENERGY_SECTION_SECONDS,
) -> BatchAnalysisResult:
    """Analyze every supported file while isolating per-track failures."""
    if include_bpm:
        _validate_tempo_range(min_bpm, max_bpm)
    if include_energy and energy_section_seconds <= 0:
        raise ValueError("Energy section duration must be greater than zero.")
    source = Path(directory).expanduser().resolve()
    cache = AnalysisCache(cache_path) if cache_path is not None else None
    tracks: list[BatchTrackAnalysis] = []
    errors: list[TrackAnalysisError] = []

    for path in scan_music(source):
        cached = (
            cache.get(
                path,
                include_bpm=include_bpm,
                include_energy=include_energy,
                min_bpm=min_bpm,
                max_bpm=max_bpm,
                energy_section_seconds=energy_section_seconds,
            )
            if cache
            else None
        )
        if cached is not None:
            tracks.append(BatchTrackAnalysis(cached, from_cache=True))
            continue

        try:
            analysis = analyze_track(
                path,
                include_bpm=include_bpm,
                include_energy=include_energy,
                min_bpm=min_bpm,
                max_bpm=max_bpm,
                energy_section_seconds=energy_section_seconds,
            )
        except Exception as error:  # noqa: BLE001 - batch must isolate bad tracks
            errors.append(
                TrackAnalysisError(
                    path=path.resolve(),
                    error_type=type(error).__name__,
                    message=str(error),
                )
            )
            continue

        tracks.append(BatchTrackAnalysis(analysis, from_cache=False))
        if cache:
            cache.put(
                analysis,
                include_bpm=include_bpm,
                include_energy=include_energy,
                min_bpm=min_bpm,
                max_bpm=max_bpm,
                energy_section_seconds=energy_section_seconds,
            )

    if cache:
        cache.save()

    return BatchAnalysisResult(
        directory=source,
        tracks=tuple(tracks),
        errors=tuple(errors),
        cache_warnings=tuple(cache.warnings if cache else ()),
    )
