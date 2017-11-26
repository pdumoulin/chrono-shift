
import time
import datetime
import requests
import json

from blinky import wemo

SWITCH = wemo('192.168.1.81')
TEAM = 'New York Rangers'
WINDOW = 60

def main():

    # did lights go on?
    ran = False

    # load game data for the next month
    url = 'https://statsapi.web.nhl.com/api/v1/schedule'
    today = datetime.date.today().strftime('%Y-%m-%d')
    future = datetime.date.today() + datetime.timedelta(30)
    response = requests.get(url)
    data = json.loads(response.content)
    games = data['dates'][0]['games']

    current_unix_time = int(time.time())

    # find if game just started    
    for game in games:
        home_team = game['teams']['home']['team']['name']
        away_team = game['teams']['away']['team']['name']

        # only light 'em up for boys in blue
        if home_team == TEAM or away_team == TEAM:
            game_start = game['gameDate']
            d = datetime.datetime.strptime(game_start, '%Y-%m-%dT%H:%M:%SZ')

            # compare start time to current time
            start_unix_time = int(time.mktime(d.timetuple()))
            time_diff = start_unix_time - current_unix_time

            # if game started in rolling window in case cron isn't on time
            if time_diff >= (0 - WINDOW) and time_diff <= WINDOW:
                ran = game
                SWITCH.burst(15)
                ran = True
                break

    # put some data into the log
    print len(games)
    print current_unix_time
    print ''
    print today
    print future
    print ''
    print ran

if __name__ == '__main__':
    main()
