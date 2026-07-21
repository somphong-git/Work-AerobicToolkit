"""Application services for building the local music library."""

from __future__ import annotations

from pathlib import Path

from aerobictoolkit.analysis import analyze_directory

from .catalog import DEFAULT_LIBRARY_PATH, LibraryCatalog
from .models import LibraryIndexResult


def index_directory(
    directory: str | Path,
    *,
    database_path: str | Path = DEFAULT_LIBRARY_PATH,
    include_bpm: bool = True,
    include_energy: bool = False,
    include_key: bool = False,
    cache_path: str | Path | None = Path("data/cache/analysis-cache.json"),
    min_bpm: float = 90.0,
    max_bpm: float = 180.0,
    energy_section_seconds: float = 15.0,
) -> LibraryIndexResult:
    """Analyze a folder and upsert every successful result into the catalog."""
    batch = analyze_directory(
        directory,
        include_bpm=include_bpm,
        include_energy=include_energy,
        include_key=include_key,
        cache_path=cache_path,
        min_bpm=min_bpm,
        max_bpm=max_bpm,
        energy_section_seconds=energy_section_seconds,
    )
    with LibraryCatalog(database_path) as catalog:
        for track in batch.tracks:
            catalog.upsert(track.analysis)
    return LibraryIndexResult(
        discovered=batch.total_count,
        indexed=batch.success_count,
        errors=batch.error_count,
        cache_hits=batch.cache_hit_count,
    )
