FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    nginx \
    gettext-base \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy Nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Make start script executable
COPY start.sh .
RUN chmod +x start.sh

# Expose port for Heroku
EXPOSE $PORT

# Run the start script
CMD ["./start.sh"] 