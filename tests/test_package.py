import pytest

from aerobictoolkit import __version__
from aerobictoolkit.cli import _configure_stdout, build_parser


def test_package_has_version():
    assert __version__ == "0.4.0"


def test_cli_parser_accepts_version():
    assert build_parser().prog == "aerobictoolkit"


def test_cli_parser_accepts_batch_report_options():
    args = build_parser().parse_args(["batch", "data/input", "--no-bpm", "--no-cache"])

    assert args.command == "batch"
    assert args.no_bpm is True
    assert args.no_cache is True


def test_configure_stdout_handles_streams_without_reconfigure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("aerobictoolkit.cli.sys.stdout", object())

    _configure_stdout()
