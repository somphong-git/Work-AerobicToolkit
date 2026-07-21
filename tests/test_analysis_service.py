"""Tests for the reusable core audio-analysis boundary."""

from pathlib import Path

import pytest

from aerobictoolkit.analysis.models import TrackMetadata
from aerobictoolkit.analysis.service import (
    _scalar_tempo,
    analyze_tempo,
    analyze_track,
    normalize_tempo,
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


def test_analyze_tempo_normalizes_octave_and_builds_confident_grid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    track = tmp_path / "track.wav"
    track.write_bytes(b"audio")

    class Tempo:
        def item(self) -> float:
            return 64.0

    class Values:
        def __init__(self, values: list[float]) -> None:
            self.values = values

        def tolist(self) -> list[float]:
            return self.values

    class Beat:
        @staticmethod
        def beat_track(*, onset_envelope: object, sr: int) -> tuple[Tempo, Values]:
            return Tempo(), Values([0.0, 1.0, 2.0])

    class Onset:
        @staticmethod
        def onset_strength(*, y: object, sr: int) -> object:
            return object()

    class Feature:
        @staticmethod
        def tempo(*, onset_envelope: object, sr: int, aggregate: None) -> Values:
            return Values([64.0, 64.0, 63.8])

    class FakeLibrosa:
        beat = Beat()
        onset = Onset()
        feature = Feature()

        @staticmethod
        def load(path: Path, *, mono: bool, sr: None) -> tuple[object, int]:
            return object(), 44_100

        @staticmethod
        def frames_to_time(frames: Values, *, sr: int) -> Values:
            return Values([0.0, 0.9375, 1.875])

    monkeypatch.setattr(
        "aerobictoolkit.analysis.service._load_librosa", lambda: FakeLibrosa()
    )

    result = analyze_tempo(track)

    assert result.raw_bpm == 64.0
    assert result.normalized_bpm == 128.0
    assert result.beat_grid.times_seconds == (0.0, 0.46875, 0.9375, 1.40625, 1.875)
    assert result.confidence >= 0.8


@pytest.mark.parametrize(
    ("raw_bpm", "expected"),
    [(64.0, 128.0), (128.0, 128.0), (256.0, 128.0)],
)
def test_normalize_tempo_resolves_half_and_double_time(
    raw_bpm: float, expected: float
) -> None:
    assert normalize_tempo(raw_bpm) == expected


def test_normalize_tempo_rejects_invalid_range() -> None:
    with pytest.raises(ValueError, match="span at least one octave"):
        normalize_tempo(128, min_bpm=100, max_bpm=150)
