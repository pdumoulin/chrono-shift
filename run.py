"""Main execution flow."""

import argparse
import datetime
import os
import pickle
import uuid
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
        help='reset tasks by scheduling tasks for next 24hrs based on config.TASKS'
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
        help='run all pending tasks AND reset tasks every config.RESET_INTERVAL seconds'
    )
    parser_execute.set_defaults(func=run_execute)

    # initialize schedule file if not exits
    if not os.path.isfile(config.SCHEDULE_FILE):
        Path(config.SCHEDULE_FILE).touch()
        reset_events([])

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
    (events, timestamp) = _read_data()
    events = sorted(events, key=lambda i: i['datetime'])
    print(timestamp.astimezone(args.tz))
    for e in events:
        print(
            e['datetime'].astimezone(args.tz),
            _diff_now(e['datetime']),
            type(e['task']),
            e['ran'],
            e['id']
        )


def run_clear(args):
    """Run clear command."""
    reset_events([])


def run_execute(args):
    """Run execute command."""
    execute()


def schedule():
    """Read task list and write future tasks to run."""
    events = []
    for task in config.SCHEDULE:
        for d in task.future_executions():
            if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
                raise Exception(f'timezone unware datetime obj for {type(task)}')  # noqa:E501
            events.append({
                'datetime': d,
                'task': task,
                'ran': False,
                'id': uuid.uuid4()
            })
    reset_events(events)


def execute():
    """Run task(s) if in time window after event runtime."""
    # get events from schedule, filter out already ran
    (events, timestamp) = _read_data()
    events = [x for x in events if not x['ran']]

    # examine event datetimes
    for event in events:

        # execute task if schedule time was in the past
        schedule_diff = _diff_now(event['datetime'])
        if schedule_diff >= 0:
            # save task ran state
            record_event_run(event)
            event['task'].execute()


    since_last = datetime.datetime.now(config.TIMEZONE_UTC) - timestamp
    if since_last.total_seconds() >= config.RESET_INTERVAL:
        schedule()


def record_event_run(event):
    """Mark that event has run."""
    (events, timestamp) = _read_data()
    for e in events:
        if e['id'] == event['id']:
            e['ran'] = True
            _write_data(events, timestamp)
            break


def reset_events(events):
    """Clear out all scheduled tasks."""
    timestamp = datetime.datetime.now(config.TIMEZONE_UTC)
    _write_data(events, timestamp)


def _diff_now(event_datetime):
    """Seconds between now and input (positive means input in past)."""
    return int((datetime.datetime.now(config.TIMEZONE_UTC) - event_datetime).total_seconds())  # noqa:E501


def _read_data():
    with open(config.SCHEDULE_FILE, 'rb') as schedule:
        data = pickle.load(schedule)
    return (data['events'], data['timestamp'])


def _write_data(events, timestamp):
    """Write object to schedule pickle file."""
    with open(config.SCHEDULE_FILE, 'wb') as schedule:
        pickle.dump({
            'events': events,
            'timestamp': timestamp
        }, schedule)


if __name__ == '__main__':
    main()
