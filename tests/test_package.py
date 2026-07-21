import pytest

from aerobictoolkit import __version__
from aerobictoolkit.cli import _configure_stdout, build_parser


def test_package_has_version():
    assert __version__ == "0.9.0"


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


def test_cli_parser_accepts_library_index_options():
    args = build_parser().parse_args(
        ["library", "index", "data/input", "--no-bpm", "--energy", "--key"]
    )

    assert args.command == "library"
    assert args.library_command == "index"
    assert args.no_bpm is True
    assert args.energy is True
    assert args.key is True


def test_cli_parser_accepts_library_search_filters():
    args = build_parser().parse_args(
        [
            "library",
            "search",
            "warmup",
            "--min-bpm",
            "120",
            "--max-energy",
            "8",
            "--tag",
            "cardio",
        ]
    )

    assert args.text == "warmup"
    assert args.min_bpm == 120.0
    assert args.max_energy == 8
    assert args.tag == ["cardio"]


@pytest.mark.parametrize("command", ["export", "import", "backup"])
def test_cli_parser_accepts_library_transfer_commands(command: str):
    args = build_parser().parse_args(
        ["library", command, "data/reports/library.json", "--database", "catalog.db"]
    )

    assert args.library_command == command
    assert args.database.name == "catalog.db"


def test_configure_stdout_handles_streams_without_reconfigure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("aerobictoolkit.cli.sys.stdout", object())

    _configure_stdout()
