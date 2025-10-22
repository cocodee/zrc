# ZRC (Zenoh Robot Control) Library

[![PyPI version](https://badge.fury.io/py/zrc.svg)](https://badge.fury.io/py/zrc)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ZRC (Zenoh Robot Control) is a robotics communication library based on [Zenoh](https://zenoh.io/), designed to provide efficient, low-latency distributed communication for robotic applications. The library provides three core communication patterns:

- **Publisher/Subscriber (PubSub)**: For real-time data streams and status broadcasting
- **Service/Client**: For synchronous request-response communication
- **Action/Client**: For long-running tasks with feedback, results, and cancellation support

## Features

- Three core communication patterns (PubSub, Service, Action)
- Support for multiple serialization formats (JSON, Protobuf, Raw)
- Thread-safe operations
- Automatic resource management
- Customizable topic prefixes
- Comprehensive error handling

## Installation

```bash
pip install zrc
```

## Quick Start

```python
import zrc

# 1. Create a node
config = {"mode": "peer", "connect": {"endpoints": ["tcp/localhost:7447"]}}
node = zrc.ZRCNode("my_robot", config=config)

try:
    # 2. Create publisher and subscriber
    def message_callback(data):
        print(f"Received: {data}")
    
    publisher = node.create_publisher("sensor_data")
    subscriber = node.create_subscriber("sensor_data", message_callback)
    
    # 3. Send data
    publisher.publish({"temperature": 25.5, "unit": "celsius"})
    
finally:
    node.close()
```

## Documentation

See [doc.md](doc.md) for complete API documentation and advanced usage examples.

## Requirements

- Python 3.7+
- zenoh>=0.7.0

## Docker Environment

For testing and development, a Docker environment is provided. See [DOCKER.md](DOCKER.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.