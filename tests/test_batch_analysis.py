"""Tests for batch orchestration, caching, and error isolation."""

from pathlib import Path

import pytest

from aerobictoolkit.analysis import analyze_directory
from aerobictoolkit.analysis.models import TrackAnalysis, TrackMetadata


def _analysis(path: Path, bpm: float | None = 128.0) -> TrackAnalysis:
    return TrackAnalysis(
        metadata=TrackMetadata(
            path=path.resolve(),
            title=path.stem,
            artist=None,
            album=None,
            duration_seconds=180.0,
            file_format=path.suffix.removeprefix("."),
            file_size_bytes=path.stat().st_size,
        ),
        bpm=bpm,
    )


def test_batch_uses_cache_and_invalidates_changed_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    music = tmp_path / "music"
    music.mkdir()
    first_track = music / "first.wav"
    second_track = music / "second.mp3"
    first_track.write_bytes(b"first")
    second_track.write_bytes(b"second")
    calls: list[Path] = []

    def fake_analyze(
        path: Path,
        *,
        include_bpm: bool,
        include_energy: bool,
        min_bpm: float,
        max_bpm: float,
        energy_section_seconds: float,
    ) -> TrackAnalysis:
        calls.append(path)
        return _analysis(path, 128.0 if include_bpm else None)

    monkeypatch.setattr("aerobictoolkit.analysis.batch.analyze_track", fake_analyze)
    cache_path = tmp_path / "cache" / "analysis.json"

    first = analyze_directory(music, cache_path=cache_path)
    second = analyze_directory(music, cache_path=cache_path)
    first_track.write_bytes(b"first changed")
    third = analyze_directory(music, cache_path=cache_path)
    fourth = analyze_directory(
        music, cache_path=cache_path, min_bpm=100.0, max_bpm=200.0
    )
    fifth = analyze_directory(music, cache_path=cache_path, include_energy=True)
    sixth = analyze_directory(music, cache_path=cache_path, include_energy=True)
    seventh = analyze_directory(
        music,
        cache_path=cache_path,
        include_energy=True,
        energy_section_seconds=10.0,
    )

    assert first.analyzed_count == 2
    assert second.cache_hit_count == 2
    assert third.cache_hit_count == 1
    assert third.analyzed_count == 1
    assert fourth.cache_hit_count == 0
    assert fourth.analyzed_count == 2
    assert fifth.analyzed_count == 2
    assert sixth.cache_hit_count == 2
    assert seventh.analyzed_count == 2
    assert len(calls) == 9


def test_batch_captures_bad_track_without_stopping_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    music = tmp_path / "music"
    music.mkdir()
    good = music / "good.wav"
    bad = music / "bad.wav"
    good.write_bytes(b"good")
    bad.write_bytes(b"bad")

    def fake_analyze(
        path: Path,
        *,
        include_bpm: bool,
        include_energy: bool,
        min_bpm: float,
        max_bpm: float,
        energy_section_seconds: float,
    ) -> TrackAnalysis:
        if path.name == "bad.wav":
            raise ValueError("decoder rejected file")
        return _analysis(path)

    monkeypatch.setattr("aerobictoolkit.analysis.batch.analyze_track", fake_analyze)

    result = analyze_directory(music, include_bpm=False)

    assert result.total_count == 2
    assert result.success_count == 1
    assert result.error_count == 1
    assert result.errors[0].error_type == "ValueError"
    assert result.errors[0].message == "decoder rejected file"


def test_batch_reports_corrupt_cache_as_warning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    music = tmp_path / "music"
    music.mkdir()
    track = music / "track.wav"
    track.write_bytes(b"audio")
    cache_path = tmp_path / "cache.json"
    cache_path.write_text("not-json", encoding="utf-8")

    def fake_analyze(path: Path, **options: object) -> TrackAnalysis:
        return _analysis(path)

    monkeypatch.setattr(
        "aerobictoolkit.analysis.batch.analyze_track",
        fake_analyze,
    )

    result = analyze_directory(music, cache_path=cache_path)

    assert result.success_count == 1
    assert len(result.cache_warnings) == 1
    assert "unreadable analysis cache" in result.cache_warnings[0]
