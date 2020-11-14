"""Main execution flow."""

import argparse
import datetime
import os
import pickle
from pathlib import Path

import config


def main():

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers()

    # set schedule events for next 24hrs
    parser_set = subparsers.add_parser('set')
    parser_set.set_defaults(func=run_set)

    # list scheduled events in local time orer
    parser_list = subparsers.add_parser('list')
    parser_list.set_defaults(func=run_list)

    # clear all scheduled events
    parser_clear = subparsers.add_parser('clear')
    parser_clear.set_defaults(func=run_clear)

    # run recentlu scheduled events
    parser_execute = subparsers.add_parser('execute')
    parser_execute.set_defaults(func=run_execute)

    # initialize schedule file if not exits
    if not os.path.isfile(config.SCHEDULE_FILE):
        Path(config.SCHEDULE_FILE).touch()
        reset_events()

    # read args and run corresponding func
    args = parser.parse_args()
    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()


def run_set(args):
    schedule()

def run_list(args):
    for e in list_events(True):
        print(
            e['datetime'].astimezone(config.TIMEZONE_LOCAL),
            _diff_now(e['datetime']),
            type(e['task']),
            e['ran']
        )

def run_clear(args):
    reset_events()

def run_execute(args):
    execute()

def schedule():
    reset_events()
    for task in config.SCHEDULE:
        for event_datetime in task.future_executions():
            append_event(event_datetime, task)


def execute():
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
    _save_data([])


def append_event(event_datetime, task):
    scheduled_events = list_events()
    scheduled_events.append({
        'datetime': event_datetime,
        'task': task,
        'ran': False
    })
    _save_data(scheduled_events)


def list_events(order=False):
    with open(config.SCHEDULE_FILE, 'rb') as schedule:
        scheduled_events = pickle.load(schedule)
    if order:
        return sorted(scheduled_events, key=lambda i: i['datetime'])
    return scheduled_events


def _diff_now(event_datetime):
    return int((datetime.datetime.now(config.TIMEZONE_UTC) - event_datetime).total_seconds())  # noqa:E501


def _save_data(data):
    with open(config.SCHEDULE_FILE, 'wb') as schedule:
        pickle.dump(data, schedule)


if __name__ == '__main__':
    main()
