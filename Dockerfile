FROM python:3.12-slim

# Install system dependencies required for WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    mime-support \
    nginx \
    gettext-base \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
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