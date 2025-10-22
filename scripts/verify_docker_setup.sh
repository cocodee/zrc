#!/bin/bash

# Verification script for Docker environment setup

set -e  # Exit on any error

echo "=== ZRC Docker Environment Verification ==="

echo "1. Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed or not in PATH"
    exit 1
fi
echo "✓ Docker is installed"

if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: Docker Compose is not installed or not in PATH"
    exit 1
fi
echo "✓ Docker Compose is installed"

echo "2. Building Docker images..."
docker-compose build > /dev/null 2>&1
echo "✓ Docker images built successfully"

echo "3. Starting Zenoh router..."
docker-compose up -d zenoh-router > /dev/null 2>&1

# Wait for router to be ready
sleep 5

echo "4. Verifying Zenoh router is running..."
if ! docker-compose ps | grep zenoh-router | grep "Up" &> /dev/null; then
    echo "ERROR: Zenoh router failed to start"
    docker-compose logs zenoh-router
    exit 1
fi
echo "✓ Zenoh router is running"

echo "5. Testing ZRC client container..."
docker-compose run --rm zrc-client python -c "import zrc; print('✓ ZRC import successful')" > /dev/null 2>&1
echo "✓ ZRC client container works"

echo "6. Running import tests in Docker..."
docker-compose run --rm zrc-client python tests/test_import.py > /dev/null 2>&1
echo "✓ Import tests passed in Docker"

echo "7. Testing Docker environment setup..."
docker-compose run --rm zrc-client python tests/test_docker_env.py > /dev/null 2>&1
echo "✓ Docker environment test passed"

echo "8. Cleaning up..."
docker-compose down > /dev/null 2>&1
echo "✓ Cleanup completed"

echo ""
echo "=== Docker Environment Verification Complete ==="
echo "All tests passed! Your Docker environment is ready for ZRC development."