"""Analyze one local track and display its estimated BPM."""

import sys
from pathlib import Path

from aerobictoolkit.analysis import analyze_track


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python examples/bpm_scan.py <path-to-audio-file>")
        raise SystemExit(2)

    result = analyze_track(Path(sys.argv[1]))
    print(f"{result.metadata.title}: {result.bpm} BPM")


if __name__ == "__main__":
    main()
