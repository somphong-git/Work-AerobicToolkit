"""Musical-key detection and DJ harmonic-wheel notation."""

from __future__ import annotations

from math import sqrt
from statistics import fmean
from typing import Any

from .models import MusicalKeyAnalysis

MAJOR_PROFILE = (6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88)
MINOR_PROFILE = (6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17)

MAJOR_NAMES = ("C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B")
MINOR_NAMES = ("C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B")

MAJOR_CAMELOT = (
    "8B",
    "3B",
    "10B",
    "5B",
    "12B",
    "7B",
    "2B",
    "9B",
    "4B",
    "11B",
    "6B",
    "1B",
)
MINOR_CAMELOT = (
    "5A",
    "12A",
    "7A",
    "2A",
    "9A",
    "4A",
    "11A",
    "6A",
    "1A",
    "8A",
    "3A",
    "10A",
)

KEY_ANALYSIS_SECONDS = 60.0
KEY_SAMPLE_RATE = 22_050


def analyze_key_samples(
    librosa: Any, samples: Any, sample_rate: int
) -> MusicalKeyAnalysis:
    """Detect the best major/minor key from a harmonic CQT chromagram."""
    if sample_rate <= 0:
        raise ValueError("Sample rate must be greater than zero.")

    prepared_samples, prepared_rate = _prepare_key_samples(
        librosa, samples, sample_rate
    )
    harmonic = librosa.effects.harmonic(prepared_samples)
    chromagram = librosa.feature.chroma_cqt(y=harmonic, sr=prepared_rate)
    pitch_profile = _mean_chroma(chromagram)
    if not any(value > 0 for value in pitch_profile):
        raise ValueError("Musical key could not be detected from silent audio.")

    candidates: list[tuple[float, int, str]] = []
    for root in range(12):
        candidates.append(
            (_correlation(pitch_profile, _rotate(MAJOR_PROFILE, root)), root, "major")
        )
        candidates.append(
            (_correlation(pitch_profile, _rotate(MINOR_PROFILE, root)), root, "minor")
        )
    candidates.sort(key=lambda item: item[0], reverse=True)
    best_score, root, mode = candidates[0]
    second_score = candidates[1][0]
    confidence = _key_confidence(best_score, second_score)
    camelot = (MAJOR_CAMELOT if mode == "major" else MINOR_CAMELOT)[root]
    compatible_camelot = compatible_camelot_keys(camelot)

    return MusicalKeyAnalysis(
        tonic=(MAJOR_NAMES if mode == "major" else MINOR_NAMES)[root],
        mode=mode,
        camelot=camelot,
        open_key=camelot_to_open_key(camelot),
        confidence=confidence,
        compatible_camelot=compatible_camelot,
        compatible_open_key=tuple(
            camelot_to_open_key(value) for value in compatible_camelot
        ),
    )


def camelot_to_open_key(camelot: str) -> str:
    """Convert Camelot notation to equivalent Open Key notation."""
    number, letter = _parse_camelot(camelot)
    open_number = ((number - 8) % 12) + 1
    suffix = "m" if letter == "A" else "d"
    return f"{open_number}{suffix}"


def compatible_camelot_keys(camelot: str) -> tuple[str, ...]:
    """Return same, adjacent, and relative-mode harmonic matches."""
    number, letter = _parse_camelot(camelot)
    previous_number = 12 if number == 1 else number - 1
    next_number = 1 if number == 12 else number + 1
    relative_letter = "B" if letter == "A" else "A"
    return (
        f"{number}{letter}",
        f"{previous_number}{letter}",
        f"{next_number}{letter}",
        f"{number}{relative_letter}",
    )


def _mean_chroma(chromagram: Any) -> tuple[float, ...]:
    rows = chromagram.tolist() if hasattr(chromagram, "tolist") else chromagram
    if len(rows) != 12:
        raise ValueError("Key analysis requires a 12-bin chromagram.")
    return tuple(
        fmean(float(value) for value in row) if len(row) else 0.0 for row in rows
    )


def _prepare_key_samples(
    librosa: Any, samples: Any, sample_rate: int
) -> tuple[Any, int]:
    max_samples = round(KEY_ANALYSIS_SECONDS * sample_rate)
    prepared = samples
    if len(samples) > max_samples:
        start = (len(samples) - max_samples) // 2
        prepared = samples[start : start + max_samples]

    if sample_rate > KEY_SAMPLE_RATE:
        prepared = librosa.resample(
            y=prepared,
            orig_sr=sample_rate,
            target_sr=KEY_SAMPLE_RATE,
        )
        return prepared, KEY_SAMPLE_RATE
    return prepared, sample_rate


def _rotate(profile: tuple[float, ...], root: int) -> tuple[float, ...]:
    return tuple(profile[(index - root) % 12] for index in range(12))


def _correlation(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    left_mean = fmean(left)
    right_mean = fmean(right)
    left_centered = [value - left_mean for value in left]
    right_centered = [value - right_mean for value in right]
    numerator = sum(a * b for a, b in zip(left_centered, right_centered, strict=True))
    denominator = sqrt(
        sum(value * value for value in left_centered)
        * sum(value * value for value in right_centered)
    )
    return numerator / denominator if denominator else 0.0


def _key_confidence(best_score: float, second_score: float) -> float:
    absolute_fit = max(0.0, min(1.0, best_score))
    separation = max(0.0, min(1.0, (best_score - second_score) / 0.15))
    return round(0.65 * absolute_fit + 0.35 * separation, 3)


def _parse_camelot(value: str) -> tuple[int, str]:
    normalized = value.strip().upper()
    if len(normalized) < 2 or normalized[-1] not in {"A", "B"}:
        raise ValueError(f"Invalid Camelot key: {value}")
    try:
        number = int(normalized[:-1])
    except ValueError as error:
        raise ValueError(f"Invalid Camelot key: {value}") from error
    if not 1 <= number <= 12:
        raise ValueError(f"Invalid Camelot key: {value}")
    return number, normalized[-1]
