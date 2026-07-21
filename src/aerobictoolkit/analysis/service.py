"""Application-facing services for core audio analysis."""

from __future__ import annotations

from pathlib import Path
from statistics import median
from typing import Any

from .models import BeatGrid, TempoAnalysis, TrackAnalysis, TrackMetadata

DEFAULT_MIN_BPM = 90.0
DEFAULT_MAX_BPM = 180.0


class AudioAnalysisDependencyError(RuntimeError):
    """Raised when an optional analysis dependency has not been installed."""


def read_track_metadata(path: str | Path) -> TrackMetadata:
    """Read file and tag metadata for one supported local audio file.

    Missing tags are normal. The filename stem is used as a dependable title
    fallback, so callers always receive a displayable track title.
    """
    track_path = Path(path).expanduser().resolve()
    if not track_path.is_file():
        message = f"Audio file does not exist: {track_path}"
        raise FileNotFoundError(message)

    audio = _load_mutagen_file()(track_path, easy=True)
    tags: dict[str, list[str]] = audio if audio is not None else {}
    info: Any = getattr(audio, "info", None)
    duration = getattr(info, "length", None)

    return TrackMetadata(
        path=track_path,
        title=_first_tag(tags, "title") or track_path.stem,
        artist=_first_tag(tags, "artist"),
        album=_first_tag(tags, "album"),
        duration_seconds=round(float(duration), 3) if duration is not None else None,
        file_format=track_path.suffix.removeprefix(".").lower(),
        file_size_bytes=track_path.stat().st_size,
    )


def analyze_tempo(
    path: str | Path,
    *,
    min_bpm: float = DEFAULT_MIN_BPM,
    max_bpm: float = DEFAULT_MAX_BPM,
) -> TempoAnalysis:
    """Analyze normalized tempo, confidence, and beat locations.

    Install the ``analysis`` extra before calling this capability:
    ``pip install -e '.[analysis]'``.
    """
    _validate_tempo_range(min_bpm, max_bpm)
    track_path = Path(path).expanduser().resolve()
    if not track_path.is_file():
        message = f"Audio file does not exist: {track_path}"
        raise FileNotFoundError(message)

    librosa = _load_librosa()
    samples, sample_rate = librosa.load(track_path, mono=True, sr=None)
    onset_envelope = librosa.onset.onset_strength(y=samples, sr=sample_rate)
    tempo, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset_envelope, sr=sample_rate
    )
    tempo_candidates = librosa.feature.tempo(
        onset_envelope=onset_envelope,
        sr=sample_rate,
        aggregate=None,
    )
    raw_bpm = _scalar_tempo(tempo)
    normalized_bpm = normalize_tempo(raw_bpm, min_bpm=min_bpm, max_bpm=max_bpm)
    detected_beats = _float_values(librosa.frames_to_time(beat_frames, sr=sample_rate))
    normalized_beats = _normalize_beat_grid(
        detected_beats, raw_bpm=raw_bpm, normalized_bpm=normalized_bpm
    )
    confidence = _tempo_confidence(
        normalized_beats,
        _float_values(tempo_candidates),
        normalized_bpm=normalized_bpm,
        min_bpm=min_bpm,
        max_bpm=max_bpm,
    )
    return TempoAnalysis(
        raw_bpm=round(raw_bpm, 2),
        normalized_bpm=round(normalized_bpm, 2),
        confidence=confidence,
        beat_grid=BeatGrid(tuple(round(value, 6) for value in normalized_beats)),
    )


def estimate_bpm(
    path: str | Path,
    *,
    min_bpm: float = DEFAULT_MIN_BPM,
    max_bpm: float = DEFAULT_MAX_BPM,
) -> float:
    """Return the normalized BPM for callers that only need one value."""
    return analyze_tempo(path, min_bpm=min_bpm, max_bpm=max_bpm).normalized_bpm


def analyze_track(
    path: str | Path,
    *,
    include_bpm: bool = True,
    min_bpm: float = DEFAULT_MIN_BPM,
    max_bpm: float = DEFAULT_MAX_BPM,
) -> TrackAnalysis:
    """Return metadata and, optionally, an estimated BPM for one track."""
    metadata = read_track_metadata(path)
    if not include_bpm:
        return TrackAnalysis(metadata=metadata, bpm=None)

    tempo = analyze_tempo(metadata.path, min_bpm=min_bpm, max_bpm=max_bpm)
    return TrackAnalysis(
        metadata=metadata,
        bpm=tempo.normalized_bpm,
        raw_bpm=tempo.raw_bpm,
        bpm_confidence=tempo.confidence,
        beat_grid=tempo.beat_grid,
    )


