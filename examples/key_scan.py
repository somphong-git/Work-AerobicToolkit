"""Detect musical key and compatible DJ-wheel positions for one track."""

import sys
from pathlib import Path

from aerobictoolkit.analysis import analyze_track


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python examples/key_scan.py <path-to-audio-file>")
        raise SystemExit(2)

    result = analyze_track(Path(sys.argv[1]), include_bpm=False, include_key=True)
    key = result.musical_key
    if key is None:
        raise RuntimeError("Musical-key analysis did not return a result.")

    print(f"Title: {result.metadata.title}")
    print(f"Key: {key.name}")
    print(f"Camelot / Open Key: {key.camelot} / {key.open_key}")
    print(f"Confidence: {key.confidence} ({key.confidence_level})")
    print(f"Compatible Camelot: {', '.join(key.compatible_camelot)}")
    print(f"Compatible Open Key: {', '.join(key.compatible_open_key)}")


if __name__ == "__main__":
    main()
