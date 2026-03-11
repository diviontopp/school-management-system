#!/bin/bash
# Durable startup script for Railway
echo ">>> STARTUP: Initiating environment check..."
echo ">>> PORT assigned: $PORT"

# Run database initialization
echo ">>> STARTUP: Running init_db.py..."
python init_db.py

if [ $? -ne 0 ]; then
    echo ">>> ERROR: Database initialization failed!"
    exit 1
fi

echo ">>> STARTUP: Starting Gunicorn on port $PORT..."
# Using gthread for better concurrency
# wsgi:app points to our wsgi.py entry point
exec gunicorn \
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
