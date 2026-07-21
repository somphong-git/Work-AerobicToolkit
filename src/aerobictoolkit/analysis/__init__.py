"""Public contracts for inspecting and analyzing audio tracks."""

from .batch import analyze_directory
from .models import (
    BatchAnalysisResult,
    BatchTrackAnalysis,
    TrackAnalysis,
    TrackAnalysisError,
    TrackMetadata,
)
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
    "BatchAnalysisResult",
    "BatchTrackAnalysis",
    "TrackAnalysis",
    "TrackAnalysisError",
    "TrackMetadata",
    "analyze_directory",
    "analyze_track",
    "estimate_bpm",
    "read_track_metadata",
    "scan_music",
]
