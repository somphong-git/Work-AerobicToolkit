from pathlib import Path

import pytest

from aerobictoolkit.analysis import scan_music


def test_scan_music_returns_supported_files_in_name_order(tmp_path: Path):
    (tmp_path / "zeta.wav").touch()
    (tmp_path / "alpha.MP3").touch()
    (tmp_path / "notes.txt").touch()
    (tmp_path / "nested").mkdir()

    tracks = scan_music(tmp_path)

    assert [track.name for track in tracks] == ["alpha.MP3", "zeta.wav"]


def test_scan_music_requires_an_existing_directory(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="Input directory does not exist"):
        scan_music(tmp_path / "missing")
