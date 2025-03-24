#!/bin/bash

# Function to handle cleanup on exit
cleanup() {
  echo "Shutting down servers..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
  exit 0
}

# Set up trap to catch Ctrl+C and other termination signals
trap cleanup SIGINT SIGTERM

# Start the backend server
echo "Starting backend server..."
cd "$(dirname "$0")/web"
python run_server.py &
BACKEND_PID=$!
echo "Backend server started with PID: $BACKEND_PID"

# Start the frontend server
echo "Starting frontend server..."
cd "$(dirname "$0")/web/frontend"
bash start_frontend.sh &
FRONTEND_PID=$!
echo "Frontend server started with PID: $FRONTEND_PID"

echo "Both servers are running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID