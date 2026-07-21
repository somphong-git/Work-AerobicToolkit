"""Generate a standard workout playlist from the local catalog."""

import json

from aerobictoolkit.playlist import (
    generate_playlist_from_catalog,
    standard_workout_session,
)

session = standard_workout_session("Example Aerobic Class")
playlist = generate_playlist_from_catalog(session)
print(json.dumps(playlist.to_dict(), ensure_ascii=False, indent=2))
