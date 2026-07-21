"""JSON and CSV report adapters for batch audio analysis."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from aerobictoolkit.analysis.models import BatchAnalysisResult

CSV_FIELDS = (
    "status",
    "from_cache",
    "path",
    "title",
    "artist",
    "album",
    "duration_seconds",
    "file_format",
    "file_size_bytes",
    "raw_bpm",
    "bpm",
    "bpm_confidence",
    "confidence_level",
    "beat_count",
    "first_beat_seconds",
    "beat_times_seconds",
    "energy_score",
    "energy_level",
    "energy_rms_db",
    "energy_onset_rate",
    "energy_brightness",
    "energy_sections",
    "musical_key",
    "key_mode",
    "camelot",
    "open_key",
    "key_confidence",
    "key_confidence_level",
    "compatible_camelot",
    "compatible_open_key",
    "error_type",
    "error_message",
)


def write_json_report(result: BatchAnalysisResult, path: str | Path) -> Path:
    """Write the complete batch result as UTF-8 JSON."""
    report_path = _prepare_path(path)
    report_path.write_text(
        json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report_path


def write_csv_report(result: BatchAnalysisResult, path: str | Path) -> Path:
    """Write one flat UTF-8 CSV row per successful or failed track."""
    report_path = _prepare_path(path)
    with report_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for item in result.tracks:
            metadata = item.analysis.metadata
            writer.writerow(
                {
                    "status": "success",
                    "from_cache": item.from_cache,
                    "path": metadata.path,
                    "title": metadata.title,
                    "artist": metadata.artist,
                    "album": metadata.album,
                    "duration_seconds": metadata.duration_seconds,
                    "file_format": metadata.file_format,
                    "file_size_bytes": metadata.file_size_bytes,
                    "raw_bpm": item.analysis.raw_bpm,
                    "bpm": item.analysis.bpm,
                    "bpm_confidence": item.analysis.bpm_confidence,
                    "confidence_level": item.analysis.confidence_level,
                    "beat_count": (
                        item.analysis.beat_grid.beat_count
                        if item.analysis.beat_grid
                        else 0
                    ),
                    "first_beat_seconds": (
                        item.analysis.beat_grid.first_beat_seconds
                        if item.analysis.beat_grid
                        else ""
                    ),
                    "beat_times_seconds": (
                        json.dumps(item.analysis.beat_grid.times_seconds)
                        if item.analysis.beat_grid
                        else ""
                    ),
                    "energy_score": (
                        item.analysis.energy.score if item.analysis.energy else ""
                    ),
                    "energy_level": (
                        item.analysis.energy.level if item.analysis.energy else ""
                    ),
                    "energy_rms_db": (
                        item.analysis.energy.rms_db if item.analysis.energy else ""
                    ),
                    "energy_onset_rate": (
                        item.analysis.energy.onset_rate if item.analysis.energy else ""
                    ),
                    "energy_brightness": (
                        item.analysis.energy.brightness if item.analysis.energy else ""
                    ),
                    "energy_sections": (
                        json.dumps(
                            [
                                section.to_dict()
                                for section in item.analysis.energy.sections
                            ]
                        )
                        if item.analysis.energy
                        else ""
                    ),
                    "musical_key": (
                        item.analysis.musical_key.name
                        if item.analysis.musical_key
                        else ""
                    ),
                    "key_mode": (
                        item.analysis.musical_key.mode
                        if item.analysis.musical_key
                        else ""
                    ),
                    "camelot": (
                        item.analysis.musical_key.camelot
                        if item.analysis.musical_key
                        else ""
                    ),
                    "open_key": (
                        item.analysis.musical_key.open_key
                        if item.analysis.musical_key
                        else ""
                    ),
                    "key_confidence": (
                        item.analysis.musical_key.confidence
                        if item.analysis.musical_key
                        else ""
                    ),
                    "key_confidence_level": (
                        item.analysis.musical_key.confidence_level
                        if item.analysis.musical_key
                        else ""
                    ),
                    "compatible_camelot": (
                        json.dumps(item.analysis.musical_key.compatible_camelot)
                        if item.analysis.musical_key
                        else ""
                    ),
                    "compatible_open_key": (
                        json.dumps(item.analysis.musical_key.compatible_open_key)
                        if item.analysis.musical_key
                        else ""
                    ),
                    "error_type": "",
                    "error_message": "",
                }
            )
        for error in result.errors:
            writer.writerow(
                {
                    "status": "error",
                    "from_cache": False,
                    "path": error.path,
                    "title": "",
                    "artist": "",
                    "album": "",
                    "duration_seconds": "",
                    "file_format": error.path.suffix.removeprefix(".").lower(),
                    "file_size_bytes": "",
                    "raw_bpm": "",
                    "bpm": "",
                    "bpm_confidence": "",
                    "confidence_level": "",
                    "beat_count": "",
                    "first_beat_seconds": "",
                    "beat_times_seconds": "",
                    "energy_score": "",
                    "energy_level": "",
                    "energy_rms_db": "",
                    "energy_onset_rate": "",
                    "energy_brightness": "",
                    "energy_sections": "",
                    "musical_key": "",
                    "key_mode": "",
                    "camelot": "",
                    "open_key": "",
                    "key_confidence": "",
                    "key_confidence_level": "",
                    "compatible_camelot": "",
                    "compatible_open_key": "",
                    "error_type": error.error_type,
                    "error_message": error.message,
                }
            )
    return report_path


def _prepare_path(path: str | Path) -> Path:
    report_path = Path(path).expanduser().resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    return report_path
