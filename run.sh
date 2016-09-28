#!/bin/bash

# crontab setup
# 0,15,30,45 * * * * /home/pi/game-time/run.sh > /home/pi/game-time/logs/cron.log 2>&1

export PYTHONPATH=$PYTHONPATH:/home/pi/blinky
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

python $DIR/game_time.py $@

