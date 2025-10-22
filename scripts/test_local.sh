#!/bin/bash

# Local test script for ZRC

set -e  # Exit on any error

echo "Running import tests..."
python tests/test_import.py

echo "Running example usage..."
python examples/basic_usage.py

echo "Local tests completed successfully!"