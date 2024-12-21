#!/bin/bash

set -e

mkdir -p logs

docker compose down script

docker compose up --build -d script
