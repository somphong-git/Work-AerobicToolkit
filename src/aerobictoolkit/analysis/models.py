"""Domain models returned by the audio-analysis engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class TrackMetadata:
    """Stable descriptive information about one local audio track."""

    path: Path
    title: str
    artist: str | None
    album: str | None
    duration_seconds: float | None
    file_format: str
    file_size_bytes: int

    def to_dict(self) -> dict[str, object]:
        """Return JSON-friendly metadata without exposing a ``Path`` object."""
        result = asdict(self)
        result["path"] = str(self.path)
        return result


@dataclass(frozen=True, slots=True)
class TrackAnalysis:
    """Metadata and derived audio metrics for one local track."""

    metadata: TrackMetadata
    bpm: float | None
    raw_bpm: float | None = None
    bpm_confidence: float | None = None
    beat_grid: BeatGrid | None = None
    energy: EnergyAnalysis | None = None
    musical_key: MusicalKeyAnalysis | None = None

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-friendly representation of the analysis result."""
        return {
            "metadata": self.metadata.to_dict(),
            "bpm": self.bpm,
            "raw_bpm": self.raw_bpm,
            "bpm_confidence": self.bpm_confidence,
            "confidence_level": self.confidence_level,
            "beat_grid": self.beat_grid.to_dict() if self.beat_grid else None,
            "energy": self.energy.to_dict() if self.energy else None,
            "musical_key": self.musical_key.to_dict() if self.musical_key else None,
        }

    @property
    def confidence_level(self) -> str | None:
        """Return a human-readable confidence band."""
        if self.bpm_confidence is None:
            return None
        if self.bpm_confidence >= 0.8:
            return "high"
        if self.bpm_confidence >= 0.5:
            return "medium"
        return "low"


@dataclass(frozen=True, slots=True)
class BeatGrid:
    """Normalized beat locations measured in seconds from track start."""

    times_seconds: tuple[float, ...]

    @property
    def beat_count(self) -> int:
        return len(self.times_seconds)

    @property
    def first_beat_seconds(self) -> float | None:
        return self.times_seconds[0] if self.times_seconds else None

    def to_dict(self) -> dict[str, object]:
        return {
            "beat_count": self.beat_count,
            "first_beat_seconds": self.first_beat_seconds,
            "times_seconds": list(self.times_seconds),
        }


@dataclass(frozen=True, slots=True)
class TempoAnalysis:
    """Raw and normalized tempo with confidence and beat timing."""

    raw_bpm: float
    normalized_bpm: float
    confidence: float
    beat_grid: BeatGrid


@dataclass(frozen=True, slots=True)
class EnergySection:
    """Energy score for one contiguous time range."""

    start_seconds: float
    end_seconds: float
    score: int

    @property
    def level(self) -> str:
        return energy_level(self.score)

    def to_dict(self) -> dict[str, object]:
        return {
            "start_seconds": self.start_seconds,
            "end_seconds": self.end_seconds,
            "score": self.score,
            "level": self.level,
        }


@dataclass(frozen=True, slots=True)
class EnergyAnalysis:
    """Overall perceptual energy and its timeline."""

    score: int
    rms_db: float
    onset_rate: float
    brightness: float
    section_seconds: float
    sections: tuple[EnergySection, ...]

    @property
    def level(self) -> str:
        return energy_level(self.score)

    def to_dict(self) -> dict[str, object]:
        return {
            "score": self.score,
            "level": self.level,
            "metrics": {
                "rms_db": self.rms_db,
                "onset_rate": self.onset_rate,
                "brightness": self.brightness,
            },
            "section_seconds": self.section_seconds,
            "sections": [section.to_dict() for section in self.sections],
        }


def energy_level(score: int) -> str:
    """Map an energy score from 1–10 to a stable descriptive level."""
    if not 1 <= score <= 10:
        raise ValueError("Energy score must be between 1 and 10.")
    if score <= 2:
        return "very-low"
    if score <= 4:
        return "low"
    if score <= 6:
        return "moderate"
    if score <= 8:
        return "high"
    return "peak"


@dataclass(frozen=True, slots=True)
class MusicalKeyAnalysis:
    """Detected musical key and DJ-oriented harmonic notation."""

    tonic: str
    mode: str
    camelot: str
    open_key: str
    confidence: float
    compatible_camelot: tuple[str, ...]
    compatible_open_key: tuple[str, ...]

    @property
    def name(self) -> str:
        return f"{self.tonic} {self.mode}"

    @property
    def confidence_level(self) -> str:
        if self.confidence >= 0.8:
            return "high"
        if self.confidence >= 0.5:
            return "medium"
        return "low"

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "tonic": self.tonic,
            "mode": self.mode,
            "camelot": self.camelot,
            "open_key": self.open_key,
            "confidence": self.confidence,
            "confidence_level": self.confidence_level,
            "compatible_camelot": list(self.compatible_camelot),
            "compatible_open_key": list(self.compatible_open_key),
        }


@dataclass(frozen=True, slots=True)
class BatchTrackAnalysis:
    """One successful analysis and whether it came from the cache."""

    analysis: TrackAnalysis
    from_cache: bool

    def to_dict(self) -> dict[str, object]:
        return {"from_cache": self.from_cache, "analysis": self.analysis.to_dict()}


@dataclass(frozen=True, slots=True)
class TrackAnalysisError:
    """A recoverable per-track failure captured during batch analysis."""

    path: Path
    error_type: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "path": str(self.path),
            "error_type": self.error_type,
            "message": self.message,
        }


@dataclass(frozen=True, slots=True)
class BatchAnalysisResult:
    """Complete outcome of analyzing a directory."""

    directory: Path
    tracks: tuple[BatchTrackAnalysis, ...]
    errors: tuple[TrackAnalysisError, ...]
    cache_warnings: tuple[str, ...] = ()
    generated_at: str = ""

    def __post_init__(self) -> None:
        if not self.generated_at:
            timestamp = datetime.now(UTC).isoformat()
            object.__setattr__(self, "generated_at", timestamp)

    @property
    def total_count(self) -> int:
        return len(self.tracks) + len(self.errors)

    @property
    def success_count(self) -> int:
        return len(self.tracks)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def cache_hit_count(self) -> int:
        return sum(track.from_cache for track in self.tracks)

    @property
    def analyzed_count(self) -> int:
        return self.success_count - self.cache_hit_count

    def to_dict(self) -> dict[str, object]:
        return {
            "directory": str(self.directory),
            "generated_at": self.generated_at,
            "summary": {
                "total": self.total_count,
                "successful": self.success_count,
                "errors": self.error_count,
                "cache_hits": self.cache_hit_count,
                "analyzed": self.analyzed_count,
            },
            "tracks": [track.to_dict() for track in self.tracks],
            "errors": [error.to_dict() for error in self.errors],
            "cache_warnings": list(self.cache_warnings),
        }
