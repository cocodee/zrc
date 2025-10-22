# Makefile for ZRC development

.PHONY: help install test test-docker verify-docker clean build

help:
	@echo "ZRC Development Commands:"
	@echo "  install        - Install package in development mode"
	@echo "  test           - Run local tests"
	@echo "  test-docker    - Run tests in Docker environment"
	@echo "  verify-docker  - Verify Docker environment setup"
	@echo "  clean          - Clean build artifacts"
	@echo "  build          - Build distribution packages"

install:
	pip install -e .

test:
	./scripts/test_local.sh

test-docker:
	./scripts/test_docker.sh

verify-docker:
	./scripts/verify_docker_setup.sh

clean:
	rm -rf build/ dist/ *.egg-info/

build:
	python -m build

example:
	python examples/basic_usage.py