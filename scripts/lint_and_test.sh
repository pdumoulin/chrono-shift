#!/bin/bash

set -e

PATH="/home/appuser/.local/bin/:$PATH"

echo 'Running yamllint'
yamllint docker-compose.yaml

echo 'Running ruff'
ruff check src/ entrypoint.py --no-cache --select I,F,E,W,B
ruff format src/ entrypoint.py --diff --no-cache

echo 'Running mypy'
mypy --disallow-untyped-defs --cache-dir=/dev/null src
