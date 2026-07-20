"""Application-facing services for core audio analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import TrackAnalysis, TrackMetadata


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


def estimate_bpm(path: str | Path) -> float:
    """Estimate a track's BPM using librosa's beat tracker.

    Install the ``analysis`` extra before calling this capability:
    ``pip install -e '.[analysis]'``.
    """
    track_path = Path(path).expanduser().resolve()
    if not track_path.is_file():
        message = f"Audio file does not exist: {track_path}"
        raise FileNotFoundError(message)

    librosa = _load_librosa()
    samples, sample_rate = librosa.load(track_path, mono=True, sr=None)
    tempo, _ = librosa.beat.beat_track(y=samples, sr=sample_rate)
    return round(_scalar_tempo(tempo), 2)


def analyze_track(path: str | Path, *, include_bpm: bool = True) -> TrackAnalysis:
    """Return metadata and, optionally, an estimated BPM for one track."""
    metadata = read_track_metadata(path)
    bpm = estimate_bpm(metadata.path) if include_bpm else None
    return TrackAnalysis(metadata=metadata, bpm=bpm)


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
