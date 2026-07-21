"""Public contracts for inspecting and analyzing audio tracks."""

from .batch import analyze_directory
from .energy import DEFAULT_ENERGY_SECTION_SECONDS
from .models import (
    BatchAnalysisResult,
    BatchTrackAnalysis,
    BeatGrid,
    EnergyAnalysis,
    EnergySection,
    TempoAnalysis,
    TrackAnalysis,
    TrackAnalysisError,
    TrackMetadata,
    energy_level,
)
from .scanner import SUPPORTED_AUDIO_EXTENSIONS, scan_music
from .service import (
    DEFAULT_MAX_BPM,
    DEFAULT_MIN_BPM,
    AudioAnalysisDependencyError,
    analyze_energy,
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
    "DEFAULT_ENERGY_SECTION_SECONDS",
    "DEFAULT_MAX_BPM",
    "DEFAULT_MIN_BPM",
    "EnergyAnalysis",
    "EnergySection",
    "TempoAnalysis",
    "TrackAnalysis",
    "TrackAnalysisError",
    "TrackMetadata",
    "analyze_directory",
    "analyze_energy",
    "analyze_track",
    "analyze_tempo",
    "estimate_bpm",
    "energy_level",
    "normalize_tempo",
    "read_track_metadata",
    "scan_music",
]
