"""Public contracts for inspecting and analyzing audio tracks."""

from .models import TrackAnalysis, TrackMetadata
from .scanner import SUPPORTED_AUDIO_EXTENSIONS, scan_music
from .service import (
    AudioAnalysisDependencyError,
    analyze_track,
    estimate_bpm,
    read_track_metadata,
)

__all__ = [
    "SUPPORTED_AUDIO_EXTENSIONS",
    "AudioAnalysisDependencyError",
    "TrackAnalysis",
    "TrackMetadata",
    "analyze_track",
    "estimate_bpm",
    "read_track_metadata",
    "scan_music",
]
