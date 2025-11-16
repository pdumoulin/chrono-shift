#!/bin/bash

set -eu

docker compose exec script pgrep -x python > /dev/null 2>&1
