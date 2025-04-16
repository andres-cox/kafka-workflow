# Makefile for Kafka Workflow Project

.PHONY: help kapply-zk kapply-kafka kapply-all kforward-kafka run-producer run-consumer kconsole-consumer kclean kget-pods install format lint test clean

# Variables
KAFKA_POD_SELECTOR = app=kafka
ZOOKEEPER_POD_SELECTOR = app=zookeeper
KAFKA_SERVICE = kafka-service
KAFKA_YAML = k8s/kafka.yaml
API_YAML = k8s/api-deployment.yaml
ZOOKEEPER_YAML = k8s/zookeeper.yaml
KAFKA_PORT_FORWARD = 9092:9092
API_PORT_FORWARD = 8000:8000
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
	@echo "  make kclean           Delete Zookeeper and Kafka Kubernetes resources"
	@echo "  make install          Install dependencies using Poetry"
	@echo "  make install-dev      Install dependencies using Poetry with dev profile"
	@echo "  make install-test     Install dependencies using Poetry with test profile"
	@echo "  make format           Format code using ruff"
	@echo "  make lint             Run ruff for linting"
	@echo "  make test             Run pytest for testing"
	@echo "  make clean            Clean up build artifacts" 
	@echo "  make kforward-api     Forward API port from pod"
	@echo "  make run-api          Run Kafka API"
	@echo "  make kconsole-consumer Run Kafka console consumer"
	@echo "  make kclean           Delete Kafka and Zookeeper resources"
	@echo "  make kget-pods        Get pod statuses"
	@echo "  make test-integration Run integration tests"
	@echo "  make docker-build     Build Docker image"
	@echo "  make docker-run       Run Docker container"	
	@echo "  make minikube-start   Start Minikube"
	@echo "  make minikube-docker-env-bash Set Minikube Docker environment, in order to use local docker images"
	@echo "  make minikube-docker-env-fish Set Minikube Docker environment, in order to use local docker images"
	@echo "  make minikube-stop    Stop Minikube"
	@echo "  make minikube-status  Check Minikube status"
	@echo "  make minikube-delete  Delete Minikube"
	
# --- Minikube Management ---
minikube-start:
	@echo "Starting Minikube..."
	minikube start --cpus=4 --memory=8192 --driver=docker

minikube-docker-env-bash:
	eval $(minikube docker-env)

minikube-docker-env-fish:
	eval (minikube docker-env)

minikube-stop:
	@echo "Stopping Minikube..."
	minikube stop

minikube-status:
	@echo "Checking Minikube status..."
	minikube status

minikube-delete:
	@echo "Deleting Minikube..."
	minikube delete

# --- Docker Management ---
docker-build:
	docker build -t $(DOCKER_IMAGE_NAME) .

docker-run:
	docker run -p $(DOCKER_PORT):$(DOCKER_PORT) $(DOCKER_IMAGE_NAME)

# --- Kubernetes Management ---
kapply-zk:
	@echo "Applying Zookeeper manifest..."
	kubectl apply -f $(ZOOKEEPER_YAML)

kapply-kafka:
	@echo "Applying Kafka manifest..."
	kubectl apply -f $(KAFKA_YAML)

kapply-api:
	@echo "Applying API manifest..."
	kubectl apply -f $(API_YAML)

kapply-all: kapply-zk kapply-kafka kapply-api
	@echo "Applied Zookeeper and Kafka manifests."

kget-pods:
	@echo "Getting pod statuses..."
	@echo "--- Zookeeper Pods ---"
	kubectl get pods -l $(ZOOKEEPER_POD_SELECTOR)
	@echo "--- Kafka Pods ---"
	kubectl get pods -l $(KAFKA_POD_SELECTOR)
	@echo "--- API Pods ---"
	kubectl get pods -l $(API_POD_SELECTOR)

kforward-api:
	@echo "Starting API port-forwarding on $(API_PORT_FORWARD)... Press Ctrl+C to stop."
	kubectl port-forward svc/api $(API_PORT_FORWARD)

kclean:
	@echo "Deleting Kafka and Zookeeper resources..."
	kubectl delete -f $(API_YAML) --ignore-not-found=true
	kubectl delete -f $(KAFKA_YAML) --ignore-not-found=true
	kubectl delete -f $(ZOOKEEPER_YAML) --ignore-not-found=true

# --- Application Execution ---
run-api:
	@echo "Running Kafka API..."
	poetry run python -m kafka_workflow.api.main

kconsole-consumer:
	@echo "Attempting to run Kafka console consumer in the pod..."
	@POD_NAME=$$(kubectl get pods -l $(KAFKA_POD_SELECTOR) -o jsonpath='{.items[0].metadata.name}'); \
	if [ -z "$$POD_NAME" ]; then \
	    echo "Error: Kafka pod not found. Ensure it's running ('make kget-pods')."; \
	    exit 1; \
	fi; \
	echo "Found Kafka pod: $$POD_NAME"; \
	echo "Connecting to topic '$(KAFKA_TOPIC)' from beginning... Press Ctrl+C to stop."; \
	kubectl exec -it $$POD_NAME -- \
		kafka-console-consumer \
			--bootstrap-server kafka-service:9092 \
			--topic $(KAFKA_TOPIC) \
			--from-beginning | cat

# --- Poetry Management ---
install:
	poetry install

install-dev:
	poetry install --with dev

install-test:
	poetry install --with test

format:
	poetry run ruff format .
	poetry run ruff check --fix .

lint:
	poetry run ruff check .

test:
	poetry run pytest

test-integration:
	poetry run pytest -v -s tests/integration

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