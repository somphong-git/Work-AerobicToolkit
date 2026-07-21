"""Workout-session modeling and future playlist optimization."""

from .generator import (
    GeneratedPlaylist,
    GeneratedPlaylistPhase,
    PlaylistGenerationRules,
    PlaylistItem,
    PlaylistRuleScore,
    generate_playlist,
    generate_playlist_from_catalog,
)
from .models import (
    CANONICAL_PHASE_ORDER,
    WorkoutPhase,
    WorkoutPhaseType,
    WorkoutSession,
    standard_workout_session,
)

__all__ = [
    "CANONICAL_PHASE_ORDER",
    "GeneratedPlaylist",
    "GeneratedPlaylistPhase",
    "PlaylistGenerationRules",
    "PlaylistItem",
    "PlaylistRuleScore",
    "WorkoutPhase",
    "WorkoutPhaseType",
    "WorkoutSession",
    "generate_playlist",
    "generate_playlist_from_catalog",
    "standard_workout_session",
]
