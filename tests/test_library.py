from pathlib import Path

import pytest

from aerobictoolkit.analysis import (
    EnergyAnalysis,
    MusicalKeyAnalysis,
    TrackAnalysis,
    TrackMetadata,
)
from aerobictoolkit.library import LibraryCatalog, LibraryQuery


def make_analysis(
    path: Path,
    *,
    title: str = "Workout Track",
    artist: str | None = "Coach",
    bpm: float | None = 128.0,
    energy_score: int | None = 8,
    camelot: str | None = "8A",
) -> TrackAnalysis:
    energy = (
        EnergyAnalysis(
            score=energy_score,
            rms_db=-10.0,
            onset_rate=3.0,
            brightness=0.5,
            section_seconds=15.0,
            sections=(),
        )
        if energy_score is not None
        else None
    )
    key = (
        MusicalKeyAnalysis(
            tonic="A",
            mode="minor",
            camelot=camelot,
            open_key="1m",
            confidence=0.9,
            compatible_camelot=(camelot,),
            compatible_open_key=("1m",),
        )
        if camelot is not None
        else None
    )
    return TrackAnalysis(
        metadata=TrackMetadata(
            path=path,
            title=title,
            artist=artist,
            album="Aerobic Set",
            duration_seconds=180.0,
            file_format="WAV",
            file_size_bytes=1000,
        ),
        bpm=bpm,
        bpm_confidence=0.95 if bpm else None,
        energy=energy,
        musical_key=key,
    )


def test_upsert_updates_track_and_preserves_tags(tmp_path: Path) -> None:
    audio_path = tmp_path / "track.wav"
    with LibraryCatalog(tmp_path / "catalog.db") as catalog:
        first = catalog.upsert(make_analysis(audio_path))
        catalog.add_tags(audio_path, ["Warmup", "Cardio"])
        updated = catalog.upsert(make_analysis(audio_path, title="Updated", bpm=130.0))

        assert updated.id == first.id
        assert updated.title == "Updated"
        assert updated.bpm == 130.0
        assert updated.tags == ("Warmup", "Cardio")
        assert len(catalog.search()) == 1


def test_search_combines_text_metric_key_format_and_tag_filters(
    tmp_path: Path,
) -> None:
    with LibraryCatalog(tmp_path / "catalog.db") as catalog:
        target = tmp_path / "target.wav"
        catalog.upsert(make_analysis(target, title="Power Warmup"))
        catalog.add_tags(target, ["Morning"])
        catalog.upsert(
            make_analysis(
                tmp_path / "other.wav",
                title="Cooldown",
                bpm=100.0,
                energy_score=3,
                camelot="5B",
            )
        )

        matches = catalog.search(
            LibraryQuery(
                text="power",
                min_bpm=120,
                max_bpm=140,
                min_energy=7,
                camelot="8a",
                mode="minor",
                file_format="wav",
                tags=("morning",),
            )
        )

        assert [track.path for track in matches] == [target.resolve()]


def test_tags_are_case_insensitive_and_can_be_removed(tmp_path: Path) -> None:
    path = tmp_path / "track.wav"
    with LibraryCatalog(tmp_path / "catalog.db") as catalog:
        catalog.upsert(make_analysis(path))
        tagged = catalog.add_tags(path, ["HIIT", "hiit", " Peak "])
        assert tagged.tags == ("HIIT", "Peak")
        assert catalog.list_tags() == (("HIIT", 1), ("Peak", 1))
        assert catalog.search(LibraryQuery(tags=("HIIT",)))

        untagged = catalog.remove_tags(path, ["HiIt"])
        assert untagged.tags == ("Peak",)
        assert catalog.list_tags() == (("Peak", 1),)


@pytest.mark.parametrize(
    "query",
    [
        LibraryQuery(limit=0),
        LibraryQuery(offset=-1),
        LibraryQuery(min_bpm=140, max_bpm=120),
        LibraryQuery(min_energy=0),
        LibraryQuery(max_energy=11),
        LibraryQuery(mode="dorian"),
    ],
)
def test_search_rejects_invalid_filters(tmp_path: Path, query: LibraryQuery) -> None:
    with (
        LibraryCatalog(tmp_path / "catalog.db") as catalog,
        pytest.raises(ValueError),
    ):
        catalog.search(query)


def test_tagging_requires_an_indexed_track(tmp_path: Path) -> None:
    with (
        LibraryCatalog(tmp_path / "catalog.db") as catalog,
        pytest.raises(ValueError, match="not indexed"),
    ):
        catalog.add_tags(tmp_path / "missing.wav", ["warmup"])
