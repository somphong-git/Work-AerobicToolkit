import pytest

from aerobictoolkit import __version__
from aerobictoolkit.cli import _configure_stdout, build_parser


def test_package_has_version():
    assert __version__ == "0.7.0"


def test_cli_parser_accepts_version():
    assert build_parser().prog == "aerobictoolkit"


def test_cli_parser_accepts_batch_report_options():
    args = build_parser().parse_args(["batch", "data/input", "--no-bpm", "--no-cache"])

    assert args.command == "batch"
    assert args.no_bpm is True
    assert args.no_cache is True


def test_cli_parser_accepts_tempo_normalization_range():
    args = build_parser().parse_args(
        ["analyze", "track.wav", "--min-bpm", "100", "--max-bpm", "200"]
    )

    assert args.min_bpm == 100.0
    assert args.max_bpm == 200.0


def test_cli_parser_accepts_energy_timeline_options():
    args = build_parser().parse_args(
        ["analyze", "track.wav", "--energy", "--energy-section-seconds", "10"]
    )

    assert args.energy is True
    assert args.energy_section_seconds == 10.0


def test_cli_parser_accepts_musical_key_option():
    args = build_parser().parse_args(["analyze", "track.wav", "--key"])

    assert args.key is True


def test_configure_stdout_handles_streams_without_reconfigure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("aerobictoolkit.cli.sys.stdout", object())

    _configure_stdout()
