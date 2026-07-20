"""Command-line entry point for Work-AerobicToolkit."""

from __future__ import annotations

import argparse

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aerobictoolkit",
        description="Create and analyze DJ mixes for aerobic dance.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    return parser


def main() -> int:
    build_parser().parse_args()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

