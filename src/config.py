import os

import pytz
from suntime import Sun  # type: ignore
from timezonefinder import TimezoneFinder  # type: ignore

from src import constants, tasks

ENVIRONMENT = constants.Environment(os.environ["ENVIRONMENT"])
SENTRY_DSN = os.environ.get("SENTRY_DSN")

# localization settings
tf = TimezoneFinder()
LONGITUDE = -73.944160
LATITUDE = 40.678177
TIMEZONE_LOCAL = pytz.timezone(tf.timezone_at(lng=LONGITUDE, lat=LATITUDE))
TIMEZONE_UTC = pytz.timezone("UTC")
SUN = Sun(LATITUDE, LONGITUDE)

# active tasks to schedule and store
SCHEDULE = [
    tasks.PlugsTask(17, 0, [("patio lights", True)]),
    tasks.PlugsTask(18, 0, [("patio lights", False)]),
    tasks.NhlGameStartTask("nyr"),
    tasks.SunriseTask([("porch lights", False)], minute_offset=30),
    tasks.SunsetTask(
        [("christmas tree", True), ("porch lights", True)], minute_offset=-45
    ),
]

# home server config
TARANTUNA_BASE_URL = "http://192.168.50.17"
