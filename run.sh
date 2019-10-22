#!/bin/bash

# crontab setup
# */5 * * * * /home/pi/game-time/run.sh > /home/pi/game-time/cron.log 2>&1

export PYTHONPATH=$PYTHONPATH:/home/pi/blinky
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
python3 $DIR/game_time.py $@

