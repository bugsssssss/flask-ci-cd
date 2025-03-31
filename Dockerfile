# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /backend

# Copy project files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 9999

# Start the webhook listener
# CMD ["python", "webhook_listener.py"]
CMD ["gunicorn", "-b", "0.0.0.0:9999", "webhook_listener:app"]
