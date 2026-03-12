FROM python:3.11-slim

WORKDIR /code

# Install system dependencies for MySQL
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/requirements.txt
WORKDIR /code
COPY . .

# Expose 8080 as a hint for Railway, though start.sh binds to $PORT
EXPOSE 8080

# Start the application: Init DB then run Gunicorn on dynamic $PORT
# Using gthread for concurrent health checks and wsgi:app for clean entry
CMD python init_db.py && gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --worker-class gthread \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --forwarded-allow-ips "*" \
    --log-level debug \
    wsgi:app
