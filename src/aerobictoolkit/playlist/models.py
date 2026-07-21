"""Workout-session domain models independent from playlist generation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class WorkoutPhaseType(StrEnum):
    """Canonical phases of an aerobic workout session."""

    WARM_UP = "warm-up"
    CARDIO = "cardio"
    PEAK = "peak"
    COOL_DOWN = "cool-down"


CANONICAL_PHASE_ORDER = tuple(WorkoutPhaseType)


@dataclass(frozen=True, slots=True)
class WorkoutPhase:
    """Target duration and musical intensity envelope for one phase."""

    phase_type: WorkoutPhaseType
    target_duration_seconds: int
    min_bpm: float
    max_bpm: float
    min_energy: int
    max_energy: int

    def __post_init__(self) -> None:
        if not isinstance(self.phase_type, WorkoutPhaseType):
            raise TypeError("phase_type must be a WorkoutPhaseType.")
        if self.target_duration_seconds <= 0:
            raise ValueError("Phase duration must be greater than zero.")
        if self.min_bpm <= 0 or self.max_bpm <= 0:
            raise ValueError("Phase BPM values must be greater than zero.")
        if self.min_bpm > self.max_bpm:
            raise ValueError("Phase minimum BPM cannot exceed maximum BPM.")
        if not 1 <= self.min_energy <= 10:
            raise ValueError("Phase minimum energy must be between 1 and 10.")
        if not 1 <= self.max_energy <= 10:
            raise ValueError("Phase maximum energy must be between 1 and 10.")
        if self.min_energy > self.max_energy:
            raise ValueError("Phase minimum energy cannot exceed maximum energy.")

    @property
    def target_duration_minutes(self) -> float:
        return self.target_duration_seconds / 60

    def accepts(self, *, bpm: float | None, energy: int | None) -> bool:
        """Return whether known track metrics fit this phase envelope."""
        if bpm is not None and not self.min_bpm <= bpm <= self.max_bpm:
            return False
        return energy is None or self.min_energy <= energy <= self.max_energy

    def to_dict(self) -> dict[str, object]:
        return {
            "phase_type": self.phase_type.value,
            "target_duration_seconds": self.target_duration_seconds,
            "target_duration_minutes": self.target_duration_minutes,
            "bpm": {"min": self.min_bpm, "max": self.max_bpm},
            "energy": {"min": self.min_energy, "max": self.max_energy},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkoutPhase:
        """Create a validated phase from the public serialized contract."""
        try:
            bpm = data["bpm"]
            energy = data["energy"]
            if not isinstance(bpm, dict) or not isinstance(energy, dict):
                raise TypeError("bpm and energy must be objects.")
            return cls(
                phase_type=WorkoutPhaseType(data["phase_type"]),
                target_duration_seconds=int(data["target_duration_seconds"]),
                min_bpm=float(bpm["min"]),
                max_bpm=float(bpm["max"]),
                min_energy=int(energy["min"]),
                max_energy=int(energy["max"]),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid workout phase: {error}") from error


@dataclass(frozen=True, slots=True)
class WorkoutSession:
    """A complete workout blueprint containing the four canonical phases."""

    name: str
    phases: tuple[WorkoutPhase, ...]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Workout session name cannot be empty.")
        phase_order = tuple(phase.phase_type for phase in self.phases)
        if phase_order != CANONICAL_PHASE_ORDER:
            expected = ", ".join(phase.value for phase in CANONICAL_PHASE_ORDER)
            raise ValueError(
                "Workout phases must appear exactly once in this order: " + expected
            )

    @property
    def total_duration_seconds(self) -> int:
        return sum(phase.target_duration_seconds for phase in self.phases)

    @property
    def total_duration_minutes(self) -> float:
        return self.total_duration_seconds / 60

    def phase(self, phase_type: WorkoutPhaseType) -> WorkoutPhase:
        """Return one phase by its stable domain identifier."""
        return self.phases[CANONICAL_PHASE_ORDER.index(phase_type)]

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "total_duration_seconds": self.total_duration_seconds,
            "total_duration_minutes": self.total_duration_minutes,
            "phases": [phase.to_dict() for phase in self.phases],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkoutSession:
        """Create a validated session from its public serialized contract."""
        try:
            raw_phases = data["phases"]
            if not isinstance(raw_phases, list):
                raise TypeError("phases must be a list.")
            return cls(
                name=str(data["name"]),
                phases=tuple(WorkoutPhase.from_dict(item) for item in raw_phases),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid workout session: {error}") from error


def standard_workout_session(
    name: str = "60-Minute Aerobic Workout",
) -> WorkoutSession:
    """Return the initial balanced 60-minute planning template."""
    return WorkoutSession(
        name=name,
        phases=(
            WorkoutPhase(WorkoutPhaseType.WARM_UP, 600, 100, 120, 3, 5),
            WorkoutPhase(WorkoutPhaseType.CARDIO, 1500, 120, 140, 5, 8),
            WorkoutPhase(WorkoutPhaseType.PEAK, 900, 135, 155, 8, 10),
            WorkoutPhase(WorkoutPhaseType.COOL_DOWN, 600, 90, 115, 2, 4),
        ),
    )
