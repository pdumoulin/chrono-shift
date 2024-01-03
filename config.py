"""Configuration."""

import pytz

from suntime import Sun

import tasks

from timezonefinder import TimezoneFinder

# active tasks to schedule and store
SCHEDULE = [
    tasks.NhlGameStartTask('nyr'),
    tasks.SunriseTask(),
    tasks.SunsetTask(minute_offset=-45)
]
SCHEDULE_FILE = '/home/pi/projects/chrono-shift/schedule.p'

# localization settings
tf = TimezoneFinder()
LONGITUDE = -73.944160
LATITUDE = 40.678177
TIMEZONE_LOCAL = pytz.timezone(tf.timezone_at(lng=LONGITUDE, lat=LATITUDE))
TIMEZONE_UTC = pytz.timezone('UTC')
SUN = Sun(LATITUDE, LONGITUDE)

# how often to clear and build task list
RESET_INTERVAL = 86400

# switch settings
PATIO_IP = '192.168.50.200'
LIVING_ROOM_IP_1 = '192.168.50.196'
LIVING_ROOM_IP_2 = '192.168.50.190'
GOAL_IP = '192.168.50.100'
