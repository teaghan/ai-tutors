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

# Check if api directory exists
if [ -d "api" ]; then
    echo "api directory exists"
    ls -la api/
else
    echo "ERROR: api directory not found"
    # Try to find where the FastAPI code might be
    echo "Looking for app.py files:"
    find . -name "app.py" | grep -v "__pycache__"
fi

# Check if api/app.py exists
if [ -f "api/app.py" ]; then
    # Start FastAPI with debugging output
    echo "Starting FastAPI on port 8000..."
    PYTHONPATH=. uvicorn api.app:app --host 127.0.0.1 --port 8000 --log-level debug &
    FASTAPI_PID=$!
    echo "FastAPI started with PID: $FASTAPI_PID"
elif [ -f "ai_tutors/app.py" ]; then
    echo "Using alternate FastAPI path: ai_tutors/app.py"
    PYTHONPATH=. uvicorn ai_tutors.app:app --host 127.0.0.1 --port 8000 --log-level debug &
    FASTAPI_PID=$!
    echo "FastAPI started with PID: $FASTAPI_PID"
else
    echo "ERROR: FastAPI app.py not found in expected locations!"
    echo "Creating placeholder API for debugging..."
    # Create a very simple FastAPI app for debugging
    mkdir -p api
    cat > api/app.py << 'EOF'
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.get("/init_request")
async def init_request(access_code: str):
    return {"init_request": f"Debug message - received access code: {access_code}"}

@app.post("/query")
async def query(request_data: dict):
    return {
        "response": "This is a placeholder response for debugging",
        "message_history": request_data.get("message_history", []) + [
            {"role": "user", "content": request_data.get("user_prompt", "")},
            {"role": "assistant", "content": "This is a placeholder response for debugging"}
        ]
    }
EOF
    echo "Created placeholder API"
    PYTHONPATH=. uvicorn api.app:app --host 127.0.0.1 --port 8000 --log-level debug &
    FASTAPI_PID=$!
    echo "FastAPI placeholder started with PID: $FASTAPI_PID"
fi

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
        break
    fi
    echo "Waiting for API to respond..."
    sleep 2
done

# Start Nginx in the foreground
echo "Starting Nginx..."
nginx -g 'daemon off;' 