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

# Ensure start script is executable
RUN chmod +x start.sh

# Start the application using our robust durable script
CMD ["./start.sh"]
