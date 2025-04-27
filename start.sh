#!/bin/bash
set -e

# Run startup script if it exists
if [ -f "startup.py" ]; then
    echo "Running startup script..."
    python startup.py &
fi

# Start FastAPI 
echo "Starting FastAPI on port 8000..."
uvicorn api.app:app --host 127.0.0.1 --port 8000 &

# Start Streamlit
echo "Starting Streamlit on port 8501..."
streamlit run main.py --server.port 8501 --server.headless true --server.enableCORS false --server.address 127.0.0.1 &

# Replace $PORT in nginx.conf with the port provided by Heroku
echo "Configuring and starting Nginx..."
envsubst '$PORT' < /etc/nginx/nginx.conf > /etc/nginx/nginx.conf.tmp
mv /etc/nginx/nginx.conf.tmp /etc/nginx/nginx.conf
cat /etc/nginx/nginx.conf

# Start Nginx
nginx -g 'daemon off;' 