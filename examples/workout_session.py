"""Create a reusable 60-minute workout-session blueprint."""

import json

from aerobictoolkit.playlist import standard_workout_session

session = standard_workout_session("Friday Aerobic Class")
print(json.dumps(session.to_dict(), ensure_ascii=False, indent=2))
