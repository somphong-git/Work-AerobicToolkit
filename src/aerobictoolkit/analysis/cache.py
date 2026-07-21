"""Persistent cache for local audio-analysis results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import TrackAnalysis, TrackMetadata

CACHE_SCHEMA_VERSION = 1


class AnalysisCache:
    """Store results keyed by path, file fingerprint, and analysis profile."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser().resolve()
        self.warnings: list[str] = []
        self._entries: dict[str, dict[str, Any]] = {}
        self._load()

    def get(self, path: Path, *, include_bpm: bool) -> TrackAnalysis | None:
        """Return a current cached result, or ``None`` when it must be analyzed."""
        key = str(path.resolve())
        entry = self._entries.get(key)
        if entry is None or entry.get("fingerprint") != _fingerprint(path, include_bpm):
            return None

        try:
            return _analysis_from_dict(entry["analysis"])
        except (KeyError, TypeError, ValueError) as error:
            self.warnings.append(f"Ignored invalid cache entry for {path}: {error}")
            self._entries.pop(key, None)
            return None

    def put(self, analysis: TrackAnalysis, *, include_bpm: bool) -> None:
        """Stage one successful result for persistence."""
        path = analysis.metadata.path.resolve()
        self._entries[str(path)] = {
            "fingerprint": _fingerprint(path, include_bpm),
            "analysis": analysis.to_dict(),
        }

    def save(self) -> None:
        """Persist atomically; analysis remains usable if cache writing fails."""
        payload = {
            "schema_version": CACHE_SCHEMA_VERSION,
            "entries": self._entries,
        }
        temporary_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            temporary_path.replace(self.path)
        except OSError as error:
            self.warnings.append(f"Could not save analysis cache: {error}")

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise TypeError("cache root must be an object")
            if payload.get("schema_version") != CACHE_SCHEMA_VERSION:
                self.warnings.append(
                    "Ignored cache with an unsupported schema version."
                )
                return
            entries = payload.get("entries", {})
            if not isinstance(entries, dict):
                raise TypeError("entries must be an object")
            self._entries = entries
        except (OSError, json.JSONDecodeError, TypeError) as error:
            self.warnings.append(f"Ignored unreadable analysis cache: {error}")


def _fingerprint(path: Path, include_bpm: bool) -> dict[str, object]:
    stat = path.stat()
    return {
        "size": stat.st_size,
        "modified_ns": stat.st_mtime_ns,
        "profile": "metadata+bpm-v1" if include_bpm else "metadata-v1",
    }


def _analysis_from_dict(data: dict[str, Any]) -> TrackAnalysis:
    metadata_data = data["metadata"]
    metadata = TrackMetadata(
        path=Path(metadata_data["path"]),
        title=str(metadata_data["title"]),
        artist=metadata_data.get("artist"),
        album=metadata_data.get("album"),
        duration_seconds=metadata_data.get("duration_seconds"),
        file_format=str(metadata_data["file_format"]),
        file_size_bytes=int(metadata_data["file_size_bytes"]),
    )
    bpm = data.get("bpm")
    return TrackAnalysis(metadata=metadata, bpm=float(bpm) if bpm is not None else None)
