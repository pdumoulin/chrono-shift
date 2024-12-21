"""Configuration."""

import pytz

from suntime import Sun

from timezonefinder import TimezoneFinder

from src import tasks

# active tasks to schedule and store
SCHEDULE = [
    tasks.NhlGameStartTask('nyr'),
    tasks.SunriseTask(minute_offset=45),
    tasks.SunsetTask(minute_offset=-45)
]

# localization settings
tf = TimezoneFinder()
LONGITUDE = -73.944160
LATITUDE = 40.678177
TIMEZONE_LOCAL = pytz.timezone(tf.timezone_at(lng=LONGITUDE, lat=LATITUDE))
TIMEZONE_UTC = pytz.timezone('UTC')
SUN = Sun(LATITUDE, LONGITUDE)

# home server config
TARANTUNA_BASE_URL = 'http://192.168.50.17'
