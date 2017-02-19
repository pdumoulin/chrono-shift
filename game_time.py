
import requests
import datetime
import pytz
import time
from BeautifulSoup import BeautifulSoup
from blinky import wemo

SWITCH = wemo('192.168.1.81')
TEAM = 'rangers'
START_YEAR = 2016
TIMEZONE = 'America/New_York'
WINDOW = 60

def main():
    # did lights go on?
    ran = None

    # load printable schedule from nhl.com
    url = 'https://www.nhl.com/%s/schedule/%s/ET/print' % (TEAM, START_YEAR)
    response = requests.get(url)
    schedule = response.content

    # parse HTML to get game times
    games = []
    soup = BeautifulSoup(schedule)
    rows = soup.findAll('tr')
    for row in rows:
        html_data = {}
        columns = row.findAll('td')
        if len(columns) == 4:

            # combine data from columns in each row
            for column in columns:
                html_data[column['class']] = column.string

            # parse data from html to get startime
            game_date = datetime.datetime.strptime(html_data['date-td'], '%b %d')
            game_time = datetime.datetime.strptime(html_data['time-td'], '%I:%M %p')
            if game_date.month > 9:
                year = START_YEAR
            else:
                year = START_YEAR + 1
            day = str(game_date.day).zfill(2)
            month = str(game_date.month).zfill(2)
            hour = str(game_time.hour).zfill(2)
            minute = str(game_time.minute).zfill(2)
            games.append("%s-%s-%s %s:%s" % (year, month, day, hour, minute))

    # get current unix timestamp to use later
    current_unix_time = int(time.time())

    for game in games:

        # parse human time to datetime object
        start = datetime.datetime.strptime(game, '%Y-%m-%d %H:%M')

        # set the timezone to new york
        local = pytz.timezone(TIMEZONE)
        local_dt = local.localize(start, is_dst=None)

        # convert from EST or EDT to UTC
        utc_dt = local_dt.astimezone(pytz.utc)

        # compare start time to current time
        start_unix_time = int(utc_dt.strftime("%s"))
        time_diff = start_unix_time - current_unix_time

        # if game started in rolling window in case cron isn't on time
        if time_diff >= (0 - WINDOW) and time_diff <= WINDOW:
            ran = game
            SWITCH.burst(15)
            ran = True
            break

    # put some data into cron.log
    print len(games)
    print current_unix_time
    print ran

if __name__ == '__main__':
    main()
