# Docker Environment for ZRC

This document explains how to use the Docker environment for testing and development of the ZRC library.

## Prerequisites

- Docker
- Docker Compose

## Docker Environment Overview

The Docker environment consists of three services:

1. **zenoh-router**: A Zenoh router for message routing
2. **zrc-client**: A ZRC client for testing
3. **zrc-server**: A ZRC server for testing

## Quick Start

### Using Make Commands

```bash
# Verify Docker environment
make verify-docker

# Run tests in Docker environment
make test-docker
```

### Build and Run Tests

```bash
# Run tests in Docker environment
./scripts/test_docker.sh
```

### Verify Docker Setup

```bash
# Verify that the Docker environment is properly configured
./scripts/verify_docker_setup.sh
```

### Manual Docker Usage

```bash
# Build the images
docker-compose build

# Start the Zenoh router
docker-compose up -d zenoh-router

# Run a test
docker-compose run --rm zrc-client python tests/test_import.py

# Run the example
docker-compose run --rm zrc-client python examples/basic_usage.py

# Stop all services
docker-compose down
```

## Services

### Zenoh Router

The Zenoh router is the central message broker that enables communication between ZRC nodes.

- Image: `eclipse/zenoh:latest`
- Ports: 7447 (TCP)
- Command: `--mode router --listen tcp/0.0.0.0:7447`

### ZRC Client

A client container with the ZRC library installed.

- Built from the local Dockerfile
- Connects to the Zenoh router
- Runs example scripts and tests

### ZRC Server

A server container with the ZRC library installed.

- Built from the local Dockerfile
- Connects to the Zenoh router
- Can be used for multi-node testing

## Environment Variables

- `RUST_LOG`: Controls logging level (info, debug, error, etc.)

## Network Configuration

All containers are on the same Docker network and can communicate with each other using service names:

- `zenoh-router`: The Zenoh router
- `zrc-client`: The ZRC client container
- `zrc-server`: The ZRC server container

## Ports

- 7447: Zenoh TCP port
- 7446: Zenoh REST API port (if enabled)

## Development Workflow

1. Make changes to the code
2. Rebuild the Docker images: `docker-compose build`
3. Run tests: `docker-compose run --rm zrc-client python tests/test_import.py`
4. Run examples: `docker-compose run --rm zrc-client python examples/basic_usage.py`

## Troubleshooting

### Connection Issues

If you see connection errors, make sure the Zenoh router is running:

```bash
docker-compose up -d zenoh-router
```

Wait a few seconds for the router to initialize before running other services.

### Permission Issues

If you encounter permission issues with Docker, make sure your user is in the docker group:

```bash
sudo usermod -aG docker $USER
```

### Clean Up

To remove all containers and networks:

```bash
docker-compose down -v --remove-orphans
```