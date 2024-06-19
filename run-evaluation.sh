#!/bin/bash
# Runs the evaluation.

set -eo pipefail

PRINT_UPTIME_INTERVAL="${PRINT_UPTIME_INTERVAL:-0}"

if [[ -z "$NUM_DOIT_TASKS" ]]; then
    echo "Must provide NUM_DOIT_TASKS in environment" 1>&2
    exit 1
fi

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
