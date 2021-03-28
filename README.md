# chrono-shift
Daily python task scheduler for localized timezones and dynamic events.


## Setup

### Packages
* python >= 3.6 required
* install python packages in `requirements.txt`

### Initialize
Assuming repo is cloned into `/home/pi/chrono-shift/`
```
/home/pi/chrono-shift/run.sh set
```

### Crontab
Assuming repo is cloned into `/home/pi/chrono-shift/`
```
# run executor every minute (will automatically build schedule every config.RESET_INTERVAL seconds)
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
    execute             run all pending tasks in recent time window of config.WINDOW seconds AND reset every config.RESET_INTERVAL seconds

optional arguments:
  -h, --help            show this help message and exit
  ```
