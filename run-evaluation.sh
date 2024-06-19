#!/bin/bash
# Runs the evaluation.
#
# Environment variables:
# - PRINT_UPTIME_INTERVAL: If set to a positive number, prints uptime every
#   PRINT_UPTIME_INTERVAL seconds.
# - NUM_DOIT_TASKS: Number of parallel tasks to run. Defaults to the number of
#   processors on the machine.

set -eo pipefail

PRINT_UPTIME_INTERVAL="${PRINT_UPTIME_INTERVAL:-0}"
NUM_DOIT_TASKS="${NUM_DOIT_TASKS:-$(nproc)}"

# Optionally track uptime. Set PRINT_UPTIME_INTERVAL to a positive number to
# enable.
if [[ -n "$PRINT_UPTIME_INTERVAL" ]] && [[ $PRINT_UPTIME_INTERVAL -gt 0 ]]; then
  # Trap to kill uptime process on exit.
  trap 'kill $(jobs -p)' EXIT
  # Uptime process.
  while true; do uptime; sleep $PRINT_UPTIME_INTERVAL; done &
fi

echo "Running tasks with ${NUM_DOIT_TASKS} parallel jobs."
doit --continue -n $NUM_DOIT_TASKS
