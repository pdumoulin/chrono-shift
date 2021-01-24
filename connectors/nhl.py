"""NHL API web interface."""

import requests


def get_schedule(start_date, end_date):
    """Load game data from nhl.com."""
    # load game data for date range (used to load entire month)
    params = {
        'startDate': start_date,
        'endDate': end_date
    }
    url = 'https://statsapi.web.nhl.com/api/v1/schedule'
    response = requests.get(url, params=params)
    data = response.json()
    if data['totalGames'] == 0:
        return []

    # combine all games from dates together
    games = [game for date in data['dates'] for game in date['games']]

    # filter out postponed games, thanks COVID-19
    games = [
        x for x in games
        if x.get('status', {}).get('detailedState', '') != 'Postponed'
    ]
    return games
