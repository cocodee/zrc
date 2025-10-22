#!/bin/bash

# Test script for ZRC in Docker environment

set -e  # Exit on any error

echo "Building Docker images..."
docker compose build

echo "Starting Zenoh router..."
docker  compose up -d zenoh-router

# Wait for router to be ready
echo "Waiting for Zenoh router to start..."
sleep 5

echo "Running import tests..."
docker compose run --rm zrc-client python tests/test_import.py

echo "Running example usage..."
docker compose run --rm zrc-client python examples/basic_usage.py

echo "Stopping all services..."
docker- ompose down

echo "Docker tests completed successfully!"