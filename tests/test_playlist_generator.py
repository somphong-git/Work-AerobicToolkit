from pathlib import Path

from aerobictoolkit.library import LibraryTrack
from aerobictoolkit.playlist import (
    GeneratedPlaylist,
    PlaylistGenerationRules,
    WorkoutPhase,
    WorkoutPhaseType,
    WorkoutSession,
    generate_playlist,
)


def make_track(
    number: int,
    *,
    bpm: float | None,
    energy: int | None,
    duration: float | None = 150,
) -> LibraryTrack:
    return LibraryTrack(
        id=number,
        path=Path(f"track-{number}.wav").resolve(),
        title=f"Track {number:02}",
        artist="Test Artist",
        album=None,
        duration_seconds=duration,
        file_format="wav",
        file_size_bytes=1000,
        bpm=bpm,
        bpm_confidence=0.9 if bpm else None,
        energy_score=energy,
        energy_level="high" if energy else None,
        musical_key=None,
        mode=None,
        camelot=None,
        open_key=None,
        key_confidence=None,
        indexed_at="2026-07-21T00:00:00+00:00",
    )


def short_session() -> WorkoutSession:
    return WorkoutSession(
        name="20-Minute Test Session",
        phases=(
            WorkoutPhase(WorkoutPhaseType.WARM_UP, 300, 100, 120, 3, 5),
            WorkoutPhase(WorkoutPhaseType.CARDIO, 300, 120, 140, 5, 8),
            WorkoutPhase(WorkoutPhaseType.PEAK, 300, 135, 155, 8, 10),
            WorkoutPhase(WorkoutPhaseType.COOL_DOWN, 300, 90, 115, 2, 4),
        ),
    )


def complete_library() -> list[LibraryTrack]:
    return [
        make_track(1, bpm=116, energy=3),
        make_track(2, bpm=119, energy=5),
        make_track(3, bpm=122, energy=6),
        make_track(4, bpm=132, energy=7),
        make_track(5, bpm=140, energy=9),
        make_track(6, bpm=152, energy=10),
        make_track(7, bpm=112, energy=4),
        make_track(8, bpm=92, energy=2),
    ]


def test_generator_builds_complete_playlist_without_track_reuse() -> None:
    result = generate_playlist(
        short_session(),
        complete_library(),
        rules=PlaylistGenerationRules(duration_tolerance_seconds=0),
    )

    assert result.is_complete
    assert result.total_duration_seconds == 1200
    assert all(len(phase.items) == 2 for phase in result.phases)
    paths = [item.track.path for item in result.items]
    assert len(paths) == len(set(paths))
    assert result.items[0].start_seconds == 0
    assert result.items[-1].end_seconds == 1200


def test_generator_orders_intensity_up_then_cool_down() -> None:
    result = generate_playlist(
        short_session(),
        complete_library(),
        rules=PlaylistGenerationRules(duration_tolerance_seconds=0),
    )

    warm_up = result.phases[0]
    cool_down = result.phases[-1]
    assert [item.track.energy_score for item in warm_up.items] == [3, 5]
    assert [item.track.energy_score for item in cool_down.items] == [4, 2]


def test_generator_is_deterministic_for_reordered_input() -> None:
    tracks = complete_library()
    rules = PlaylistGenerationRules(duration_tolerance_seconds=0)

    first = generate_playlist(short_session(), tracks, rules=rules)
    second = generate_playlist(short_session(), list(reversed(tracks)), rules=rules)

    assert [item.track.path for item in first.items] == [
        item.track.path for item in second.items
    ]


def test_generator_excludes_missing_metrics_and_reports_shortfall() -> None:
    tracks = [
        make_track(1, bpm=None, energy=5),
        make_track(2, bpm=110, energy=None),
        make_track(3, bpm=110, energy=4, duration=None),
        make_track(4, bpm=110, energy=4),
    ]

    result = generate_playlist(
        short_session(),
        tracks,
        rules=PlaylistGenerationRules(duration_tolerance_seconds=0),
    )

    assert not result.is_complete
    assert len(result.items) == 1
    assert result.warnings[0].startswith("Excluded 3 track")
    assert any("duration differs" in warning for warning in result.warnings)


def test_rule_scores_and_serialization_are_explainable() -> None:
    result = generate_playlist(
        short_session(),
        complete_library(),
        rules=PlaylistGenerationRules(duration_tolerance_seconds=0),
    )

    assert isinstance(result, GeneratedPlaylist)
    assert all(0 <= item.score.total <= 100 for item in result.items)
    payload = result.to_dict()
    assert payload["summary"]["track_count"] == 8
    assert payload["phases"][0]["is_complete"] is True


def test_duration_tolerance_can_accept_small_shortfall() -> None:
    session = short_session()
    tracks = [
        make_track(phase_index, bpm=bpm, energy=energy, duration=250)
        for phase_index, (bpm, energy) in enumerate(
            [(110, 4), (130, 6), (145, 9), (100, 3)], start=1
        )
    ]

    result = generate_playlist(
        session,
        tracks,
        rules=PlaylistGenerationRules(duration_tolerance_seconds=60),
    )

    assert result.is_complete


def test_generation_rules_validate_limits() -> None:
    for kwargs in (
        {"duration_tolerance_seconds": -1},
        {"max_tracks_per_phase": 0},
    ):
        try:
            PlaylistGenerationRules(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid generation rules were accepted.")
