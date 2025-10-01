#!/bin/bash

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 {install|uninstall} <script_name.py>"
    exit 1
fi

ACTION="$1"
PYTHON_SCRIPT_NAME="$2"

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
PYTHON_SCRIPT_PATH="$SCRIPT_DIR/$PYTHON_SCRIPT_NAME"

if [[ ! -f "$PYTHON_SCRIPT_PATH" ]]; then
    echo "Error: Script not found at $PYTHON_SCRIPT_PATH"
    exit 1
fi

BASENAME=$(basename "$PYTHON_SCRIPT_NAME" .py)
LOCK_FILE="/tmp/${BASENAME}.lock"
LOG_FILE="$SCRIPT_DIR/logs/cron/${BASENAME}.log"
CRON_COMMENT="# Cron job for $PYTHON_SCRIPT_NAME"

UV_PATH=$(which uv)
if [[ -z "$UV_PATH" ]]; then
    echo "Error: 'uv' executable not found in PATH."
    exit 1
fi

CRON_JOB="*/30 * * * * /usr/bin/flock -n \"$LOCK_FILE\" bash -c 'cd \"$SCRIPT_DIR\" && \"$UV_PATH\" run \"$PYTHON_SCRIPT_NAME\"' >> \"$LOG_FILE\" 2>&1 $CRON_COMMENT"


install_cron() {
    echo "Installing cron job for $PYTHON_SCRIPT_NAME..."
    mkdir -p "$(dirname "$LOG_FILE")"
    
    local cmd_array=(
        bash 
        -c 
        "cd \"$SCRIPT_DIR\" && \"$UV_PATH\" run \"$PYTHON_SCRIPT_NAME\""
    )

    (crontab -l 2>/dev/null | grep -vF "$CRON_COMMENT"; echo "$CRON_JOB") | crontab -
    
    echo "Cron job installed successfully."
    echo "---"
    
    echo "Triggering immediate first run in the background..."
    nohup /usr/bin/flock -n "$LOCK_FILE" "${cmd_array[@]}" >> "$LOG_FILE" 2>&1 &
    
    echo "Job started. Use './status.sh $PYTHON_SCRIPT_NAME' to monitor."
}

uninstall_cron() {
    echo "Uninstalling cron job for $PYTHON_SCRIPT_NAME..."
    (crontab -l 2>/dev/null | grep -vF "$CRON_COMMENT") | crontab -
    echo "Cron job uninstalled."
}


if [[ "$ACTION" == "install" ]]; then
    install_cron
elif [[ "$ACTION" == "uninstall" ]]; then
    uninstall_cron
else
    echo "Error: Invalid action '$ACTION'. Use 'install' or 'uninstall'."
    echo "Usage: $0 {install|uninstall} <your_script_name.py>"
    exit 1
fi