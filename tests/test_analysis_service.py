"""Tests for the reusable core audio-analysis boundary."""

from pathlib import Path

import pytest

from aerobictoolkit.analysis.models import TrackMetadata
from aerobictoolkit.analysis.service import (
    _scalar_tempo,
    analyze_track,
    estimate_bpm,
    read_track_metadata,
)


def test_read_track_metadata_uses_filename_when_audio_has_no_tags(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    track = tmp_path / "Warm Up.wav"
    track.write_bytes(b"audio")

    class FakeInfo:
        length = 123.4567

    class FakeAudio(dict[str, list[str]]):
        info = FakeInfo()

    monkeypatch.setattr(
        "aerobictoolkit.analysis.service._load_mutagen_file",
        lambda: lambda path, easy: FakeAudio(),
    )

    metadata = read_track_metadata(track)

    assert metadata.title == "Warm Up"
    assert metadata.duration_seconds == 123.457
    assert metadata.file_format == "wav"
    assert metadata.file_size_bytes == 5


def test_analyze_track_can_skip_bpm(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    track = tmp_path / "track.mp3"
    track.write_bytes(b"audio")
    metadata = TrackMetadata(track, "Track", None, None, None, "mp3", 5)
    monkeypatch.setattr(
        "aerobictoolkit.analysis.service.read_track_metadata", lambda path: metadata
    )

    result = analyze_track(track, include_bpm=False)

    assert result.metadata is metadata
    assert result.bpm is None


def test_scalar_tempo_accepts_scalar_and_array_like_values() -> None:
    class ArrayLike:
        def item(self) -> float:
            return 128.125

    assert _scalar_tempo(120) == 120.0
    assert _scalar_tempo(ArrayLike()) == 128.125


def test_estimate_bpm_normalizes_librosa_array_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    track = tmp_path / "track.wav"
    track.write_bytes(b"audio")

    class Tempo:
        def item(self) -> float:
            return 127.994

    class Beat:
        @staticmethod
        def beat_track(*, y: object, sr: int) -> tuple[Tempo, object]:
            return Tempo(), object()

    class FakeLibrosa:
        beat = Beat()

        @staticmethod
        def load(path: Path, *, mono: bool, sr: None) -> tuple[object, int]:
            return object(), 44_100

    monkeypatch.setattr(
        "aerobictoolkit.analysis.service._load_librosa", lambda: FakeLibrosa()
    )

    assert estimate_bpm(track) == 127.99
