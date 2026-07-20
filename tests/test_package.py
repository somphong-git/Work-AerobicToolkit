import pytest

from aerobictoolkit import __version__
from aerobictoolkit.cli import _configure_stdout, build_parser


def test_package_has_version():
    assert __version__ == "0.3.0"


def test_cli_parser_accepts_version():
    assert build_parser().prog == "aerobictoolkit"


def test_configure_stdout_handles_streams_without_reconfigure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("aerobictoolkit.cli.sys.stdout", object())

    _configure_stdout()
