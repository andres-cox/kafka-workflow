# Kafka Workflow

A Python-based Kafka producer and consumer implementation using FastAPI and aiokafka.

## Features

- Async Kafka producer and consumer
- Kubernetes deployment support
- Environment-based configuration
- Comprehensive logging
- Type hints and linting

## Prerequisites

- Python 3.10+
- Poetry for dependency management
- Kubernetes cluster (for deployment)
- Kafka cluster

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd kafka-workflow
```

2. Install dependencies:
```bash
make install
```

## Usage

### Local Development

1. Start Kafka (using Kubernetes):
```bash
make kapply-all
```

2. Run the producer:
```bash
make run-producer
```

3. Run the consumer:
```bash
make run-consumer
```

### Kubernetes Deployment

1. Apply Kubernetes manifests:
```bash
make kapply-all
```

2. Forward Kafka port:
```bash
make kforward-kafka
```

## Development

- Format code: `make format`
- Run linter: `make lint`
- Run tests: `make test`
- Clean build artifacts: `make clean`

## Project Structure

```
kafka-workflow/
├── src/
│   └── kafka_workflow/
│       ├── __init__.py
│       ├── producer.py
│       └── consumer.py
├── kubernetes/
│   ├── kafka/
│   └── zookeeper/
├── Makefile
├── pyproject.toml
└── README.md
```

## License

MIT 