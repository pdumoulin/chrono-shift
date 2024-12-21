"""App entrypoint."""

import logging

from src import run

logging.basicConfig(
    level=logging.INFO,
    format='[%(process)d][%(asctime)s.%(msecs)03d] %(levelname)s [%(thread)d] - %(message)s',  # noqa:E501
    handlers=[
        logging.FileHandler('/tmp/logs/app.log'),
        logging.StreamHandler()
    ]
)
run()
