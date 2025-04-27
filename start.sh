#!/bin/bash
set -e

# Setup trap to kill background processes on exit
trap 'kill $(jobs -p) 2>/dev/null' EXIT

# Display environment variables for debugging
echo "PORT: ${PORT:-8080}"

# Run startup script if it exists
if [ -f "startup.py" ]; then
    echo "Running startup script..."
    python startup.py &
fi

# More robust port check that works without netcat
check_port() {
    (echo > /dev/tcp/127.0.0.1/$1) >/dev/null 2>&1
    return $?
}

# Start FastAPI server
echo "Starting FastAPI server..."
if check_port 8000; then
    echo "WARNING: Port 8000 already in use, skipping API server start"
else
    PYTHONPATH=. uvicorn api.app:app --host 127.0.0.1 --port 8000 --log-level info &
    FASTAPI_PID=$!
    echo "FastAPI started with PID: $FASTAPI_PID"
fi

# Start Streamlit
if [ -f "main.py" ]; then
    echo "Starting Streamlit on port 8501..."
    streamlit run main.py --server.port 8501 --server.headless true --server.enableCORS false --server.address 127.0.0.1 &
    STREAMLIT_PID=$!
    echo "Streamlit started with PID: $STREAMLIT_PID"
else
    echo "ERROR: Could not find main.py for Streamlit"
    exit 1
fi

# Configure Nginx
echo "Configuring Nginx..."
envsubst '$PORT' < /etc/nginx/nginx.conf > /etc/nginx/nginx.conf.tmp
mv /etc/nginx/nginx.conf.tmp /etc/nginx/nginx.conf

# Wait for API to be ready with shorter intervals
echo "Waiting for API to start..."
MAX_ATTEMPTS=10
ATTEMPTS=0
while ! curl -s http://127.0.0.1:8000/ > /dev/null && [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
    ATTEMPTS=$((ATTEMPTS+1))
    echo "Waiting for API to respond... (Attempt $ATTEMPTS/$MAX_ATTEMPTS)"
    sleep 1
done

if [ $ATTEMPTS -ge $MAX_ATTEMPTS ]; then
    echo "WARNING: API did not respond after $MAX_ATTEMPTS attempts"
    if [ -n "$FASTAPI_PID" ]; then
        echo "Attempting to restart the API..."
        kill -9 $FASTAPI_PID 2>/dev/null || true
        PYTHONPATH=. uvicorn api.app:app --host 127.0.0.1 --port 8000 --log-level info &
        FASTAPI_PID=$!
        echo "FastAPI restarted with PID: $FASTAPI_PID"
        sleep 3
    fi
fi

# Verify API is working
if curl -s http://127.0.0.1:8000/ > /dev/null; then
    echo "API is responding correctly"
else 
    echo "ERROR: API is not responding to test request"
fi

# Start Nginx in the foreground
echo "Starting Nginx..."
exec nginx -g 'daemon off;' 