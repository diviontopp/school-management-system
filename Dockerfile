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

# Set up user permissions for Hugging Face Spaces (UID 1000)
RUN chmod -R 777 /code
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

WORKDIR /code

# Hugging Face Spaces route traffic to port 7860
EXPOSE 7860

# 1 worker prevents OOM kills in HF's constrained environment
# 120s timeout prevents gunicorn from killing long-running DB init
CMD ["gunicorn", "-b", "0.0.0.0:7860", "--timeout", "120", "--workers", "1", "--access-logfile", "-", "--error-logfile", "-", "--forwarded-allow-ips", "*", "app:app"]
