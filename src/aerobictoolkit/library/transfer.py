"""Portable JSON/CSV transfer and SQLite backup services."""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path

from .catalog import DEFAULT_LIBRARY_PATH, LibraryCatalog
from .models import LibraryImportResult, LibraryQuery, LibraryTrack

TRANSFER_SCHEMA_VERSION = 1
CSV_FIELDS = (
    "path",
    "title",
    "artist",
    "album",
    "duration_seconds",
    "file_format",
    "file_size_bytes",
    "bpm",
    "bpm_confidence",
    "energy_score",
    "energy_level",
    "musical_key",
    "mode",
    "camelot",
    "open_key",
    "key_confidence",
    "indexed_at",
    "tags",
)
REQUIRED_FIELDS = {"path", "title", "file_format", "file_size_bytes"}
NUMERIC_FIELDS = {
    "duration_seconds": float,
    "file_size_bytes": int,
    "bpm": float,
    "bpm_confidence": float,
    "energy_score": int,
    "key_confidence": float,
}


def export_library(
    output_path: str | Path,
    *,
    database_path: str | Path = DEFAULT_LIBRARY_PATH,
) -> Path:
    """Export all catalog metadata to JSON or CSV based on the extension."""
    output = Path(output_path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    tracks = _read_all_tracks(database_path)
    records = [_portable_record(track) for track in tracks]
    if output.suffix.lower() == ".json":
        payload = {
            "schema_version": TRANSFER_SCHEMA_VERSION,
            "exported_at": datetime.now(UTC).isoformat(),
            "track_count": len(tracks),
            "tracks": records,
        }
        output.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    elif output.suffix.lower() == ".csv":
        with output.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
            writer.writeheader()
            for row in records:
                row["tags"] = json.dumps(row["tags"], ensure_ascii=False)
                writer.writerow({field: row.get(field) for field in CSV_FIELDS})
    else:
        raise ValueError("Export path must use a .json or .csv extension.")
    return output


def import_library(
    input_path: str | Path,
    *,
    database_path: str | Path = DEFAULT_LIBRARY_PATH,
) -> LibraryImportResult:
    """Import portable metadata, updating matching paths and merging tags."""
    source = Path(input_path).expanduser().resolve()
    records = _read_records(source)
    validated_records: list[dict[str, object]] = []
    for position, record in enumerate(records, start=1):
        try:
            validated_records.append(_validate_record(record))
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid track at row {position}: {error}") from error
    imported = 0
    updated = 0
    with LibraryCatalog(database_path) as catalog:
        for record in validated_records:
            _, existed = catalog.import_metadata(record)
            if existed:
                updated += 1
            else:
                imported += 1
    return LibraryImportResult(total=len(records), imported=imported, updated=updated)


def backup_library(
    output_path: str | Path,
    *,
    database_path: str | Path = DEFAULT_LIBRARY_PATH,
) -> Path:
    """Create a consistent copy of the SQLite catalog."""
    with LibraryCatalog(database_path) as catalog:
        return catalog.backup(output_path)


def _read_all_tracks(database_path: str | Path) -> list[LibraryTrack]:
    tracks: list[LibraryTrack] = []
    offset = 0
    with LibraryCatalog(database_path) as catalog:
        while True:
            page = catalog.search(LibraryQuery(limit=1000, offset=offset))
            tracks.extend(page)
            if len(page) < 1000:
                break
            offset += len(page)
    return tracks


def _portable_record(track: LibraryTrack) -> dict[str, object]:
    record = track.to_dict()
    record.pop("id")
    return record


def _read_records(source: Path) -> list[dict[str, object]]:
    if source.suffix.lower() == ".json":
        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid JSON: {error.msg}") from error
        if not isinstance(payload, dict):
            raise ValueError("JSON import must contain an object.")
        if payload.get("schema_version") != TRANSFER_SCHEMA_VERSION:
            raise ValueError("Unsupported or missing transfer schema version.")
        records = payload.get("tracks")
        if not isinstance(records, list):
            raise ValueError("JSON import must contain a tracks list.")
        return records
    if source.suffix.lower() == ".csv":
        with source.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))
    raise ValueError("Import path must use a .json or .csv extension.")


def _validate_record(record: object) -> dict[str, object]:
    if not isinstance(record, dict):
        raise TypeError("Track must be an object.")
    missing = sorted(field for field in REQUIRED_FIELDS if not record.get(field))
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    result = dict(record)
    for field, converter in NUMERIC_FIELDS.items():
        value = result.get(field)
        if value in (None, ""):
            result[field] = None
            continue
        try:
            result[field] = converter(value)
        except (TypeError, ValueError) as error:
            raise ValueError(f"{field} must be numeric") from error
    tags = result.get("tags", [])
    if isinstance(tags, str):
        try:
            tags = json.loads(tags) if tags else []
        except json.JSONDecodeError as error:
            raise ValueError("tags must contain a JSON array") from error
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        raise ValueError("tags must be a list of strings")
    result["tags"] = tags
    return result
