#!/bin/bash

set -eu

# service is running
docker compose exec script pgrep -x python

# no errors are in logs
ERROR_COUNT=$(cat logs/app.log | grep ERROR | wc -l)
if [[ $ERROR_COUNT -gt 0 ]]; then
    exit 2
fi
