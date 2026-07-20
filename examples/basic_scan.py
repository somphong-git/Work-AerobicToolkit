"""List supported audio files in the local data/input directory."""

import sys
from pathlib import Path

from aerobictoolkit.analysis import scan_music


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    input_directory = Path(__file__).resolve().parents[1] / "data" / "input"
    tracks = scan_music(input_directory)

    if not tracks:
        print(f"No supported audio files found in {input_directory}")
        return

    for index, track in enumerate(tracks, start=1):
        print(f"{index:03d}. {track.name}")


if __name__ == "__main__":
    main()
