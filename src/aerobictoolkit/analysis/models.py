"""Domain models returned by the audio-analysis engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass
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
