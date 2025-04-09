# Makefile for Kafka Workflow Project

.PHONY: help kapply-zk kapply-kafka kapply-all kforward-kafka run-producer run-consumer kconsole-consumer kclean kget-pods install format lint test clean

# Variables
KAFKA_POD_SELECTOR = app=kafka
ZOOKEEPER_POD_SELECTOR = app=zookeeper
KAFKA_SERVICE = kafka-service
KAFKA_YAML = k8s/kafka.yaml
ZOOKEEPER_YAML = k8s/zookeeper.yaml
KAFKA_PORT_FORWARD = 9092:9092
PRODUCER_SCRIPT = src/producer/main.py
CONSUMER_SCRIPT = src/consumer/main.py
KAFKA_TOPIC = test-topic
KAFKA_BOOTSTRAP_SERVERS ?= localhost:9092

help:
	@echo "Kafka Workflow Project"
	@echo ""
	@echo "Usage:"
	@echo "  make help             Show this help message"
	@echo "  make kapply-zk        Apply Zookeeper Kubernetes resources"
	@echo "  make kapply-kafka     Apply Kafka Kubernetes resources"
	@echo "  make kapply-all       Apply all Kubernetes resources"
	@echo "  make kforward-kafka   Forward Kafka port from pod"
	@echo "  make run-producer     Run Kafka producer"
	@echo "  make run-consumer     Run Kafka consumer"
	@echo "  make kconsole-consumer Run Kafka console consumer in the pod (reads from beginning)"
	@echo "  make kclean           Delete Zookeeper and Kafka Kubernetes resources"
	@echo "  make install          Install dependencies using Poetry"
	@echo "  make format           Format code using ruff"
	@echo "  make lint             Run ruff for linting"
	@echo "  make test             Run pytest for testing"
	@echo "  make clean            Clean up build artifacts"

# --- Kubernetes Management ---
kapply-zk:
	@echo "Applying Zookeeper manifest..."
	poetry run kubectl apply -f $(ZOOKEEPER_YAML)

kapply-kafka:
	@echo "Applying Kafka manifest..."
	poetry run kubectl apply -f $(KAFKA_YAML)

kapply-all: kapply-zk kapply-kafka
	@echo "Applied Zookeeper and Kafka manifests."

kget-pods:
	@echo "Getting pod statuses..."
	@echo "--- Zookeeper Pods ---"
	poetry run kubectl get pods -l $(ZOOKEEPER_POD_SELECTOR)
	@echo "--- Kafka Pods ---"
	poetry run kubectl get pods -l $(KAFKA_POD_SELECTOR)

kforward-kafka:
	@echo "Starting Kafka port-forwarding on $(KAFKA_PORT_FORWARD)... Press Ctrl+C to stop."
	@echo "NOTE: Run 'make run-producer' or 'make run-consumer' in another terminal."
	poetry run kubectl port-forward svc/$(KAFKA_SERVICE) $(KAFKA_PORT_FORWARD)

kclean:
	@echo "Deleting Kafka and Zookeeper resources..."
	poetry run kubectl delete -f $(KAFKA_YAML) --ignore-not-found=true
	poetry run kubectl delete -f $(ZOOKEEPER_YAML) --ignore-not-found=true

# --- Application Execution ---
run-producer:
	@echo "Running Kafka producer..."
	PYTHONPATH=src poetry run python src/producer/main.py

run-consumer:
	@echo "Running Kafka consumer... Press Ctrl+C to stop."
	PYTHONPATH=src poetry run python src/consumer/main.py

kconsole-consumer:
	@echo "Attempting to run Kafka console consumer in the pod..."
	@POD_NAME=$$(poetry run kubectl get pods -l $(KAFKA_POD_SELECTOR) -o jsonpath='{.items[0].metadata.name}'); \
	if [ -z "$$POD_NAME" ]; then \
	    echo "Error: Kafka pod not found. Ensure it's running ('make kget-pods')."; \
	    exit 1; \
	fi; \
	echo "Found Kafka pod: $$POD_NAME"; \
	echo "Connecting to topic '$(KAFKA_TOPIC)' from beginning... Press Ctrl+C to stop."; \
	poetry run kubectl exec -it $$POD_NAME -- \
		kafka-console-consumer \
			--bootstrap-server localhost:9092 \
			--topic $(KAFKA_TOPIC) \
			--from-beginning | cat

install:
	poetry install

format:
	poetry run ruff format .
	poetry run ruff check --fix .

lint:
	poetry run ruff check .

test:
	poetry run pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 