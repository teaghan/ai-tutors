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

# Create a guaranteed API to satisfy Nginx
mkdir -p api
echo "Creating robust API endpoint..."
cat > api/app.py << 'EOF'
from fastapi import FastAPI, HTTPException, Request
import os
import time

# Create a very simple FastAPI application
app = FastAPI(title="AI Tutors API", debug=True)

@app.get("/")
async def root(request: Request):
    client_host = request.client.host if request.client else "unknown"
    return {
        "message": "API is running", 
        "status": "OK", 
        "time": time.time(),
        "client": client_host,
        "headers": dict(request.headers)
    }

@app.get("/init_request")
async def init_request(access_code: str = None, request: Request = None):
    client_host = request.client.host if request.client else "unknown"
    if not access_code:
        raise HTTPException(status_code=400, detail="Missing access code")
    return {
        "init_request": f"Hello! I'm your AI Tutor. How can I help you today? (Debug: received access code: {access_code}, from: {client_host})",
        "version": "fallback-v1",
        "client": client_host
    }

@app.post("/query")
async def query(request_data: dict, request: Request = None):
    client_host = request.client.host if request.client else "unknown"
    user_prompt = request_data.get("user_prompt", "No prompt provided")
    return {
        "response": f"This is a placeholder response. The FastAPI server is running correctly, but the main AI functionality isn't available. You asked: '{user_prompt}'",
        "message_history": request_data.get("message_history", []) + [
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": f"This is a placeholder response. The FastAPI server is running correctly, but the main AI functionality isn't available. Client: {client_host}"}
        ],
        "debug_info": {
            "client": client_host,
            "time": time.time()
        }
    }
EOF

echo "API file created with full debugging endpoints"

# Start FastAPI with debugging output - CRITICAL: bind to 0.0.0.0 instead of 127.0.0.1
echo "Starting FastAPI on port 8000 (0.0.0.0)..."
PYTHONPATH=. uvicorn api.app:app --host 0.0.0.0 --port 8000 --log-level debug &
FASTAPI_PID=$!
echo "FastAPI started with PID: $FASTAPI_PID"

# Check for the existence of the Streamlit entry point
if [ -f "main.py" ]; then
    # Start Streamlit
    echo "Starting Streamlit on port 8501..."
    # Also bind Streamlit to 0.0.0.0 for better container networking
    streamlit run main.py --server.port 8501 --server.headless true --server.enableCORS false --server.address 0.0.0.0 &
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

# Wait for API to be ready and test explicitly
echo "Waiting for API to start..."
sleep 5
ATTEMPTS=0
while ! curl -s http://localhost:8000/ > /dev/null; do
    ATTEMPTS=$((ATTEMPTS+1))
    if [ $ATTEMPTS -gt 3 ]; then
        echo "WARNING: API did not respond after 3 attempts, trying direct call to 0.0.0.0..."
        curl -v http://0.0.0.0:8000/ || echo "Direct call failed"
        break
    fi
    echo "Waiting for API to respond (attempt $ATTEMPTS)..."
    sleep 2
done

# Test various ways to access the API to debug networking
echo "Testing API in different ways:"
echo "1. Via localhost:"
curl -v http://localhost:8000/ || echo "localhost access failed"
echo "2. Via 0.0.0.0:"
curl -v http://0.0.0.0:8000/ || echo "0.0.0.0 access failed"
echo "3. Via 127.0.0.1:"
curl -v http://127.0.0.1:8000/ || echo "127.0.0.1 access failed"

# View process status to confirm services are running
echo "Process status:"
ps aux | grep -E "uvicorn|streamlit"

# Start Nginx in the foreground
echo "Starting Nginx..."
nginx -g 'daemon off;' 