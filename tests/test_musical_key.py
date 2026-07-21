"""Tests for musical-key detection and DJ wheel notation."""

from pathlib import Path

import pytest

from aerobictoolkit.analysis.cache import AnalysisCache
from aerobictoolkit.analysis.models import (
    MusicalKeyAnalysis,
    TrackAnalysis,
    TrackMetadata,
)
from aerobictoolkit.analysis.musical_key import (
    MAJOR_PROFILE,
    analyze_key_samples,
    camelot_to_open_key,
    compatible_camelot_keys,
)


class FakeEffects:
    @staticmethod
    def harmonic(samples: object) -> object:
        return samples


class FakeFeature:
    @staticmethod
    def chroma_cqt(*, y: object, sr: int) -> list[list[float]]:
        return [[value, value, value] for value in MAJOR_PROFILE]


class FakeLibrosa:
    effects = FakeEffects()
    feature = FakeFeature()

    @staticmethod
    def resample(*, y: object, orig_sr: int, target_sr: int) -> object:
        return y


def test_key_detector_finds_c_major_and_dj_notation() -> None:
    result = analyze_key_samples(FakeLibrosa(), [0.0], 44_100)

    assert result.name == "C major"
    assert result.camelot == "8B"
    assert result.open_key == "1d"
    assert result.confidence_level == "high"
    assert result.compatible_camelot == ("8B", "7B", "9B", "8A")


@pytest.mark.parametrize(
    ("camelot", "open_key"),
    [("8B", "1d"), ("8A", "1m"), ("1B", "6d"), ("1A", "6m"), ("12B", "5d")],
)
def test_camelot_to_open_key_mapping(camelot: str, open_key: str) -> None:
    assert camelot_to_open_key(camelot) == open_key


def test_compatible_keys_wrap_around_wheel() -> None:
    assert compatible_camelot_keys("1A") == ("1A", "12A", "2A", "1B")


def test_musical_key_round_trips_through_cache(tmp_path: Path) -> None:
    track = tmp_path / "track.wav"
    track.write_bytes(b"audio")
    metadata = TrackMetadata(track, "Track", None, None, 10.0, "wav", 5)
    musical_key = MusicalKeyAnalysis(
        tonic="F#",
        mode="minor",
        camelot="11A",
        open_key="4m",
        confidence=0.88,
        compatible_camelot=("11A", "10A", "12A", "11B"),
        compatible_open_key=("4m", "3m", "5m", "4d"),
    )
    analysis = TrackAnalysis(metadata=metadata, bpm=None, musical_key=musical_key)
    cache_path = tmp_path / "cache.json"
    cache = AnalysisCache(cache_path)
    cache.put(
        analysis,
        include_bpm=False,
        include_energy=False,
        include_key=True,
        min_bpm=90.0,
        max_bpm=180.0,
        energy_section_seconds=15.0,
    )
    cache.save()

    restored = AnalysisCache(cache_path).get(
        track,
        include_bpm=False,
        include_energy=False,
        include_key=True,
        min_bpm=90.0,
        max_bpm=180.0,
        energy_section_seconds=15.0,
    )

    assert restored is not None
    assert restored.musical_key == musical_key
