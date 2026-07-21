"""Analyze the perceptual energy and timeline of one local track."""

import sys
from pathlib import Path

from aerobictoolkit.analysis import analyze_track


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python examples/energy_scan.py <path-to-audio-file>")
        raise SystemExit(2)

    result = analyze_track(Path(sys.argv[1]), include_energy=True)
    energy = result.energy
    if energy is None:
        raise RuntimeError("Energy analysis did not return a result.")

    print(f"Title: {result.metadata.title}")
    print(f"Energy: {energy.score}/10 ({energy.level})")
    for section in energy.sections:
        print(
            f"{section.start_seconds:7.2f}-{section.end_seconds:7.2f}s: "
            f"{section.score}/10 ({section.level})"
        )


if __name__ == "__main__":
    main()
