"""NHL API web interface."""

import requests


def get_schedule():
    """Load game data from nhl.com."""
    # load game data for the next month
    url = 'https://statsapi.web.nhl.com/api/v1/schedule'
    response = requests.get(url)
    data = response.json()
    if data['totalGames'] == 0:
        return []
    games = data['dates'][0]['games']

    # filter out postponed games, thanks COVID-19
    games = [
        x for x in games
        if x.get('status', {}).get('detailedState', '') != 'Postponed'
    ]
    return games
