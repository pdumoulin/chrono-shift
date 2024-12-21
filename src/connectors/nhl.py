"""NHL API web interface."""

import requests


def get_schedule(start_date, team_code):
    """Load game data from nhl.com."""
    url = f'https://api-web.nhle.com/v1/club-schedule/{team_code}/week/{start_date}'  # noqa:E231,E501
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data['games']
