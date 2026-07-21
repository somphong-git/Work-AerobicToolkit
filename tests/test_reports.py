"""Tests for JSON and CSV batch reports."""

import csv
import json
from pathlib import Path

from aerobictoolkit.analysis.models import (
    BatchAnalysisResult,
    BatchTrackAnalysis,
    BeatGrid,
    EnergyAnalysis,
    EnergySection,
    TrackAnalysis,
    TrackAnalysisError,
    TrackMetadata,
)
from aerobictoolkit.export import write_csv_report, write_json_report


def test_reports_include_successes_cache_state_and_errors(tmp_path: Path) -> None:
    track_path = tmp_path / "เพลง.wav"
    analysis = TrackAnalysis(
        TrackMetadata(track_path, "เพลง", "Artist", None, 180.0, "wav", 123),
        bpm=125.5,
        raw_bpm=62.75,
        bpm_confidence=0.91,
        beat_grid=BeatGrid((0.25, 0.728, 1.206)),
        energy=EnergyAnalysis(
            score=7,
            rms_db=-12.5,
            onset_rate=2.1,
            brightness=0.22,
            section_seconds=15.0,
            sections=(EnergySection(0.0, 15.0, 6), EnergySection(15.0, 30.0, 8)),
        ),
    )
    result = BatchAnalysisResult(
        directory=tmp_path,
        tracks=(BatchTrackAnalysis(analysis, from_cache=True),),
        errors=(TrackAnalysisError(tmp_path / "bad.mp3", "ValueError", "bad"),),
        generated_at="2026-07-21T00:00:00+00:00",
    )

    json_path = write_json_report(result, tmp_path / "reports" / "result.json")
    csv_path = write_csv_report(result, tmp_path / "reports" / "result.csv")

    json_data = json.loads(json_path.read_text(encoding="utf-8"))
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        csv_rows = list(csv.DictReader(stream))

    assert json_data["summary"]["cache_hits"] == 1
    assert json_data["summary"]["errors"] == 1
    assert json_data["tracks"][0]["analysis"]["confidence_level"] == "high"
    assert json_data["tracks"][0]["analysis"]["beat_grid"]["beat_count"] == 3
    assert json_data["tracks"][0]["analysis"]["energy"]["score"] == 7
    assert len(json_data["tracks"][0]["analysis"]["energy"]["sections"]) == 2
    assert csv_rows[0]["title"] == "เพลง"
    assert csv_rows[0]["from_cache"] == "True"
    assert csv_rows[0]["bpm_confidence"] == "0.91"
    assert csv_rows[0]["beat_count"] == "3"
    assert csv_rows[0]["energy_score"] == "7"
    assert csv_rows[0]["energy_level"] == "high"
    assert csv_rows[1]["status"] == "error"
    assert csv_rows[1]["error_type"] == "ValueError"
