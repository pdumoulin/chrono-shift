#!/bin/bash

# crontab setup
# * * * * * /home/pi/chrono-shift/run.sh execute >> /home/pi/chrono-shift/cron-execute.log 2>&1

export PYTHONPATH=$PYTHONPATH:/home/pi/blinky
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
python3 $DIR/run.py $@

