"""Persistent cache for local audio-analysis results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import (
    BeatGrid,
    EnergyAnalysis,
    EnergySection,
    MusicalKeyAnalysis,
    TrackAnalysis,
    TrackMetadata,
)

CACHE_SCHEMA_VERSION = 4


class AnalysisCache:
    """Store results keyed by path, file fingerprint, and analysis profile."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser().resolve()
        self.warnings: list[str] = []
        self._entries: dict[str, dict[str, Any]] = {}
        self._load()

    def get(
        self,
        path: Path,
        *,
        include_bpm: bool,
        include_energy: bool,
        include_key: bool,
        min_bpm: float,
        max_bpm: float,
        energy_section_seconds: float,
    ) -> TrackAnalysis | None:
        """Return a current cached result, or ``None`` when it must be analyzed."""
        key = str(path.resolve())
        entry = self._entries.get(key)
        fingerprint = _fingerprint(
            path,
            include_bpm,
            include_energy,
            include_key,
            min_bpm,
            max_bpm,
            energy_section_seconds,
        )
        if entry is None or entry.get("fingerprint") != fingerprint:
            return None

        try:
            return _analysis_from_dict(entry["analysis"])
        except (KeyError, TypeError, ValueError) as error:
            self.warnings.append(f"Ignored invalid cache entry for {path}: {error}")
            self._entries.pop(key, None)
            return None

    def put(
        self,
        analysis: TrackAnalysis,
        *,
        include_bpm: bool,
        include_energy: bool,
        include_key: bool,
        min_bpm: float,
        max_bpm: float,
        energy_section_seconds: float,
    ) -> None:
        """Stage one successful result for persistence."""
        path = analysis.metadata.path.resolve()
        self._entries[str(path)] = {
            "fingerprint": _fingerprint(
                path,
                include_bpm,
                include_energy,
                include_key,
                min_bpm,
                max_bpm,
                energy_section_seconds,
            ),
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


def _fingerprint(
    path: Path,
    include_bpm: bool,
    include_energy: bool,
    include_key: bool,
    min_bpm: float,
    max_bpm: float,
    energy_section_seconds: float,
) -> dict[str, object]:
    stat = path.stat()
    return {
        "size": stat.st_size,
        "modified_ns": stat.st_mtime_ns,
        "profile": {
            "tempo": "confidence+beat-grid-v1" if include_bpm else None,
            "energy": "perceptual-energy-v1" if include_energy else None,
            "musical_key": "krumhansl-cqt-v1" if include_key else None,
        },
        "tempo_range": [min_bpm, max_bpm] if include_bpm else None,
        "energy_section_seconds": energy_section_seconds if include_energy else None,
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
    raw_bpm = data.get("raw_bpm")
    confidence = data.get("bpm_confidence")
    beat_grid_data = data.get("beat_grid")
    beat_grid = None
    if beat_grid_data is not None:
        beat_grid = BeatGrid(
            tuple(float(value) for value in beat_grid_data.get("times_seconds", ()))
        )
    energy_data = data.get("energy")
    energy = None
    if energy_data is not None:
        metrics = energy_data["metrics"]
        energy = EnergyAnalysis(
            score=int(energy_data["score"]),
            rms_db=float(metrics["rms_db"]),
            onset_rate=float(metrics["onset_rate"]),
            brightness=float(metrics["brightness"]),
            section_seconds=float(energy_data["section_seconds"]),
            sections=tuple(
                EnergySection(
                    start_seconds=float(section["start_seconds"]),
                    end_seconds=float(section["end_seconds"]),
                    score=int(section["score"]),
                )
                for section in energy_data.get("sections", ())
            ),
        )
    key_data = data.get("musical_key")
    musical_key = None
    if key_data is not None:
        musical_key = MusicalKeyAnalysis(
            tonic=str(key_data["tonic"]),
            mode=str(key_data["mode"]),
            camelot=str(key_data["camelot"]),
            open_key=str(key_data["open_key"]),
            confidence=float(key_data["confidence"]),
            compatible_camelot=tuple(key_data.get("compatible_camelot", ())),
            compatible_open_key=tuple(key_data.get("compatible_open_key", ())),
        )
    return TrackAnalysis(
        metadata=metadata,
        bpm=float(bpm) if bpm is not None else None,
        raw_bpm=float(raw_bpm) if raw_bpm is not None else None,
        bpm_confidence=float(confidence) if confidence is not None else None,
        beat_grid=beat_grid,
        energy=energy,
        musical_key=musical_key,
    )
