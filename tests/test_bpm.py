"""Foundation coverage reserved for the future BPM-analysis feature."""

import aerobictoolkit.analysis as analysis


def test_analysis_boundary_is_importable_without_optional_audio_dependencies():
    assert analysis.__name__ == "aerobictoolkit.analysis"