def normalize_tempo(
    bpm: float,
    *,
    min_bpm: float = DEFAULT_MIN_BPM,
    max_bpm: float = DEFAULT_MAX_BPM,
) -> float:
    """Move a positive BPM by octaves into the configured target range."""
    _validate_tempo_range(min_bpm, max_bpm)
    if bpm <= 0:
        raise ValueError("BPM must be greater than zero.")

    normalized = float(bpm)
    while normalized < min_bpm:
        normalized *= 2
    while normalized > max_bpm:
        normalized /= 2
    return round(normalized, 2)


def _first_tag(tags: dict[str, list[str]], name: str) -> str | None:
    values = tags.get(name)
    return values[0].strip() if values and values[0].strip() else None


def _load_mutagen_file() -> Any:
    """Load the metadata adapter lazily to keep import costs at the edge."""
    try:
        from mutagen import File as mutagen_file
    except ImportError as error:  # pragma: no cover - declared runtime dependency
        raise AudioAnalysisDependencyError(
            "Metadata analysis requires mutagen. Reinstall Work-AerobicToolkit."
        ) from error
    return mutagen_file


def _load_librosa() -> Any:
    """Load the BPM adapter only when BPM estimation is requested."""
    try:
        import librosa
    except ImportError as error:
        raise AudioAnalysisDependencyError(
            "BPM analysis requires the analysis extra. "
            "Install it with: pip install -e '.[analysis]'"
        ) from error
    return librosa


def _scalar_tempo(tempo: Any) -> float:
    """Normalize librosa's scalar or ndarray tempo return value."""
    try:
        return float(tempo.item())
    except AttributeError:
        return float(tempo)


def _float_values(values: Any) -> list[float]:
    try:
        unpacked = values.tolist()
    except AttributeError:
        unpacked = values
    if isinstance(unpacked, (int, float)):
        return [float(unpacked)]
    return [float(value) for value in unpacked]


def _normalize_beat_grid(
    beat_times: list[float], *, raw_bpm: float, normalized_bpm: float
) -> list[float]:
    if len(beat_times) < 2 or raw_bpm <= 0:
        return beat_times

    ratio = normalized_bpm / raw_bpm
    if ratio > 1:
        subdivisions = max(1, round(ratio))
        expanded: list[float] = []
        for start, end in zip(beat_times, beat_times[1:], strict=False):
            interval = (end - start) / subdivisions
            expanded.extend(start + interval * step for step in range(subdivisions))
        expanded.append(beat_times[-1])
        return expanded

    if ratio < 1:
        stride = max(1, round(1 / ratio))
        return beat_times[::stride]
    return beat_times


def _tempo_confidence(
    beat_times: list[float],
    tempo_candidates: list[float],
    *,
    normalized_bpm: float,
    min_bpm: float,
    max_bpm: float,
) -> float:
    intervals = [
        end - start for start, end in zip(beat_times, beat_times[1:], strict=False)
    ]
    regularity = 0.0
    if intervals:
        typical_interval = median(intervals)
        if typical_interval > 0:
            deviation = median(abs(value - typical_interval) for value in intervals)
            regularity = max(0.0, 1.0 - min(1.0, 4 * deviation / typical_interval))

    normalized_candidates = [
        normalize_tempo(value, min_bpm=min_bpm, max_bpm=max_bpm)
        for value in tempo_candidates
        if value > 0
    ]
    agreement = 0.0
    if normalized_candidates:
        agreement_scores = [
            max(0.0, 1.0 - abs(value - normalized_bpm) / (normalized_bpm * 0.08))
            for value in normalized_candidates
        ]
        agreement = sum(agreement_scores) / len(agreement_scores)

    beat_support = min(1.0, len(beat_times) / 32)
    return round(0.55 * regularity + 0.3 * agreement + 0.15 * beat_support, 3)


def _validate_tempo_range(min_bpm: float, max_bpm: float) -> None:
    if min_bpm <= 0 or max_bpm < min_bpm * 2:
        raise ValueError(
            "Tempo range must be positive and span at least one octave "
            "(max BPM >= 2 × min BPM)."
        )
