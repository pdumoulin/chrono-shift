"""App run logic."""

import logging
import time
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from src import config
from src.connectors import heartbeat


def run():
    """Start script."""
    logging.info('Script Start')
    exit_code = 0
    executions = []
    try:

        # run script for 1 day
        stop_time = datetime.now(config.TIMEZONE_LOCAL) + timedelta(days=1)
        logging.info(f'Run Until: {stop_time}')

        # generate future execution events from tasks
        for task in config.SCHEDULE:
            for dtime in task.future_executions():
                executions.append({
                    'datetime': dtime.astimezone(config.TIMEZONE_LOCAL),
                    'task': task
                })

        # validate task times
        for execution in sorted(executions, key=lambda e: e['datetime']):
            logging.info(f"Scheduled Task: {type(execution['task']).__name__} @ {execution['datetime']}")  # noqa:E501
            execution_dt = execution['datetime']
            if execution_dt > stop_time:
                raise Exception('Task execution scheduled for after script stop time')  # noqa:E501

        # run tasks, pausing in between
        for execution in sorted(executions, key=lambda e: e['datetime']):
            sleep_until(execution['datetime'])
            logging.info(f"Run Task: {type(execution['task']).__name__}")
            try:
                execution['task'].execute()
            except Exception:
                logging.exception(f"Error Running Task: {type(execution['task']).__name__}")  # noqa:E501
                exit_code = 1
            else:
                logging.info(f"Completed Task: {type(execution['task']).__name__}")  # noqa:E501

        # sleep until time to exit and auto-restart
        sleep_until(stop_time)
    except Exception:
        logging.exception('Unexpected error')
        exit_code = 2

    # exit and send heartbeat
    heartbeat.send(exit_code)
    logging.info(f"Script End ({exit_code})")
    exit(exit_code)


def sleep_until(target: datetime):
    """Pause until specified datetime."""
    now = datetime.now(timezone.utc)
    if target.tzinfo is None:
        raise Exception(f'target datetime "{target}" has no tzinfo"')
    if target < now:
        logging.info(f'Skipping Sleep: {target}')
        return
    diff = (target - now).seconds
    logging.info(f'Sleeping Until: {target}')
    time.sleep(diff)
