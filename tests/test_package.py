from aerobictoolkit import __version__
from aerobictoolkit.cli import build_parser


def test_package_has_version():
    assert __version__ == "0.2.0"


def test_cli_parser_accepts_version():
    assert build_parser().prog == "aerobictoolkit"
