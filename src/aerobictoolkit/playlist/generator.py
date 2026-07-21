"""Deterministic rule-based playlist generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aerobictoolkit.library import LibraryCatalog, LibraryQuery, LibraryTrack

from .models import WorkoutPhase, WorkoutPhaseType, WorkoutSession


@dataclass(frozen=True, slots=True)
class PlaylistGenerationRules:
    """Stable knobs for the initial deterministic generator."""

    duration_tolerance_seconds: int = 120
    max_tracks_per_phase: int = 50

    def __post_init__(self) -> None:
        if self.duration_tolerance_seconds < 0:
            raise ValueError("Duration tolerance cannot be negative.")
        if self.max_tracks_per_phase < 1:
            raise ValueError("Maximum tracks per phase must be at least one.")


@dataclass(frozen=True, slots=True)
class PlaylistRuleScore:
    """Explainable component scores normalized to 0–100."""

    bpm: float
    energy: float
    duration: float
    total: float

    def to_dict(self) -> dict[str, float]:
        return {
            "bpm": self.bpm,
            "energy": self.energy,
            "duration": self.duration,
            "total": self.total,
        }


@dataclass(frozen=True, slots=True)
class PlaylistItem:
    """One selected library track and its place in the workout timeline."""

    track: LibraryTrack
    phase_type: WorkoutPhaseType
    start_seconds: float
    end_seconds: float
    score: PlaylistRuleScore

    def to_dict(self) -> dict[str, object]:
        return {
            "phase_type": self.phase_type.value,
            "start_seconds": self.start_seconds,
            "end_seconds": self.end_seconds,
            "score": self.score.to_dict(),
            "track": self.track.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class GeneratedPlaylistPhase:
    """Selected tracks and duration fit for one workout phase."""

    target: WorkoutPhase
    items: tuple[PlaylistItem, ...]
    actual_duration_seconds: float
    duration_tolerance_seconds: int

    @property
    def duration_difference_seconds(self) -> float:
        return self.actual_duration_seconds - self.target.target_duration_seconds

    @property
    def is_complete(self) -> bool:
        return abs(self.duration_difference_seconds) <= self.duration_tolerance_seconds

    def to_dict(self) -> dict[str, object]:
        return {
            "target": self.target.to_dict(),
            "actual_duration_seconds": self.actual_duration_seconds,
            "duration_difference_seconds": self.duration_difference_seconds,
            "is_complete": self.is_complete,
            "items": [item.to_dict() for item in self.items],
        }


@dataclass(frozen=True, slots=True)
class GeneratedPlaylist:
    """Complete, explainable output from the playlist generator."""

    session: WorkoutSession
    phases: tuple[GeneratedPlaylistPhase, ...]
    warnings: tuple[str, ...] = ()

    @property
    def items(self) -> tuple[PlaylistItem, ...]:
        return tuple(item for phase in self.phases for item in phase.items)

    @property
    def total_duration_seconds(self) -> float:
        return sum(phase.actual_duration_seconds for phase in self.phases)

    @property
    def is_complete(self) -> bool:
        return all(phase.is_complete for phase in self.phases)

    def to_dict(self) -> dict[str, object]:
        return {
            "session": self.session.to_dict(),
            "summary": {
                "track_count": len(self.items),
                "total_duration_seconds": self.total_duration_seconds,
                "is_complete": self.is_complete,
            },
            "phases": [phase.to_dict() for phase in self.phases],
            "warnings": list(self.warnings),
        }


def generate_playlist(
    session: WorkoutSession,
    tracks: tuple[LibraryTrack, ...] | list[LibraryTrack],
    *,
    rules: PlaylistGenerationRules | None = None,
) -> GeneratedPlaylist:
    """Assign analyzed tracks by BPM, energy, and duration without reuse."""
    rules = rules or PlaylistGenerationRules()
    available = tuple(tracks)
    eligible = tuple(track for track in available if _has_required_metrics(track))
    missing_count = len(available) - len(eligible)
    warnings: list[str] = []
    if missing_count:
        warnings.append(
            f"Excluded {missing_count} track(s) without BPM, energy, or duration."
        )

    candidate_map = {
        phase.phase_type: [
            track
            for track in eligible
            if phase.accepts(bpm=track.bpm, energy=track.energy_score)
        ]
        for phase in session.phases
    }
    phase_positions = {
        phase.phase_type: position for position, phase in enumerate(session.phases)
    }
    allocation_order = sorted(
        session.phases,
        key=lambda phase: (
            len(candidate_map[phase.phase_type]),
            phase_positions[phase.phase_type],
        ),
    )
    used_paths: set[str] = set()
    selected_by_phase: dict[
        WorkoutPhaseType, list[tuple[LibraryTrack, PlaylistRuleScore]]
    ] = {}
    for phase in allocation_order:
        candidates = [
            track
            for track in candidate_map[phase.phase_type]
            if str(track.path.resolve()) not in used_paths
        ]
        selected = _select_phase_tracks(phase, candidates, rules)
        selected_by_phase[phase.phase_type] = selected
        used_paths.update(str(track.path.resolve()) for track, _ in selected)

    generated_phases: list[GeneratedPlaylistPhase] = []
    timeline_seconds = 0.0
    for phase in session.phases:
        selected = selected_by_phase[phase.phase_type]
        ordered = _order_for_phase(phase.phase_type, selected)
        items: list[PlaylistItem] = []
        for track, score in ordered:
            duration = track.duration_seconds or 0.0
            item = PlaylistItem(
                track=track,
                phase_type=phase.phase_type,
                start_seconds=round(timeline_seconds, 3),
                end_seconds=round(timeline_seconds + duration, 3),
                score=score,
            )
            items.append(item)
            timeline_seconds += duration
        actual_duration = sum(item.track.duration_seconds or 0.0 for item in items)
        generated = GeneratedPlaylistPhase(
            target=phase,
            items=tuple(items),
            actual_duration_seconds=round(actual_duration, 3),
            duration_tolerance_seconds=rules.duration_tolerance_seconds,
        )
        generated_phases.append(generated)
        if not generated.is_complete:
            warnings.append(
                f"{phase.phase_type.value} duration differs from target by "
                f"{generated.duration_difference_seconds:+.1f} seconds."
            )

    return GeneratedPlaylist(
        session=session,
        phases=tuple(generated_phases),
        warnings=tuple(warnings),
    )


def generate_playlist_from_catalog(
    session: WorkoutSession,
    *,
    database_path: str | Path = "data/library/catalog.sqlite3",
    rules: PlaylistGenerationRules | None = None,
) -> GeneratedPlaylist:
    """Load the complete local catalog and generate a workout playlist."""
    tracks: list[LibraryTrack] = []
    offset = 0
    with LibraryCatalog(database_path) as catalog:
        while True:
            page = catalog.search(LibraryQuery(limit=1000, offset=offset))
            tracks.extend(page)
            if len(page) < 1000:
                break
            offset += len(page)
    return generate_playlist(session, tracks, rules=rules)


def _select_phase_tracks(
    phase: WorkoutPhase,
    candidates: list[LibraryTrack],
    rules: PlaylistGenerationRules,
) -> list[tuple[LibraryTrack, PlaylistRuleScore]]:
    selected: list[tuple[LibraryTrack, PlaylistRuleScore]] = []
    duration = 0.0
    remaining = list(candidates)
    minimum_duration = max(
        0, phase.target_duration_seconds - rules.duration_tolerance_seconds
    )
    while (
        duration < minimum_duration
        and remaining
        and len(selected) < rules.max_tracks_per_phase
    ):
        ranked = [(_score_track(phase, track, duration), track) for track in remaining]
        score, track = min(
            ranked,
            key=lambda candidate: (
                -candidate[0].total,
                candidate[1].title.casefold(),
                str(candidate[1].path).casefold(),
            ),
        )
        selected.append((track, score))
        duration += track.duration_seconds or 0.0
        remaining.remove(track)
    return selected


def _score_track(
    phase: WorkoutPhase, track: LibraryTrack, selected_duration: float
) -> PlaylistRuleScore:
    bpm = _center_fit(track.bpm, phase.min_bpm, phase.max_bpm)
    energy = _center_fit(track.energy_score, phase.min_energy, phase.max_energy)
    remaining = max(0.0, phase.target_duration_seconds - selected_duration)
    duration = max(
        0.0,
        1.0
        - abs(remaining - (track.duration_seconds or 0.0))
        / phase.target_duration_seconds,
    )
    total = bpm * 0.45 + energy * 0.35 + duration * 0.20
    return PlaylistRuleScore(
        bpm=round(bpm * 100, 2),
        energy=round(energy * 100, 2),
        duration=round(duration * 100, 2),
        total=round(total * 100, 2),
    )


def _center_fit(value: float | int | None, minimum: float, maximum: float) -> float:
    if value is None:
        return 0.0
    midpoint = (minimum + maximum) / 2
    half_span = max((maximum - minimum) / 2, 1.0)
    return max(0.0, 1.0 - abs(float(value) - midpoint) / half_span)


def _has_required_metrics(track: LibraryTrack) -> bool:
    return (
        track.duration_seconds is not None
        and track.duration_seconds > 0
        and track.bpm is not None
        and track.energy_score is not None
    )


def _order_for_phase(
    phase_type: WorkoutPhaseType,
    selected: list[tuple[LibraryTrack, PlaylistRuleScore]],
) -> list[tuple[LibraryTrack, PlaylistRuleScore]]:
    if phase_type == WorkoutPhaseType.COOL_DOWN:
        return sorted(
            selected,
            key=lambda item: (
                -(item[0].energy_score or 0),
                -(item[0].bpm or 0),
                item[0].title.casefold(),
            ),
        )
    return sorted(
        selected,
        key=lambda item: (
            item[0].energy_score or 0,
            item[0].bpm or 0,
            item[0].title.casefold(),
        ),
    )
