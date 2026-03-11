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

ENV PYTHONUNBUFFERED=1

# Expose the port (Railway typically uses PORT env var)
EXPOSE 8080

# Run initialization script then start gunicorn
CMD python init_db.py && gunicorn -b 0.0.0.0:${PORT:-8080} --timeout 120 --workers 2 --access-logfile - --error-logfile - --forwarded-allow-ips "*" "app:app"
