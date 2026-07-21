"""Perceptual energy scoring from decoded audio samples."""

from __future__ import annotations

from math import ceil, floor
from statistics import fmean
from typing import Any

from .models import EnergyAnalysis, EnergySection

DEFAULT_ENERGY_SECTION_SECONDS = 15.0


def analyze_energy_samples(
    librosa: Any,
    samples: Any,
    sample_rate: int,
    *,
    section_seconds: float = DEFAULT_ENERGY_SECTION_SECONDS,
) -> EnergyAnalysis:
    """Calculate overall and section energy from one decoded mono signal."""
    if section_seconds <= 0:
        raise ValueError("Energy section duration must be greater than zero.")
    if sample_rate <= 0:
        raise ValueError("Sample rate must be greater than zero.")

    rms_values = _float_values(librosa.feature.rms(y=samples)[0])
    centroid_values = _float_values(
        librosa.feature.spectral_centroid(y=samples, sr=sample_rate)[0]
    )
    frame_count = min(len(rms_values), len(centroid_values))
    rms_values = rms_values[:frame_count]
    centroid_values = centroid_values[:frame_count]
    onset_envelope = librosa.onset.onset_strength(y=samples, sr=sample_rate)
    onset_times = _float_values(
        librosa.onset.onset_detect(
            onset_envelope=onset_envelope,
            sr=sample_rate,
            units="time",
        )
    )
    duration = len(samples) / sample_rate
    frame_times = _float_values(
        librosa.frames_to_time(range(frame_count), sr=sample_rate)
    )

    score, rms_db, onset_rate, brightness = _score_window(
        librosa,
        rms_values,
        centroid_values,
        onset_times,
        duration=max(duration, 0.001),
        sample_rate=sample_rate,
    )
    sections = _build_sections(
        librosa,
        frame_times,
        rms_values,
        centroid_values,
        onset_times,
        duration=duration,
        sample_rate=sample_rate,
        section_seconds=section_seconds,
    )
    return EnergyAnalysis(
        score=score,
        rms_db=round(rms_db, 3),
        onset_rate=round(onset_rate, 3),
        brightness=round(brightness, 3),
        section_seconds=section_seconds,
        sections=tuple(sections),
    )


def _build_sections(
    librosa: Any,
    frame_times: list[float],
    rms_values: list[float],
    centroid_values: list[float],
    onset_times: list[float],
    *,
    duration: float,
    sample_rate: int,
    section_seconds: float,
) -> list[EnergySection]:
    sections: list[EnergySection] = []
    section_count = max(1, ceil(duration / section_seconds))
    for index in range(section_count):
        start = index * section_seconds
        end = min(duration, start + section_seconds)
        frame_indices = [
            frame_index
            for frame_index, frame_time in enumerate(frame_times)
            if start <= frame_time < end
        ]
        section_rms = [rms_values[item] for item in frame_indices]
        section_centroid = [centroid_values[item] for item in frame_indices]
        section_onsets = [value for value in onset_times if start <= value < end]
        score, _, _, _ = _score_window(
            librosa,
            section_rms,
            section_centroid,
            section_onsets,
            duration=max(end - start, 0.001),
            sample_rate=sample_rate,
        )
        sections.append(
            EnergySection(
                start_seconds=round(start, 3),
                end_seconds=round(end, 3),
                score=score,
            )
        )
    return sections


def _score_window(
    librosa: Any,
    rms_values: list[float],
    centroid_values: list[float],
    onset_times: list[float],
    *,
    duration: float,
    sample_rate: int,
) -> tuple[int, float, float, float]:
    mean_rms = fmean(rms_values) if rms_values else 0.0
    rms_db = _scalar(librosa.amplitude_to_db(mean_rms, ref=1.0))
    onset_rate = len(onset_times) / duration
    mean_centroid = fmean(centroid_values) if centroid_values else 0.0
    brightness = mean_centroid / (sample_rate / 2)

    loudness_component = _clamp((rms_db + 35) / 27)
    activity_component = _clamp(onset_rate / 4)
    brightness_component = _clamp((brightness - 0.04) / 0.32)
    combined = (
        0.55 * loudness_component
        + 0.30 * activity_component
        + 0.15 * brightness_component
    )
    score = max(1, min(10, floor(combined * 9 + 1.5)))
    return score, rms_db, onset_rate, brightness


def _float_values(values: Any) -> list[float]:
    try:
        unpacked = values.tolist()
    except AttributeError:
        unpacked = values
    if isinstance(unpacked, (int, float)):
        return [float(unpacked)]
    return [float(value) for value in unpacked]


def _scalar(value: Any) -> float:
    try:
        return float(value.item())
    except AttributeError:
        return float(value)


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
