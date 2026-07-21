"""SQLite-backed local music catalog."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from aerobictoolkit.analysis import TrackAnalysis

from .models import LibraryQuery, LibraryTrack

SCHEMA_VERSION = 1
DEFAULT_LIBRARY_PATH = Path("data/library/catalog.sqlite3")


class LibraryCatalog:
    """Persist and query analyzed tracks without coupling to a user interface."""

    def __init__(self, database_path: str | Path = DEFAULT_LIBRARY_PATH) -> None:
        self.path = Path(database_path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._initialize()

    def __enter__(self) -> LibraryCatalog:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self._connection.close()

    def upsert(self, analysis: TrackAnalysis) -> LibraryTrack:
        """Insert or refresh analysis fields while preserving user tags."""
        metadata = analysis.metadata
        key = analysis.musical_key
        energy = analysis.energy
        path = str(metadata.path.expanduser().resolve())
        values = (
            path,
            metadata.title,
            metadata.artist,
            metadata.album,
            metadata.duration_seconds,
            metadata.file_format.lower(),
            metadata.file_size_bytes,
            analysis.bpm,
            analysis.bpm_confidence,
            energy.score if energy else None,
            energy.level if energy else None,
            key.name if key else None,
            key.mode if key else None,
            key.camelot if key else None,
            key.open_key if key else None,
            key.confidence if key else None,
            datetime.now(UTC).isoformat(),
            json.dumps(analysis.to_dict(), ensure_ascii=False),
        )
        self._connection.execute(
            """
            INSERT INTO tracks (
                path, title, artist, album, duration_seconds, file_format,
                file_size_bytes, bpm, bpm_confidence, energy_score, energy_level,
                musical_key, mode, camelot, open_key, key_confidence, indexed_at,
                analysis_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                title=excluded.title, artist=excluded.artist, album=excluded.album,
                duration_seconds=excluded.duration_seconds,
                file_format=excluded.file_format,
                file_size_bytes=excluded.file_size_bytes, bpm=excluded.bpm,
                bpm_confidence=excluded.bpm_confidence,
                energy_score=excluded.energy_score, energy_level=excluded.energy_level,
                musical_key=excluded.musical_key, mode=excluded.mode,
                camelot=excluded.camelot, open_key=excluded.open_key,
                key_confidence=excluded.key_confidence, indexed_at=excluded.indexed_at,
                analysis_json=excluded.analysis_json
            """,
            values,
        )
        self._connection.commit()
        track = self.get(path)
        if track is None:  # pragma: no cover - database invariant
            raise RuntimeError("Catalog did not return the indexed track.")
        return track

    def get(self, path: str | Path) -> LibraryTrack | None:
        resolved = str(Path(path).expanduser().resolve())
        rows = self._select("WHERE t.path = ?", [resolved], limit=1, offset=0)
        return rows[0] if rows else None

    def search(self, query: LibraryQuery | None = None) -> tuple[LibraryTrack, ...]:
        """Find tracks using text, metric, harmonic, format, and tag filters."""
        query = query or LibraryQuery()
        self._validate_query(query)
        clauses: list[str] = []
        parameters: list[object] = []
        if query.text:
            pattern = f"%{_escape_like(query.text.strip())}%"
            clauses.append(
                "(t.title LIKE ? ESCAPE '\\' OR COALESCE(t.artist, '') LIKE ? "
                "ESCAPE '\\' OR COALESCE(t.album, '') LIKE ? ESCAPE '\\' "
                "OR t.path LIKE ? ESCAPE '\\')"
            )
            parameters.extend([pattern] * 4)
        filters = (
            (query.min_bpm, "t.bpm >= ?"),
            (query.max_bpm, "t.bpm <= ?"),
            (query.min_energy, "t.energy_score >= ?"),
            (query.max_energy, "t.energy_score <= ?"),
        )
        for value, clause in filters:
            if value is not None:
                clauses.append(clause)
                parameters.append(value)
        for value, column in (
            (query.camelot, "t.camelot"),
            (query.mode, "t.mode"),
            (query.file_format, "t.file_format"),
        ):
            if value:
                clauses.append(f"LOWER({column}) = ?")
                parameters.append(value.strip().lower())
        for tag in _normalize_tags(query.tags):
            clauses.append(
                "EXISTS (SELECT 1 FROM track_tags qtt "
                "JOIN tags qt ON qt.id = qtt.tag_id "
                "WHERE qtt.track_id = t.id AND qt.normalized_name = ?)"
            )
            parameters.append(tag.casefold())
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        return tuple(self._select(where, parameters, query.limit, query.offset))

    def add_tags(self, path: str | Path, tags: Iterable[str]) -> LibraryTrack:
        track = self._require_track(path)
        normalized = _normalize_tags(tags)
        if not normalized:
            raise ValueError("Provide at least one non-empty tag.")
        for tag in normalized:
            self._connection.execute(
                "INSERT OR IGNORE INTO tags (name, normalized_name) VALUES (?, ?)",
                (tag, tag.casefold()),
            )
            self._connection.execute(
                """INSERT OR IGNORE INTO track_tags (track_id, tag_id)
                SELECT ?, id FROM tags WHERE normalized_name = ?""",
                (track.id, tag.casefold()),
            )
        self._connection.commit()
        return self._require_track(path)

    def remove_tags(self, path: str | Path, tags: Iterable[str]) -> LibraryTrack:
        track = self._require_track(path)
        normalized = _normalize_tags(tags)
        if not normalized:
            raise ValueError("Provide at least one non-empty tag.")
        placeholders = ", ".join("?" for _ in normalized)
        self._connection.execute(
            f"""DELETE FROM track_tags WHERE track_id = ? AND tag_id IN
            (SELECT id FROM tags WHERE normalized_name IN ({placeholders}))""",
            [track.id, *(tag.casefold() for tag in normalized)],
        )
        self._connection.execute(
            "DELETE FROM tags WHERE NOT EXISTS "
            "(SELECT 1 FROM track_tags WHERE track_tags.tag_id = tags.id)"
        )
        self._connection.commit()
        return self._require_track(path)

    def list_tags(self) -> tuple[tuple[str, int], ...]:
        rows = self._connection.execute(
            """SELECT tags.name, COUNT(track_tags.track_id) AS track_count
            FROM tags JOIN track_tags ON track_tags.tag_id = tags.id
            GROUP BY tags.id ORDER BY tags.normalized_name"""
        ).fetchall()
        return tuple((row["name"], row["track_count"]) for row in rows)

    def import_metadata(self, record: dict[str, object]) -> tuple[LibraryTrack, bool]:
        """Upsert one validated portable record and merge its tags."""
        path = str(Path(str(record["path"])).expanduser().resolve())
        existed = self.get(path) is not None
        indexed_at = str(record.get("indexed_at") or datetime.now(UTC).isoformat())
        values = (
            path,
            str(record["title"]),
            _optional_string(record.get("artist")),
            _optional_string(record.get("album")),
            record.get("duration_seconds"),
            str(record["file_format"]).lower(),
            int(record["file_size_bytes"]),
            record.get("bpm"),
            record.get("bpm_confidence"),
            record.get("energy_score"),
            _optional_string(record.get("energy_level")),
            _optional_string(record.get("musical_key")),
            _optional_string(record.get("mode")),
            _optional_string(record.get("camelot")),
            _optional_string(record.get("open_key")),
            record.get("key_confidence"),
            indexed_at,
            json.dumps(record, ensure_ascii=False),
        )
        self._connection.execute(
            """INSERT INTO tracks (
                path, title, artist, album, duration_seconds, file_format,
                file_size_bytes, bpm, bpm_confidence, energy_score, energy_level,
                musical_key, mode, camelot, open_key, key_confidence, indexed_at,
                analysis_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                title=excluded.title, artist=excluded.artist, album=excluded.album,
                duration_seconds=excluded.duration_seconds,
                file_format=excluded.file_format,
                file_size_bytes=excluded.file_size_bytes, bpm=excluded.bpm,
                bpm_confidence=excluded.bpm_confidence,
                energy_score=excluded.energy_score, energy_level=excluded.energy_level,
                musical_key=excluded.musical_key, mode=excluded.mode,
                camelot=excluded.camelot, open_key=excluded.open_key,
                key_confidence=excluded.key_confidence, indexed_at=excluded.indexed_at,
                analysis_json=excluded.analysis_json""",
            values,
        )
        self._connection.commit()
        tags = record.get("tags", [])
        if tags:
            if not isinstance(tags, list) or not all(
                isinstance(tag, str) for tag in tags
            ):
                raise ValueError("Track tags must be a list of strings.")
            self.add_tags(path, tags)
        track = self.get(path)
        if track is None:  # pragma: no cover - database invariant
            raise RuntimeError("Catalog did not return the imported track.")
        return track, existed

    def backup(self, destination: str | Path) -> Path:
        """Create a transactionally consistent SQLite backup."""
        target = Path(destination).expanduser().resolve()
        if target == self.path:
            raise ValueError("Backup destination must differ from the catalog path.")
        target.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(target) as backup_connection:
            self._connection.backup(backup_connection)
        return target

    def _require_track(self, path: str | Path) -> LibraryTrack:
        track = self.get(path)
        if track is None:
            raise ValueError(f"Track is not indexed: {Path(path)}")
        return track

    def _select(
        self, where: str, parameters: list[object], limit: int, offset: int
    ) -> list[LibraryTrack]:
        rows = self._connection.execute(
            f"""SELECT t.*, GROUP_CONCAT(tags.name, char(31)) AS tag_names
            FROM tracks t
            LEFT JOIN track_tags tt ON tt.track_id = t.id
            LEFT JOIN tags ON tags.id = tt.tag_id
            {where}
            GROUP BY t.id ORDER BY t.title COLLATE NOCASE, t.path
            LIMIT ? OFFSET ?""",
            [*parameters, limit, offset],
        ).fetchall()
        return [_row_to_track(row) for row in rows]

    def _initialize(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS schema_info (
                version INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                artist TEXT,
                album TEXT,
                duration_seconds REAL,
                file_format TEXT NOT NULL,
                file_size_bytes INTEGER NOT NULL,
                bpm REAL,
                bpm_confidence REAL,
                energy_score INTEGER,
                energy_level TEXT,
                musical_key TEXT,
                mode TEXT,
                camelot TEXT,
                open_key TEXT,
                key_confidence REAL,
                indexed_at TEXT NOT NULL,
                analysis_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                normalized_name TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS track_tags (
                track_id INTEGER NOT NULL REFERENCES tracks(id) ON DELETE CASCADE,
                tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
                PRIMARY KEY (track_id, tag_id)
            );
            CREATE INDEX IF NOT EXISTS idx_tracks_bpm ON tracks(bpm);
            CREATE INDEX IF NOT EXISTS idx_tracks_energy ON tracks(energy_score);
            CREATE INDEX IF NOT EXISTS idx_tracks_camelot ON tracks(camelot);
            CREATE INDEX IF NOT EXISTS idx_tracks_format ON tracks(file_format);
            """
        )
        row = self._connection.execute(
            "SELECT version FROM schema_info LIMIT 1"
        ).fetchone()
        if row is None:
            self._connection.execute(
                "INSERT INTO schema_info (version) VALUES (?)", (SCHEMA_VERSION,)
            )
        elif row["version"] != SCHEMA_VERSION:
            raise RuntimeError(
                f"Unsupported catalog schema {row['version']}; "
                f"expected {SCHEMA_VERSION}."
            )
        self._connection.commit()

    @staticmethod
    def _validate_query(query: LibraryQuery) -> None:
        if query.limit < 1 or query.limit > 1000:
            raise ValueError("Search limit must be between 1 and 1000.")
        if query.offset < 0:
            raise ValueError("Search offset cannot be negative.")
        if (
            query.min_bpm is not None
            and query.max_bpm is not None
            and query.min_bpm > query.max_bpm
        ):
            raise ValueError("Minimum BPM cannot exceed maximum BPM.")
        if query.min_energy is not None and not 1 <= query.min_energy <= 10:
            raise ValueError("Minimum energy must be between 1 and 10.")
        if query.max_energy is not None and not 1 <= query.max_energy <= 10:
            raise ValueError("Maximum energy must be between 1 and 10.")
        if (
            query.min_energy is not None
            and query.max_energy is not None
            and query.min_energy > query.max_energy
        ):
            raise ValueError("Minimum energy cannot exceed maximum energy.")
        if query.mode and query.mode.lower() not in {"major", "minor"}:
            raise ValueError("Mode must be major or minor.")


def _normalize_tags(tags: Iterable[str]) -> tuple[str, ...]:
    unique: dict[str, str] = {}
    for raw_tag in tags:
        tag = raw_tag.strip()
        if tag:
            unique.setdefault(tag.casefold(), tag)
    return tuple(unique.values())


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _optional_string(value: object) -> str | None:
    return None if value is None or value == "" else str(value)


def _row_to_track(row: sqlite3.Row) -> LibraryTrack:
    tags = tuple(row["tag_names"].split(chr(31))) if row["tag_names"] else ()
    return LibraryTrack(
        id=row["id"],
        path=Path(row["path"]),
        title=row["title"],
        artist=row["artist"],
        album=row["album"],
        duration_seconds=row["duration_seconds"],
        file_format=row["file_format"],
        file_size_bytes=row["file_size_bytes"],
        bpm=row["bpm"],
        bpm_confidence=row["bpm_confidence"],
        energy_score=row["energy_score"],
        energy_level=row["energy_level"],
        musical_key=row["musical_key"],
        mode=row["mode"],
        camelot=row["camelot"],
        open_key=row["open_key"],
        key_confidence=row["key_confidence"],
        indexed_at=row["indexed_at"],
        tags=tags,
    )
