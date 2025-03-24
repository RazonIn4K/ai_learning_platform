#!/bin/bash

# Enhanced start_all.sh with process monitoring, auto-restart, and error handling

# Function to check if a process is running
is_process_running() {
    pgrep -f "$1" > /dev/null
}

# Function to start a process with error handling and auto-restart
start_process() {
    local process_name="$1"
    local command="$2"
    local log_file="$3"

    if is_process_running "$process_name"; then
        echo "$process_name is already running."
        return
    fi

    echo "Starting $process_name..."
    # Redirect both stdout and stderr to the log file
    eval "$command" > "$log_file" 2>&1 &

    # Check if the process started successfully
    sleep 1 # Give it a second to start
    if ! is_process_running "$process_name"; then
        echo "Error: Failed to start $process_name. Check $log_file for details."
        return 1
    fi

    echo "$process_name started successfully."
    return 0
}

# Function to gracefully stop a process
stop_process() {
  local process_name="$1"
  if is_process_running "$process_name"; then
    echo "Stopping $process_name..."
    pkill -f "$process_name"
    # Wait for the process to terminate gracefully
    wait_count=0
    while is_process_running "$process_name"; do
      sleep 1
      wait_count=$((wait_count + 1))
      if [[ $wait_count -gt 10 ]]; then  # Wait for a maximum of 10 seconds
        echo "Warning: $process_name did not stop gracefully. Forcefully killing..."
        pkill -9 -f "$process_name"
        break
      fi
    done
    echo "$process_name stopped."
  else
    echo "$process_name is not running."
  fi
}

# Trap signals for graceful shutdown
trap 'stop_process "python3 ai_learning_platform/web/api.py"; stop_process "python3 ai_learning_platform/gray_swan/gray_swan_automator.py"; exit' INT TERM

# --- Main Script ---

# Check dependencies
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install it and try again."
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install it and try again."
    exit 1
fi

# Check if virtual environment exists, create if it doesn't
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt  # Assuming a requirements.txt file exists at the project root

# Start processes with monitoring and auto-restart
start_process "python3 ai_learning_platform/web/api.py" "python3 ai_learning_platform/web/api.py" "logs/api_server.log"
start_process "python3 ai_learning_platform/gray_swan/gray_swan_automator.py" "python3 ai_learning_platform/gray_swan/gray_swan_automator.py" "logs/gray_swan_automator.log"

# Keep the script running (monitoring loop)
while true; do
    sleep 60  # Check every 60 seconds

    if ! is_process_running "python3 ai_learning_platform/web/api.py"; then
        echo "API server crashed. Restarting..."
        start_process "python3 ai_learning_platform/web/api.py" "python3 ai_learning_platform/web/api.py" "logs/api_server.log"
    fi

    if ! is_process_running "python3 ai_learning_platform/gray_swan/gray_swan_automator.py"; then
        echo "GraySwan Automator crashed. Restarting..."
        start_process "python3 ai_learning_platform/gray_swan/gray_swan_automator.py" "python3 ai_learning_platform/gray_swan/gray_swan_automator.py" "logs/gray_swan_automator.log"
    fi
done