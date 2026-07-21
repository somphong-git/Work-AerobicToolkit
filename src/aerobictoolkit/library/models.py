"""Public data contracts for the local music library."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class LibraryQuery:
    """Search and filter criteria shared by every future interface."""

    text: str | None = None
    min_bpm: float | None = None
    max_bpm: float | None = None
    min_energy: int | None = None
    max_energy: int | None = None
    camelot: str | None = None
    mode: str | None = None
    file_format: str | None = None
    tags: tuple[str, ...] = ()
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True, slots=True)
class LibraryTrack:
    """One catalog entry with searchable analysis fields and user tags."""

    id: int
    path: Path
    title: str
    artist: str | None
    album: str | None
    duration_seconds: float | None
    file_format: str
    file_size_bytes: int
    bpm: float | None
    bpm_confidence: float | None
    energy_score: int | None
    energy_level: str | None
    musical_key: str | None
    mode: str | None
    camelot: str | None
    open_key: str | None
    key_confidence: float | None
    indexed_at: str
    tags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        result = asdict(self)
        result["path"] = str(self.path)
        result["tags"] = list(self.tags)
        return result


@dataclass(frozen=True, slots=True)
class LibraryIndexResult:
    """Outcome of batch analysis followed by catalog persistence."""

    discovered: int
    indexed: int
    errors: int
    cache_hits: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)
