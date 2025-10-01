#!/bin/bash

if [[ -z "$1" ]]; then
    echo "Usage: $0 <your_script_name.py>"
    exit 1
fi

PYTHON_SCRIPT_NAME="$1"

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

BASENAME=$(basename "$PYTHON_SCRIPT_NAME" .py)
LOCK_FILE="/tmp/${BASENAME}.lock"
LOG_FILE="$SCRIPT_DIR/logs/cron/${BASENAME}.log"

echo "--- Status for $PYTHON_SCRIPT_NAME ---"

if [ -f "$LOCK_FILE" ]; then
    echo -e "STATUS: RUNNING"

    PID=$(pgrep -f "uv run $PYTHON_SCRIPT_NAME")

    if [ -n "$PID" ]; then
        UPTIME=$(ps -p "$PID" -o etime= | tr -d ' ')
        echo "Uptime: $UPTIME"
    else
        echo "Uptime: Lock file found, but process is not running. It may have crashed."
    fi

    echo ""
    echo "--- Last 30 Log Entries ---"
    if [ -f "$LOG_FILE" ]; then
        tail -n 30 "$LOG_FILE"
    else
        echo "Log file not found."
    fi

else
    echo -e "\e[31mSTATUS: NOT RUNNING\e[0m" 
    echo "The script may have completed or is waiting for the next scheduled run."
    echo ""
    echo "--- Last 5 Log Entries from Previous Run ---"
    if [ -f "$LOG_FILE" ]; then
        tail -n 5 "$LOG_FILE"
    else
        echo "Log file not found."
    fi
fi

echo "---------------------------------"