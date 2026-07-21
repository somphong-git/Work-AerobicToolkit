"""Command-line adapter for Work-AerobicToolkit's reusable engine."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .analysis import (
    AudioAnalysisDependencyError,
    BatchAnalysisResult,
    TrackAnalysis,
    analyze_directory,
    analyze_track,
    scan_music,
)
from .export import write_csv_report, write_json_report
from .library import (
    DEFAULT_LIBRARY_PATH,
    LibraryCatalog,
    LibraryQuery,
    index_directory,
)


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
    _add_energy_options(analyze_parser)
    _add_key_option(analyze_parser)
    _add_tempo_range_options(analyze_parser)

    batch_parser = commands.add_parser(
        "batch", help="Analyze a directory and write JSON and CSV reports."
    )
    batch_parser.add_argument("directory", type=Path)
    batch_parser.add_argument(
        "--no-bpm", action="store_true", help="Read metadata without BPM analysis."
    )
    batch_parser.add_argument(
        "--no-cache", action="store_true", help="Do not read or write the cache."
    )
    batch_parser.add_argument(
        "--cache",
        type=Path,
        default=Path("data/cache/analysis-cache.json"),
        help="Cache file path.",
    )
    batch_parser.add_argument(
        "--json-report",
        type=Path,
        default=Path("data/reports/analysis-report.json"),
        help="JSON report path.",
    )
    batch_parser.add_argument(
        "--csv-report",
        type=Path,
        default=Path("data/reports/analysis-report.csv"),
        help="CSV report path.",
    )
    _add_energy_options(batch_parser)
    _add_key_option(batch_parser)
    _add_tempo_range_options(batch_parser)

    library_parser = commands.add_parser(
        "library", help="Build and search the local music catalog."
    )
    library_commands = library_parser.add_subparsers(dest="library_command")
    index_parser = library_commands.add_parser(
        "index", help="Analyze a directory and update the catalog."
    )
    index_parser.add_argument("directory", type=Path)
    _add_database_option(index_parser)
    index_parser.add_argument("--no-bpm", action="store_true")
    index_parser.add_argument("--no-cache", action="store_true")
    index_parser.add_argument(
        "--cache", type=Path, default=Path("data/cache/analysis-cache.json")
    )
    _add_energy_options(index_parser)
    _add_key_option(index_parser)
    _add_tempo_range_options(index_parser)

    search_parser = library_commands.add_parser(
        "search", help="Search and filter indexed tracks."
    )
    search_parser.add_argument("text", nargs="?")
    _add_database_option(search_parser)
    search_parser.add_argument("--min-bpm", type=float)
    search_parser.add_argument("--max-bpm", type=float)
    search_parser.add_argument("--min-energy", type=int)
    search_parser.add_argument("--max-energy", type=int)
    search_parser.add_argument("--camelot")
    search_parser.add_argument("--mode", choices=("major", "minor"))
    search_parser.add_argument("--format", dest="file_format")
    search_parser.add_argument("--tag", action="append", default=[])
    search_parser.add_argument("--limit", type=int, default=100)
    search_parser.add_argument("--offset", type=int, default=0)
    search_parser.add_argument("--json", action="store_true")

    for name, help_text in (
        ("tag", "Attach tags to an indexed track."),
        ("untag", "Remove tags from an indexed track."),
    ):
        tag_parser = library_commands.add_parser(name, help=help_text)
        tag_parser.add_argument("path", type=Path)
        tag_parser.add_argument("tags", nargs="+")
        _add_database_option(tag_parser)
    tags_parser = library_commands.add_parser("tags", help="List known tags.")
    _add_database_option(tags_parser)
    return parser


def main() -> int:
    """Run the selected command-line adapter."""
    _configure_stdout()
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "scan":
            for track in scan_music(args.directory):
                print(track)
        elif args.command == "analyze":
            result = analyze_track(
                args.path,
                include_bpm=not args.no_bpm,
                include_energy=args.energy,
                include_key=args.key,
                min_bpm=args.min_bpm,
                max_bpm=args.max_bpm,
                energy_section_seconds=args.energy_section_seconds,
            )
            if args.json:
                print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
            else:
                _print_analysis(result)
        elif args.command == "batch":
            return _run_batch(args)
        elif args.command == "library":
            return _run_library(args, parser)
        else:
            parser.print_help()
        return 0
    except (AudioAnalysisDependencyError, OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


def _print_analysis(result: TrackAnalysis) -> None:
    """Render the human-readable CLI representation."""
    metadata = result.metadata
    print(f"Title: {metadata.title}")
    print(f"Artist: {metadata.artist or '-'}")
    print(f"Duration: {metadata.duration_seconds or '-'} seconds")
    print(f"BPM: {result.bpm or '-'}")
    print(f"Raw BPM: {result.raw_bpm or '-'}")
    confidence = result.bpm_confidence
    print(f"Confidence: {confidence if confidence is not None else '-'}")
    print(f"Confidence level: {result.confidence_level or '-'}")
    print(f"Beats detected: {result.beat_grid.beat_count if result.beat_grid else 0}")
    if result.energy:
        section_scores = [section.score for section in result.energy.sections]
        print(f"Energy: {result.energy.score}/10 ({result.energy.level})")
        print(
            f"Energy sections: {len(section_scores)} "
            f"(range {min(section_scores)}-{max(section_scores)})"
        )
    if result.musical_key:
        key = result.musical_key
        print(f"Key: {key.name}")
        print(f"Camelot / Open Key: {key.camelot} / {key.open_key}")
        print(f"Key confidence: {key.confidence} ({key.confidence_level})")
        print(f"Compatible Camelot: {', '.join(key.compatible_camelot)}")


def _run_batch(args: argparse.Namespace) -> int:
    cache_path = None if args.no_cache else args.cache
    result = analyze_directory(
        args.directory,
        include_bpm=not args.no_bpm,
        include_energy=args.energy,
        include_key=args.key,
        cache_path=cache_path,
        min_bpm=args.min_bpm,
        max_bpm=args.max_bpm,
        energy_section_seconds=args.energy_section_seconds,
    )
    json_path = write_json_report(result, args.json_report)
    csv_path = write_csv_report(result, args.csv_report)
    _print_batch_summary(result, json_path=json_path, csv_path=csv_path)
    return 1 if result.errors else 0


def _print_batch_summary(
    result: BatchAnalysisResult, *, json_path: Path, csv_path: Path
) -> None:
    print(f"Tracks found: {result.total_count}")
    print(f"Successful: {result.success_count}")
    print(f"Analyzed now: {result.analyzed_count}")
    print(f"Cache hits: {result.cache_hit_count}")
    print(f"Errors: {result.error_count}")
    print(f"JSON report: {json_path}")
    print(f"CSV report: {csv_path}")
    for warning in result.cache_warnings:
        print(f"Cache warning: {warning}", file=sys.stderr)
    for error in result.errors:
        print(
            f"Failed: {error.path} ({error.error_type}: {error.message})",
            file=sys.stderr,
        )


def _run_library(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    if args.library_command == "index":
        result = index_directory(
            args.directory,
            database_path=args.database,
            include_bpm=not args.no_bpm,
            include_energy=args.energy,
            include_key=args.key,
            cache_path=None if args.no_cache else args.cache,
            min_bpm=args.min_bpm,
            max_bpm=args.max_bpm,
            energy_section_seconds=args.energy_section_seconds,
        )
        print(f"Tracks discovered: {result.discovered}")
        print(f"Indexed: {result.indexed}")
        print(f"Cache hits: {result.cache_hits}")
        print(f"Errors: {result.errors}")
        print(f"Catalog: {args.database}")
        return 1 if result.errors else 0

    if args.library_command == "search":
        query = LibraryQuery(
            text=args.text,
            min_bpm=args.min_bpm,
            max_bpm=args.max_bpm,
            min_energy=args.min_energy,
            max_energy=args.max_energy,
            camelot=args.camelot,
            mode=args.mode,
            file_format=args.file_format,
            tags=tuple(args.tag),
            limit=args.limit,
            offset=args.offset,
        )
        with LibraryCatalog(args.database) as catalog:
            tracks = catalog.search(query)
        if args.json:
            print(
                json.dumps(
                    [track.to_dict() for track in tracks],
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            for track in tracks:
                metrics = [
                    f"{track.bpm:g} BPM" if track.bpm is not None else "BPM -",
                    f"energy {track.energy_score}"
                    if track.energy_score is not None
                    else "energy -",
                    track.camelot or "key -",
                ]
                tags = f" [{', '.join(track.tags)}]" if track.tags else ""
                print(f"{track.title} | {' | '.join(metrics)}{tags}")
                print(f"  {track.path}")
            print(f"Matches: {len(tracks)}")
        return 0

    if args.library_command in {"tag", "untag"}:
        with LibraryCatalog(args.database) as catalog:
            if args.library_command == "tag":
                track = catalog.add_tags(args.path, args.tags)
            else:
                track = catalog.remove_tags(args.path, args.tags)
        print(f"Tags for {track.title}: {', '.join(track.tags) or '-'}")
        return 0

    if args.library_command == "tags":
        with LibraryCatalog(args.database) as catalog:
            tags = catalog.list_tags()
        for name, count in tags:
            print(f"{name}: {count}")
        return 0

    parser.parse_args(["library", "--help"])
    return 0


def _add_tempo_range_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--min-bpm",
        type=float,
        default=90.0,
        help="Lower bound for octave-normalized BPM (default: 90).",
    )
    parser.add_argument(
        "--max-bpm",
        type=float,
        default=180.0,
        help="Upper bound for octave-normalized BPM (default: 180).",
    )


def _add_energy_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--energy",
        action="store_true",
        help="Calculate an energy score and section timeline.",
    )
    parser.add_argument(
        "--energy-section-seconds",
        type=float,
        default=15.0,
        help="Length of each energy timeline section (default: 15 seconds).",
    )


def _add_key_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--key",
        action="store_true",
        help="Detect musical key and Camelot/Open Key notation.",
    )


def _add_database_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_LIBRARY_PATH,
        help=f"SQLite catalog path (default: {DEFAULT_LIBRARY_PATH}).",
    )


def _configure_stdout() -> None:
    """Enable UTF-8 output for local track names on Windows consoles."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
