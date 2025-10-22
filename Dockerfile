# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Expose default Zenoh port
EXPOSE 7447

# Set environment variables
ENV PYTHONPATH=/app

# Default command
CMD ["python", "examples/basic_usage.py"]