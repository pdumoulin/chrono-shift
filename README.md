# chrono-shift
Daily python task scheduler for localized timezones and dynamic events.


## Setup

### Packages
* python >= 3.6 required
* install python packages in `requirements.txt`

### Crontab
Assuming repo is cloned into `/home/pi/chrono-shift/`
```
# run scheduler at midnight system time
0 0 * * * /home/pi/chrono-shift/run.sh set >> /home/pi/chrono-shift/cron-set.log 2>&1

# run executor every minute
* * * * * /home/pi/chrono-shift/run.sh execute >> /home/pi/chrono-shift/cron-execute.log 2>&1
```
:warning: `run.sh` updates python path, assuming `/home/pi/blinky/` is clone of [blinky](https://github.com/pdumoulin/blinky) repo

### Add Tasks
1. Subclass `BaseTask` in `tasks.__init__.py`
2. Add instance of new task in `config.SCHEDULE`

## CLI Interface
```
usage: run.py [-h] {set,list,clear,execute} ...

positional arguments:
  {set,list,clear,execute}
    set                 reset and schedule tasks for next 24hrs based on config.TASKS
    list                view currently set task schedule
    clear               delete all scheduled tasks
    execute             run all pending tasks in recent time window of 60s

optional arguments:
  -h, --help            show this help message and exit
  ```
