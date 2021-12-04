"""Configuration."""

import pytz

from suntime import Sun

import tasks

from timezonefinder import TimezoneFinder

# active tasks to schedule and store
SCHEDULE = [
    tasks.NhlGameStartTask('New York Rangers'),
    tasks.SunriseTask(),
    tasks.SunsetTask()
]
SCHEDULE_FILE = '/home/pi/chrono-shift/schedule.p'

# localization settings
tf = TimezoneFinder()
LONGITUDE = -73.944160
LATITUDE = 40.678177
TIMEZONE_LOCAL = pytz.timezone(tf.timezone_at(lng=LONGITUDE, lat=LATITUDE))
TIMEZONE_UTC = pytz.timezone('UTC')
SUN = Sun(LATITUDE, LONGITUDE)

# allowed diff between task schedule time and execute time
WINDOW = 60

# how often to clear and build task list
RESET_INTERVAL = 86400

# switch settings
PATIO_IP = '192.168.50.200'
PORCH_IP = '192.168.50.242'
LIVING_ROOM_IP = '192.168.50.196'
GOAL_IP = '192.168.50.100'
