#!/bin/bash
set -e

# Display environment variables for debugging (excluding sensitive ones)
echo "PORT: $PORT"
echo "Available Python modules:"
pip list | grep -E "streamlit|fastapi|uvicorn"

# Run startup script if it exists
if [ -f "startup.py" ]; then
    echo "Running startup script..."
    python startup.py &
fi

# Start FastAPI 
echo "Starting FastAPI on port 8000..."
uvicorn api.app:app --host 127.0.0.1 --port 8000 &
FASTAPI_PID=$!
echo "FastAPI started with PID: $FASTAPI_PID"

# Check for the existence of the Streamlit entry point
if [ -f "main.py" ]; then
    # Start Streamlit
    echo "Starting Streamlit on port 8501..."
    streamlit run main.py --server.port 8501 --server.headless true --server.enableCORS false --server.address 127.0.0.1 &
    STREAMLIT_PID=$!
    echo "Streamlit started with PID: $STREAMLIT_PID"
else
    echo "WARNING: Could not find main.py for Streamlit"
    echo "Looking for potential Streamlit entry points:"
    find . -name "*.py" | grep -v "__pycache__" | head -10
fi

# Replace $PORT in nginx.conf with the port provided by Heroku
echo "Configuring and starting Nginx..."
envsubst '$PORT' < /etc/nginx/nginx.conf > /etc/nginx/nginx.conf.tmp
mv /etc/nginx/nginx.conf.tmp /etc/nginx/nginx.conf

# Start Nginx in the foreground
echo "Starting Nginx..."
nginx -g 'daemon off;' 