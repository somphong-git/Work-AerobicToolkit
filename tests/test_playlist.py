"""Workout-session domain contract tests."""

import pytest

from aerobictoolkit.playlist import (
    CANONICAL_PHASE_ORDER,
    WorkoutPhase,
    WorkoutPhaseType,
    WorkoutSession,
    standard_workout_session,
)


def test_standard_session_has_canonical_intensity_curve() -> None:
    session = standard_workout_session()

    assert tuple(phase.phase_type for phase in session.phases) == CANONICAL_PHASE_ORDER
    assert session.total_duration_seconds == 3600
    assert session.total_duration_minutes == 60
    assert session.phase(WorkoutPhaseType.WARM_UP).max_energy == 5
    assert session.phase(WorkoutPhaseType.PEAK).min_energy == 8
    assert session.phase(WorkoutPhaseType.COOL_DOWN).max_bpm == 115


def test_phase_accepts_tracks_with_known_or_missing_metrics() -> None:
    phase = standard_workout_session().phase(WorkoutPhaseType.CARDIO)

    assert phase.accepts(bpm=128, energy=7)
    assert phase.accepts(bpm=None, energy=7)
    assert phase.accepts(bpm=128, energy=None)
    assert not phase.accepts(bpm=150, energy=7)
    assert not phase.accepts(bpm=128, energy=9)


def test_session_serialization_round_trip() -> None:
    session = standard_workout_session("Morning Class")

    restored = WorkoutSession.from_dict(session.to_dict())

    assert restored == session
    assert restored.to_dict()["total_duration_minutes"] == 60


@pytest.mark.parametrize(
    "kwargs",
    [
        {"target_duration_seconds": 0},
        {"min_bpm": 140, "max_bpm": 120},
        {"min_bpm": 0},
        {"min_energy": 0},
        {"max_energy": 11},
        {"min_energy": 8, "max_energy": 5},
    ],
)
def test_phase_rejects_invalid_envelopes(kwargs: dict[str, int]) -> None:
    values = {
        "phase_type": WorkoutPhaseType.CARDIO,
        "target_duration_seconds": 600,
        "min_bpm": 120,
        "max_bpm": 140,
        "min_energy": 5,
        "max_energy": 8,
    }
    values.update(kwargs)

    with pytest.raises(ValueError):
        WorkoutPhase(**values)


@pytest.mark.parametrize(
    "phases",
    [
        standard_workout_session().phases[:-1],
        tuple(reversed(standard_workout_session().phases)),
        (
            standard_workout_session().phases[0],
            standard_workout_session().phases[1],
            standard_workout_session().phases[1],
            standard_workout_session().phases[3],
        ),
    ],
)
def test_session_requires_each_phase_once_in_order(
    phases: tuple[WorkoutPhase, ...],
) -> None:
    with pytest.raises(ValueError, match="exactly once"):
        WorkoutSession(name="Invalid", phases=phases)


def test_session_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="name"):
        WorkoutSession(name=" ", phases=standard_workout_session().phases)


def test_deserialization_rejects_malformed_contract() -> None:
    with pytest.raises(ValueError, match="Invalid workout session"):
        WorkoutSession.from_dict({"name": "Missing phases"})
