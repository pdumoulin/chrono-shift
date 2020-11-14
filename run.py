"""Main execution flow."""

import argparse
import datetime
import os
import pickle
from pathlib import Path

import config

import pytz


def main():
    """Entrypoint."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # set schedule events for next 24hrs
    parser_set = subparsers.add_parser(
        'set',
        help='reset and schedule tasks for next 24hrs based on config.TASKS'
    )
    parser_set.set_defaults(func=run_set)

    # list scheduled events in local time orer
    parser_list = subparsers.add_parser(
        'list',
        help='view currently set task schedule',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser_list.add_argument(
        '--tz', type=str, required=False,
        default=config.TIMEZONE_LOCAL,
        help='timezone to display scheduled datetimes')
    parser_list.set_defaults(func=run_list)

    # clear all scheduled events
    parser_clear = subparsers.add_parser(
        'clear',
        help='delete all scheduled tasks'
    )
    parser_clear.set_defaults(func=run_clear)

    # run recently scheduled events
    parser_execute = subparsers.add_parser(
        'execute',
        help=f'run any pending task in recent time window of {config.WINDOW}s'
    )
    parser_execute.set_defaults(func=run_execute)

    # initialize schedule file if not exits
    if not os.path.isfile(config.SCHEDULE_FILE):
        Path(config.SCHEDULE_FILE).touch()
        reset_events()

    # read args and run corresponding func
    args = parser.parse_args()
    if 'tz' in args and type(args.tz) == str:
        args.tz = pytz.timezone(args.tz)
    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()


def run_set(args):
    """Run set command."""
    schedule()


def run_list(args):
    """Run list command."""
    for e in list_events(True):
        print(
            e['datetime'].astimezone(args.tz),
            _diff_now(e['datetime']),
            type(e['task']),
            e['ran']
        )


def run_clear(args):
    """Run clear command."""
    reset_events()


def run_execute(args):
    """Run execute command."""
    execute()


def schedule():
    """Read task list and write future tasks to run."""
    reset_events()
    for task in config.SCHEDULE:
        for event_datetime in task.future_executions():
            append_event(event_datetime, task)


def execute():
    """Run task(s) if in time window after event runtime."""
    # get events from schedule, filter out already ran
    events = [x for x in list_events() if not x['ran']]

    # examine event datetimes
    for event in events:

        # execute task if runtime was recent and in the past
        schedule_diff = _diff_now(event['datetime'])
        if schedule_diff >= 0 and schedule_diff < config.WINDOW:
            event['task'].execute()

            # save task ran state
            event['ran'] = True
            _save_data(events)


def reset_events():
    """Clear out all scheduled tasks."""
    _save_data([])


def append_event(event_datetime, task):
    """Add new scheduled task."""
    scheduled_events = list_events()
    scheduled_events.append({
        'datetime': event_datetime,
        'task': task,
        'ran': False
    })
    _save_data(scheduled_events)


def list_events(order=False):
    """Output scheduled tasks."""
    with open(config.SCHEDULE_FILE, 'rb') as schedule:
        scheduled_events = pickle.load(schedule)
    if order:
        return sorted(scheduled_events, key=lambda i: i['datetime'])
    return scheduled_events


def _diff_now(event_datetime):
    """Seconds between now and input (positive menas input in past)."""
    return int((datetime.datetime.now(config.TIMEZONE_UTC) - event_datetime).total_seconds())  # noqa:E501


def _save_data(data):
    """Write object to schedule pickle file."""
    with open(config.SCHEDULE_FILE, 'wb') as schedule:
        pickle.dump(data, schedule)


if __name__ == '__main__':
    main()
