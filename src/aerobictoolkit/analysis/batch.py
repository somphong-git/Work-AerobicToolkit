"""Batch orchestration for directory-level audio analysis."""

from __future__ import annotations

from pathlib import Path

from .cache import AnalysisCache
from .models import BatchAnalysisResult, BatchTrackAnalysis, TrackAnalysisError
from .scanner import scan_music
from .service import analyze_track


def analyze_directory(
    directory: str | Path,
    *,
    include_bpm: bool = True,
    cache_path: str | Path | None = None,
) -> BatchAnalysisResult:
    """Analyze every supported file while isolating per-track failures."""
    source = Path(directory).expanduser().resolve()
    cache = AnalysisCache(cache_path) if cache_path is not None else None
    tracks: list[BatchTrackAnalysis] = []
    errors: list[TrackAnalysisError] = []

    for path in scan_music(source):
        cached = cache.get(path, include_bpm=include_bpm) if cache else None
        if cached is not None:
            tracks.append(BatchTrackAnalysis(cached, from_cache=True))
            continue

        try:
            analysis = analyze_track(path, include_bpm=include_bpm)
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
            cache.put(analysis, include_bpm=include_bpm)

    if cache:
        cache.save()

    return BatchAnalysisResult(
        directory=source,
        tracks=tuple(tracks),
        errors=tuple(errors),
        cache_warnings=tuple(cache.warnings if cache else ()),
    )
