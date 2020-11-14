#!/bin/bash

# crontab setup
# 0 0 * * * /home/pi/chrono-shift/run.sh set > /home/pi/chrono-shift/cron-set.logs 2>&1
# * * * * * /home/pi/chrono-shift/run.sh execute> /home/pi/chrono-shift/cron-execute.logs 2>&1

export PYTHONPATH=$PYTHONPATH:/home/pi/blinky
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
python3 $DIR/run.py $@

