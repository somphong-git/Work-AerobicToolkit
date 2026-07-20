"""File-system scanning utilities for audio tracks."""

from pathlib import Path

SUPPORTED_AUDIO_EXTENSIONS = frozenset(
    {".aac", ".flac", ".m4a", ".mp3", ".ogg", ".wav"}
)


def scan_music(folder: str | Path) -> list[Path]:
    """Return supported audio files directly contained in *folder*.

    The scanner deliberately avoids recursive traversal: playlist and project
    organization are application concerns that will be defined in a later sprint.
    """
    directory = Path(folder).expanduser()

    if not directory.is_dir():
        message = f"Input directory does not exist: {directory}"
        raise FileNotFoundError(message)

    return [
        path
        for path in sorted(directory.iterdir())
        if path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS
    ]
