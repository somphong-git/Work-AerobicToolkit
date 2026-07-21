"""Tests for perceptual energy scoring and section timelines."""

from __future__ import annotations

from math import log10
from pathlib import Path

import pytest

from aerobictoolkit.analysis.cache import AnalysisCache
from aerobictoolkit.analysis.energy import analyze_energy_samples
from aerobictoolkit.analysis.models import (
    BeatGrid,
    EnergyAnalysis,
    EnergySection,
    TempoAnalysis,
    TrackAnalysis,
    TrackMetadata,
    energy_level,
)
from aerobictoolkit.analysis.service import analyze_track


class Values:
    def __init__(self, values: list[float]) -> None:
        self.values = values

    def tolist(self) -> list[float]:
        return self.values

    def __getitem__(self, index: int) -> Values:
        assert index == 0
        return self


class FakeFeature:
    @staticmethod
    def rms(*, y: object) -> Values:
        return Values([0.05, 0.08, 0.1, 0.3, 0.4, 0.5])

    @staticmethod
    def spectral_centroid(*, y: object, sr: int) -> Values:
        return Values([5, 7, 10, 20, 25, 30])


class FakeOnset:
    @staticmethod
    def onset_strength(*, y: object, sr: int) -> object:
        return object()

    @staticmethod
    def onset_detect(*, onset_envelope: object, sr: int, units: str) -> Values:
        return Values([1, 3, 6, 12, 16, 18, 25])


class FakeLibrosa:
    feature = FakeFeature()
    onset = FakeOnset()

    @staticmethod
    def frames_to_time(frames: object, *, sr: int) -> Values:
        return Values([0, 5, 10, 15, 20, 25])

    @staticmethod
    def amplitude_to_db(value: float, *, ref: float) -> float:
        return 20 * log10(value) if value > 0 else -100.0


def test_energy_analysis_scores_overall_track_and_sections() -> None:
    result = analyze_energy_samples(
        FakeLibrosa(), [0.0] * 3000, 100, section_seconds=15
    )

    assert 1 <= result.score <= 10
    assert len(result.sections) == 2
    assert result.sections[0].start_seconds == 0
    assert result.sections[1].end_seconds == 30
    assert result.sections[1].score > result.sections[0].score


@pytest.mark.parametrize(
    ("score", "expected"),
    [(1, "very-low"), (3, "low"), (5, "moderate"), (7, "high"), (10, "peak")],
)
def test_energy_level_bands(score: int, expected: str) -> None:
    assert energy_level(score) == expected


def test_track_analysis_decodes_once_for_tempo_and_energy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    track = tmp_path / "track.wav"
    track.write_bytes(b"audio")
    metadata = TrackMetadata(track, "Track", None, None, 10.0, "wav", 5)
    load_count = 0

    class Loader:
        @staticmethod
        def load(path: Path, *, mono: bool, sr: None) -> tuple[list[float], int]:
            nonlocal load_count
            load_count += 1
            return [0.0] * 100, 10

    tempo = TempoAnalysis(120.0, 120.0, 0.9, BeatGrid((0.0, 0.5)))
    energy = EnergyAnalysis(6, -15.0, 2.0, 0.2, 15.0, (EnergySection(0.0, 10.0, 6),))
    monkeypatch.setattr(
        "aerobictoolkit.analysis.service.read_track_metadata", lambda path: metadata
    )
    monkeypatch.setattr("aerobictoolkit.analysis.service._load_librosa", Loader)
    monkeypatch.setattr(
        "aerobictoolkit.analysis.service._analyze_tempo_samples",
        lambda *args, **kwargs: tempo,
    )
    monkeypatch.setattr(
        "aerobictoolkit.analysis.service.analyze_energy_samples",
        lambda *args, **kwargs: energy,
    )

    result = analyze_track(track, include_bpm=True, include_energy=True)

    assert load_count == 1
    assert result.bpm == 120.0
    assert result.energy is energy


def test_energy_round_trips_through_analysis_cache(tmp_path: Path) -> None:
    track = tmp_path / "track.wav"
    track.write_bytes(b"audio")
    metadata = TrackMetadata(track, "Track", None, None, 10.0, "wav", 5)
    energy = EnergyAnalysis(8, -10.0, 2.5, 0.3, 15.0, (EnergySection(0.0, 10.0, 8),))
    analysis = TrackAnalysis(metadata=metadata, bpm=None, energy=energy)
    cache_path = tmp_path / "cache.json"
    cache = AnalysisCache(cache_path)
    cache.put(
        analysis,
        include_bpm=False,
        include_energy=True,
        min_bpm=90.0,
        max_bpm=180.0,
        energy_section_seconds=15.0,
    )
    cache.save()

    restored = AnalysisCache(cache_path).get(
        track,
        include_bpm=False,
        include_energy=True,
        min_bpm=90.0,
        max_bpm=180.0,
        energy_section_seconds=15.0,
    )

    assert restored is not None
    assert restored.energy == energy
