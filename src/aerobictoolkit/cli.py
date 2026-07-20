"""Command-line adapter for Work-AerobicToolkit's reusable engine."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .analysis import TrackAnalysis, analyze_track, scan_music


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser without invoking domain behavior."""
    parser = argparse.ArgumentParser(
        prog="aerobictoolkit",
        description="Create and analyze DJ mixes for aerobic dance.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command")

    scan_parser = commands.add_parser("scan", help="List supported audio files.")
    scan_parser.add_argument("directory", type=Path)

    analyze_parser = commands.add_parser(
        "analyze", help="Read metadata and estimate a track's BPM."
    )
    analyze_parser.add_argument("path", type=Path)
    analyze_parser.add_argument(
        "--no-bpm", action="store_true", help="Read metadata without BPM analysis."
    )
    analyze_parser.add_argument(
        "--json", action="store_true", help="Print the result as JSON."
    )
    return parser


def main() -> int:
    """Run the selected command-line adapter."""
    _configure_stdout()
    args = build_parser().parse_args()
    if args.command == "scan":
        for track in scan_music(args.directory):
            print(track)
    elif args.command == "analyze":
        result = analyze_track(args.path, include_bpm=not args.no_bpm)
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            _print_analysis(result)
    return 0


def _print_analysis(result: TrackAnalysis) -> None:
    """Render the human-readable CLI representation."""
    metadata = result.metadata
    print(f"Title: {metadata.title}")
    print(f"Artist: {metadata.artist or '-'}")
    print(f"Duration: {metadata.duration_seconds or '-'} seconds")
    print(f"BPM: {result.bpm or '-'}")


def _configure_stdout() -> None:
    """Enable UTF-8 output for local track names on Windows consoles."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
