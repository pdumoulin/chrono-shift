import logging
import time
from datetime import datetime, timedelta, timezone

import sentry_sdk
from pydantic import BaseModel

from src import config, constants
from src.tasks import BaseTask

if config.ENVIRONMENT != constants.Environment.DEV or config.SENTRY_DSN:
    sentry_sdk.init(dsn=config.SENTRY_DSN, environment=config.ENVIRONMENT.value)


class TaskExecution(BaseModel):
    dt: datetime
    task: BaseTask

    class Config:
        arbitrary_types_allowed = True


def run() -> None:
    logging.info("Script Start")
    exit_code = 0
    executions: list[TaskExecution] = []
    try:
        # run script for 1 day
        stop_time = datetime.now(config.TIMEZONE_LOCAL) + timedelta(days=1)
        logging.info(f"Run Until: {stop_time}")

        # generate future execution events from tasks
        for task in config.SCHEDULE:
            for dtime in task.future_executions():
                executions.append(
                    TaskExecution(dt=dtime.astimezone(config.TIMEZONE_LOCAL), task=task)
                )

        # filter out executions outside of script runtime
        executions = [
            x for x in executions if x.dt < stop_time
        ]

        # validate task times
        for execution in sorted(executions, key=lambda e: e.dt):
            logging.info(
                f"Scheduled Task: {type(execution.task).__name__} @ {execution.dt}"
            )

        # run tasks, pausing in between
        for execution in sorted(executions, key=lambda e: e.dt):
            sleep_until(execution.dt)
            logging.info(f"Run Task: {type(execution.task).__name__}")
            try:
                execution.task.execute()
            except Exception as e:
                logging.exception(
                    f"Error Running Task: {type(execution.task).__name__}"
                )
                sentry_sdk.capture_exception(e)
                exit_code = 1
            else:
                logging.info(f"Completed Task: {type(execution.task).__name__}")

        # sleep until time to exit and auto-restart
        sleep_until(stop_time)
    except Exception as e:
        logging.exception("Unexpected error")
        sentry_sdk.capture_exception(e)
        exit_code = 2

    # exit
    logging.info(f"Script End ({exit_code})")
    exit(exit_code)


def sleep_until(target: datetime) -> None:
    now = datetime.now(timezone.utc)
    if target.tzinfo is None:
        raise Exception(f'target datetime "{target}" has no tzinfo"')
    if target < now:
        logging.info(f"Skipping Sleep: {target}")
        return
    diff = (target - now).seconds
    logging.info(f"Sleeping Until: {target}")
    time.sleep(diff)
