from pathlib import Path

SUPPORTED = {
    ".mp3",
    ".wav",
    ".flac",
    ".m4a",
    ".aac",
    ".ogg"
}


def scan_music(folder: str):
    folder = Path(folder)

    if not folder.exists():
        raise FileNotFoundError(folder)

    songs = []

    for file in sorted(folder.iterdir()):
        if file.suffix.lower() in SUPPORTED:
            songs.append(file)

    return songs