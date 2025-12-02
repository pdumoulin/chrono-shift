from datetime import date

import requests


def get_schedule(start_date: date, team_code: str) -> list[dict]:
    url = f"https://api-web.nhle.com/v1/club-schedule/{team_code}/week/{start_date}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data["games"]
