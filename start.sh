#!/bin/bash
set -e

# Display environment variables for debugging (excluding sensitive ones)
echo "PORT: $PORT"
echo "Available Python modules:"
pip list | grep -E "streamlit|fastapi|uvicorn"

# List files to debug issues
echo "Directory contents:"
ls -la
echo "API files:"
find . -name "app.py" | grep -v "__pycache__"

# Run startup script if it exists
if [ -f "startup.py" ]; then
    echo "Running startup script..."
    python startup.py &
fi

# Always create a simple API endpoint for debugging
echo "Creating guaranteed API for debugging..."
mkdir -p api
cat > api/app.py << 'EOF'
from fastapi import FastAPI, HTTPException
import os

app = FastAPI(title="AI Tutors API")

@app.get("/")
async def root():
    return {"message": "API is running", "status": "OK"}

@app.get("/init_request")
async def init_request(access_code: str = None):
    if not access_code:
        raise HTTPException(status_code=400, detail="Missing access code")
    return {
        "init_request": f"Debug message - received access code: {access_code}",
        "version": "debug-fallback"
    }

@app.post("/query")
async def query(request_data: dict):
    return {
        "response": "This is a placeholder response for debugging. The API server is running but not fully configured.",
        "message_history": request_data.get("message_history", []) + [
            {"role": "user", "content": request_data.get("user_prompt", "")},
            {"role": "assistant", "content": "This is a placeholder response for debugging. The API server is running but not fully configured."}
        ]
    }
EOF

echo "API file created with basic endpoints"
cat api/app.py

# Start FastAPI with debugging output
echo "Starting FastAPI on port 8000..."
PYTHONPATH=. uvicorn api.app:app --host 127.0.0.1 --port 8000 --log-level debug &
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

# Wait for API to be ready
echo "Waiting for API to start..."
sleep 5
ATTEMPTS=0
while ! curl -s http://127.0.0.1:8000/ > /dev/null; do
    ATTEMPTS=$((ATTEMPTS+1))
    if [ $ATTEMPTS -gt 5 ]; then
        echo "WARNING: API did not respond after 5 attempts"
        # Restart the API as a last resort
        echo "Attempting to restart the API..."
        kill -9 $FASTAPI_PID || true
        PYTHONPATH=. uvicorn api.app:app --host 127.0.0.1 --port 8000 --log-level debug &
        FASTAPI_PID=$!
        echo "FastAPI restarted with PID: $FASTAPI_PID"
        sleep 5
        break
    fi
    echo "Waiting for API to respond..."
    sleep 2
done

# Try a test request to the API to verify it's working
curl -s http://127.0.0.1:8000/ || echo "ERROR: API is not responding to test request"

# Start Nginx in the foreground
echo "Starting Nginx..."
nginx -g 'daemon off;' 