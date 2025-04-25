# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy project files into the container
COPY . .

# Install dependencies
RUN apt-get update && apt-get install -y docker.io
RUN apt-get update && apt-get install -y curl
RUN curl -L "https://github.com/docker/compose/releases/download/v2.24.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
RUN chmod +x /usr/local/bin/docker-compose

RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 9999

# Start the webhook listener
# CMD ["python", "webhook_listener.py"]
CMD ["gunicorn", "-b", "0.0.0.0:9999", "webhook_listener:app"]
