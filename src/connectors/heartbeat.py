"""Heartbeat sender."""

import logging
import os

import requests


def send(exit_code):
    """Report on task results."""
    heartbeat_id = os.getenv('HEARTBEAT_ID')
    if not heartbeat_id:
        logging.error('Heartbeat ID not configured')
        return
    url = f'https://uptime.betterstack.com/api/v1/heartbeat/{heartbeat_id}/{exit_code}'  # noqa:E501,E231
    response = requests.get(url)
    try:
        response.raise_for_status()
    except Exception:
        logging.exception('Error Sending Heartbeat')
