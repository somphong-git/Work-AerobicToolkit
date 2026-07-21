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

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-friendly representation of the analysis result."""
        return {"metadata": self.metadata.to_dict(), "bpm": self.bpm}


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
