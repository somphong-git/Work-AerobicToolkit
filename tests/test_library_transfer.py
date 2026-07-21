import json
from pathlib import Path

import pytest

from aerobictoolkit.library import (
    LibraryCatalog,
    backup_library,
    export_library,
    import_library,
)

from .test_library import make_analysis


@pytest.mark.parametrize("extension", ["json", "csv"])
def test_export_import_round_trip_preserves_metadata_and_tags(
    tmp_path: Path, extension: str
) -> None:
    source_db = tmp_path / "source.db"
    track_path = tmp_path / "เพลง.wav"
    with LibraryCatalog(source_db) as catalog:
        catalog.upsert(make_analysis(track_path, title="เพลงทดสอบ"))
        catalog.add_tags(track_path, ["แอโรบิก", "Peak, Hour"])
    transfer = export_library(
        tmp_path / f"library.{extension}", database_path=source_db
    )

    result = import_library(transfer, database_path=tmp_path / "target.db")

    assert result.total == 1
    assert result.imported == 1
    assert result.updated == 0
    with LibraryCatalog(tmp_path / "target.db") as catalog:
        imported = catalog.get(track_path)
        assert imported is not None
        assert imported.title == "เพลงทดสอบ"
        assert imported.bpm == 128.0
        assert imported.energy_score == 8
        assert imported.camelot == "8A"
        assert imported.tags == ("แอโรบิก", "Peak, Hour")


def test_import_updates_existing_track_and_merges_tags(tmp_path: Path) -> None:
    database = tmp_path / "catalog.db"
    track_path = tmp_path / "track.wav"
    with LibraryCatalog(database) as catalog:
        catalog.upsert(make_analysis(track_path, title="Old"))
        catalog.add_tags(track_path, ["Local"])
    payload = {
        "schema_version": 1,
        "tracks": [
            {
                "path": str(track_path),
                "title": "Imported",
                "artist": None,
                "album": None,
                "duration_seconds": 200,
                "file_format": "wav",
                "file_size_bytes": 42,
                "bpm": 130,
                "tags": ["Shared"],
            }
        ],
    }
    source = tmp_path / "import.json"
    source.write_text(json.dumps(payload), encoding="utf-8")

    result = import_library(source, database_path=database)

    assert result.updated == 1
    with LibraryCatalog(database) as catalog:
        track = catalog.get(track_path)
        assert track is not None
        assert track.title == "Imported"
        assert track.tags == ("Local", "Shared")


def test_backup_is_a_readable_independent_catalog(tmp_path: Path) -> None:
    source = tmp_path / "catalog.db"
    track_path = tmp_path / "track.wav"
    with LibraryCatalog(source) as catalog:
        catalog.upsert(make_analysis(track_path))

    backup = backup_library(tmp_path / "backups" / "catalog.db", database_path=source)

    assert backup.exists()
    with LibraryCatalog(backup) as catalog:
        assert catalog.get(track_path) is not None


@pytest.mark.parametrize(
    ("name", "content", "message"),
    [
        ("bad.txt", "anything", "json or .csv"),
        ("bad.json", "{}", "schema version"),
        (
            "missing.json",
            json.dumps({"schema_version": 1, "tracks": [{}]}),
            "Missing required fields",
        ),
    ],
)
def test_import_rejects_unsupported_or_invalid_data(
    tmp_path: Path, name: str, content: str, message: str
) -> None:
    source = tmp_path / name
    source.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        import_library(source, database_path=tmp_path / "catalog.db")


def test_export_rejects_unknown_extension(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="json or .csv"):
        export_library(tmp_path / "library.txt", database_path=tmp_path / "catalog.db")


def test_backup_rejects_catalog_as_destination(tmp_path: Path) -> None:
    database = tmp_path / "catalog.db"
    with pytest.raises(ValueError, match="must differ"):
        backup_library(database, database_path=database)
