#!/bin/bash

set -e

PATH="/home/appuser/.local/bin/:$PATH"

echo 'Running ruff/isort'
ruff check --select I --fix .

echo 'Running ruff'
ruff format src/ entrypoint.py
