"""Public contracts for inspecting and analyzing audio tracks."""

from .batch import analyze_directory
from .models import (
    BatchAnalysisResult,
    BatchTrackAnalysis,
    BeatGrid,
    TempoAnalysis,
    TrackAnalysis,
    TrackAnalysisError,
    TrackMetadata,
)
from .scanner import SUPPORTED_AUDIO_EXTENSIONS, scan_music
from .service import (
    DEFAULT_MAX_BPM,
    DEFAULT_MIN_BPM,
    AudioAnalysisDependencyError,
    analyze_tempo,
    analyze_track,
    estimate_bpm,
    normalize_tempo,
    read_track_metadata,
)

__all__ = [
    "SUPPORTED_AUDIO_EXTENSIONS",
    "AudioAnalysisDependencyError",
    "BatchAnalysisResult",
    "BatchTrackAnalysis",
    "BeatGrid",
    "DEFAULT_MAX_BPM",
    "DEFAULT_MIN_BPM",
    "TempoAnalysis",
    "TrackAnalysis",
    "TrackAnalysisError",
    "TrackMetadata",
    "analyze_directory",
    "analyze_track",
    "analyze_tempo",
    "estimate_bpm",
    "normalize_tempo",
    "read_track_metadata",
    "scan_music",
]
