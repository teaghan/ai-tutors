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

# Kill any process using port 8000 if needed
if check_port 8000; then
    echo "Port 8000 is in use, attempting to free it..."
    if command -v lsof >/dev/null 2>&1; then
        lsof -i :8000 -t | xargs kill -9 2>/dev/null || true
    fi
    sleep 1
fi

# Start FastAPI server with proper debugging
echo "Starting FastAPI server..."
PYTHONPATH=. uvicorn api.app:app --host 0.0.0.0 --port 8000 --log-level info &
FASTAPI_PID=$!
echo "FastAPI started with PID: $FASTAPI_PID"

# Start Streamlit
if [ -f "main.py" ]; then
    echo "Starting Streamlit on port 8501..."
    streamlit run main.py --server.port 8501 --server.headless true --server.enableCORS false --server.address 0.0.0.0 &
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

# Wait for API to be ready with shorter intervals and longer timeout
echo "Waiting for API to start..."
MAX_ATTEMPTS=30  # More attempts, 30 seconds total
ATTEMPTS=0
API_STARTED=false

while [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
    if curl -s http://localhost:8000/ > /dev/null; then
        echo "✓ API is responding correctly"
        API_STARTED=true
        break
    fi
    ATTEMPTS=$((ATTEMPTS+1))
    echo "Waiting for API to respond... (Attempt $ATTEMPTS/$MAX_ATTEMPTS)"
    sleep 1
done

if [ "$API_STARTED" != "true" ]; then
    echo "WARNING: API did not respond after $MAX_ATTEMPTS attempts"
    echo "Logging API process details for debugging:"
    ps -ef | grep uvicorn || true
    echo "API log snippet:"
    tail -n 20 /var/log/nginx/error.log 2>/dev/null || true
    
    echo "Attempting to restart the API with more verbosity..."
    kill -9 $FASTAPI_PID 2>/dev/null || true
    PYTHONPATH=. uvicorn api.app:app --host 0.0.0.0 --port 8000 --log-level debug &
    FASTAPI_PID=$!
    echo "FastAPI restarted with PID: $FASTAPI_PID"
    sleep 5
    
    # Final check
    if curl -s http://localhost:8000/ > /dev/null; then
        echo "✓ API is now responding after restart"
    else
        echo "⚠ API is still not responding. Starting in fallback mode with basic API..."
        kill -9 $FASTAPI_PID 2>/dev/null || true
        cat > fallback_api.py << 'EOF'
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="AI Tutors API (Fallback)")

@app.get("/")
async def root():
    return {"status": "ok", "mode": "fallback"}

@app.get("/init_request")
async def init_request(access_code: str = None):
    return {"init_request": "API is running in fallback mode. Please try again later."}

@app.post("/query")
async def query(request_data: dict):
    return {"response": "API is running in fallback mode. Please try again later."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
        PYTHONPATH=. uvicorn fallback_api:app --host 0.0.0.0 --port 8000 &
        FASTAPI_PID=$!
        echo "Fallback API started with PID: $FASTAPI_PID"
        sleep 3
    fi
fi

# Final check before starting Nginx
curl -s http://localhost:8000/ || echo "⚠ API might not be working correctly"

# Start Nginx in the foreground
echo "Starting Nginx..."
exec nginx -g 'daemon off;' 