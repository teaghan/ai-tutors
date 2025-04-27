FROM python:3.12-slim

# Install system dependencies for WeasyPrint
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      python3-pip \
      python3-cffi \
      libcairo2 \
      libpango-1.0-0 \
      libpangoft2-1.0-0 \
      libharfbuzz0b \
      libharfbuzz-subset0 \
      libgdk-pixbuf2.0-0 \
      libffi-dev \
      libjpeg-dev \
      libopenjp2-7-dev \
      shared-mime-info \
      mime-support \
      nginx \
      gettext-base && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf.template

# Create startup script
RUN echo '#!/bin/bash\n\
envsubst "\$PORT" < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf\n\
python -m api.app & \n\
streamlit run main.py --server.port 8501 --server.headless true & \n\
echo "Starting Nginx..."\n\
nginx -g "daemon off;"\n\
' > start.sh && chmod +x start.sh

# Expose port
EXPOSE $PORT

# Run the application
CMD ["./start.sh"] 