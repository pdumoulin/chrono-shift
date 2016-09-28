
import sys
import os
import csv
import urllib2
import datetime
import pytz
import time
from blinky import wemo

SWITCH = wemo('192.168.1.81')
TEAM = 'New York Rangers'
WINDOW = 60

def main():
    # did lights go on?
    ran = False

    # download and interate through NYR schedule
    csv_file = open(sys.argv[1], 'r')
    reader = csv.DictReader(csv_file)

    # get current unix timestamp to use later
    current_unix_time = int(time.time())

    for row in reader:

        # only flash lights when nyr is playing
        if row['Home'] != TEAM and row['Away'] != TEAM:
            continue

        # parse gametime string into datetime object
        time_string = ' '.join([row['Date'], row['Time']])
        start = datetime.datetime.strptime(time_string, '%Y-%m-%d %I:%M %p')

        # set the timezone to new york
        local = pytz.timezone('America/New_York')
        local_dt = local.localize(start, is_dst=None)

        # convert from EST or EDT to UTC
        utc_dt = local_dt.astimezone(pytz.utc)

        # compare start time to current time
        start_unix_time = int(utc_dt.strftime("%s"))
        time_diff = start_unix_time - current_unix_time

        # if game started in rolling window in case cron isn't on time
        if time_diff >= (0 - WINDOW) and time_diff <= WINDOW:
            SWITCH.burst(15)
            ran = True
            break

    # put some data into cron.log
    print current_unix_time
    print ran

if __name__ == '__main__':
    main()
