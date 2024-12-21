"""Home server interface."""

import json

import requests

from src import config

HEADERS = {'content-type': 'application/json'}


def update_plug(index: int, status: bool) -> None:
    """Update plug status."""
    url = f'{config.TARANTUNA_BASE_URL}/plugs/{index}'
    body = json.dumps({'status': status})
    response = requests.patch(url, data=body, headers=HEADERS)
    response.raise_for_status()


def list_plugs(name_filter=None) -> list[dict]:
    """Get all available plugs."""
    url = f'{config.TARANTUNA_BASE_URL}/plugs'
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    if name_filter:
        data = [
            plug
            for plug in data
            if any(
                [
                    name in plug['name'].lower()
                    for name in name_filter
                ]
            )
        ]
    return data
