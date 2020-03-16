"""Turn on lights when hockey game starts."""

import datetime
import time

from blinky import Wemo

import requests

SWITCH = Wemo('192.168.1.81')
TEAM = 'New York Rangers'
WINDOW = 60


def main():
    """Entrypoint of script."""
    # did lights go on?
    ran = False

    # load game data for the next month
    url = 'https://statsapi.web.nhl.com/api/v1/schedule'
    response = requests.get(url)
    data = response.json()
    if data['totalGames'] == 0:
        print('No games today!')
        exit()
    games = data['dates'][0]['games']
    current_unix_time = int(time.time())

    # filter out postponed games, thanks COVID-19
    games = [
        x for x in games
        if x.get('status', {}).get('detailedState', '') != 'Postponed'
    ]

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
            print(d)
            print(time_diff)
            print('')

            # if game started in rolling window in case cron isn't on time
            if time_diff >= (0 - WINDOW) and time_diff <= WINDOW:
                ran = game
                SWITCH.burst(15)
                ran = True
                break

    # put some data into the log
    print(len(games))
    print(current_unix_time)
    print(ran)


if __name__ == '__main__':
    main()
