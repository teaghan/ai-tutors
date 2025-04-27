#!/bin/bash
set -e

# Configure Nginx
echo "Configuring Nginx..."
envsubst '$PORT' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Start FastAPI server
echo "Starting FastAPI server..."
PYTHONPATH=. uvicorn api.app:app --host 0.0.0.0 --port 8000 &

# Start Streamlit
echo "Starting Streamlit on port 8501..."
streamlit run main.py --server.port 8501 --server.headless true --server.enableCORS false --server.address 0.0.0.0 &

# Sleep a moment to let services start
sleep 3

# Start Nginx in foreground
echo "Starting Nginx..."
exec nginx -g 'daemon off;' 