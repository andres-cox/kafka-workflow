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

## Setup Minikube

1. Start Minikube:
   ```bash
   make minikube-start
   ```

### Local Development

1. Point your local Docker CLI to Minikube's internal Docker daemon, in order to use local images
   ```bash
   make minikube-docker-env-bash
   
   make minikube-docker-env-fish # For fish shell
   ```

2. Initialize Docker:
   ```bash
   make docker-build
   ```

3. Provision all services in minikube:
   ```bash
   make kapply-all
   ```

4. Forward API port for Kafka:
   ```bash
   make kforward-api
   ```

5. Run producer and consumer tests:
   ```bash
   make test-integration
   ```

## Development

- Format code: `make format`
- Run linter: `make lint`
- Run tests: `make test`
- Clean build artifacts: `make clean`

## Project Structure

```
kafka-workflow/
├── Dockerfile
├── Makefile
├── README.md
├── k8s
│   ├── api-deployment.yaml
│   ├── kafka.yaml
│   └── zookeeper.yaml
├── poetry.lock
├── pyproject.toml
├── src
│   ├── kafka_workflow
│   │   ├── api
│   │   │   └── main.py
│   │   ├── consumer
│   │   │   └── main.py
│   │   └── producer
│   │       └── main.py
│   └── shared
│       ├── schemas
│       │   ├── messages.py
│       │   └── serializers.py
│       └── utils
│           └── logger.py
└── tests
    └── integration
        ├── conftest.py
        ├── test_consume.py
        └── test_produce.py

```

## License

MIT 