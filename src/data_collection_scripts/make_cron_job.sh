#!/bin/bash

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 {install|uninstall|run} <script_name.py>"
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
    
    local CMD_ARRAY=(
        bash 
        -c 
        "cd \"$SCRIPT_DIR\" && \"$UV_PATH\" run \"$PYTHON_SCRIPT_NAME\""
    )

    (crontab -l 2>/dev/null | grep -vF "$CRON_COMMENT"; echo "$CRON_JOB") | crontab -
    
    echo "Cron job installed successfully."
    echo "---"
    
    echo "Triggering immediate first run in the background..."
    nohup /usr/bin/flock -n "$LOCK_FILE" "${CMD_ARRAY[@]}" >> "$LOG_FILE" 2>&1 &
    
    echo "Job started. Use './status.sh $PYTHON_SCRIPT_NAME' to monitor."
}

uninstall_cron() {
    echo "Uninstalling cron job for $PYTHON_SCRIPT_NAME..."
    (crontab -l 2>/dev/null | grep -vF "$CRON_COMMENT") | crontab -
    echo "Cron job uninstalled."
}

run_script() {
    echo "Running script $PYTHON_SCRIPT_NAME immediately..."
    mkdir -p "$(dirname "$LOG_FILE")"
    
    local CMD_ARRAY=(
        bash 
        -c 
        "cd \"$SCRIPT_DIR\" && \"$UV_PATH\" run \"$PYTHON_SCRIPT_NAME\""
    )


    echo "--- Start Run: $(date) ---" >> "$LOG_FILE"

    "${CMD_ARRAY[@]}" | tee -a "$LOG_FILE"
    
    EXIT_CODE=$?
    echo "--- End Run: (Exit Code: $EXIT_CODE): $(date) ---" >> "$LOG_FILE"

    if [[ $EXIT_CODE -eq 0 ]]; then
        echo "Script completed successfully."
    else
        echo "Script execution failed with exit code $EXIT_CODE."
    fi

    return $EXIT_CODE
}

if [[ "$ACTION" == "install" ]]; then
    install_cron
elif [[ "$ACTION" == "uninstall" ]]; then
    uninstall_cron
elif [[ "$ACTION" == "run" ]]; then
    run_script
else
    echo "Error: Invalid action '$ACTION'. Use 'install' or 'uninstall' or 'run'."
    echo "Usage: $0 {install|uninstall|run} <script_name.py>"
    exit 1
fi