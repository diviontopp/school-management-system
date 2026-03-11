FROM python:3.11-slim

WORKDIR /code

# Install system dependencies for MySQL
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

# Sequential startup: Init DB then run Gunicorn on Railway's dynamic $PORT
# Added explicit access/error logging and proxy trust flags
CMD python init_db.py && gunicorn app:app \
    --bind 0.0.0.0:$PORT \
    --worker-class gthread \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --forwarded-allow-ips "*" \
    --log-level debug
