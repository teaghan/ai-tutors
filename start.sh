#!/bin/bash
set -e

# Configure Nginx
echo "Configuring Nginx..."
envsubst '$PORT' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Start FastAPI server
echo "Starting FastAPI server..."
PYTHONPATH=. uvicorn api.app:app --host 0.0.0.0 --port 8000 &

# Start Streamlit with original Procfile settings
echo "Starting Streamlit..."
streamlit run main.py --server.port 8501 --server.headless true --server.enableCORS false --server.address 0.0.0.0 &

# Run startup.py as in original Procfile
echo "Running startup.py..."
python startup.py &

# Sleep a moment to let services start
sleep 3

# Start Nginx in foreground
echo "Starting Nginx..."
exec nginx -g 'daemon off;' 