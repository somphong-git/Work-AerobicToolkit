"""Analyze one local track and display its estimated BPM."""

import sys
from pathlib import Path

from aerobictoolkit.analysis import analyze_track


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python examples/bpm_scan.py <path-to-audio-file>")
        raise SystemExit(2)

    result = analyze_track(Path(sys.argv[1]))
    print(f"Title: {result.metadata.title}")
    print(f"Normalized BPM: {result.bpm}")
    print(f"Raw BPM: {result.raw_bpm}")
    print(f"Confidence: {result.bpm_confidence} ({result.confidence_level})")
    print(f"Beat count: {result.beat_grid.beat_count if result.beat_grid else 0}")


if __name__ == "__main__":
    main()
