# Stage 1: Build
FROM python:3.10-slim as builder

WORKDIR /app
ENV POETRY_VERSION=2.1.2

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Copy ALL files needed for installation
COPY pyproject.toml poetry.lock ./
COPY src/kafka_workflow ./src/kafka_workflow
COPY src/shared ./src/shared

# Install dependencies (including your package)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --only main

# Stage 2: Runtime
FROM python:3.10-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --from=builder /app/src /app/src

# Environment variables
ENV PYTHONPATH=/app
ENV KAFKA_BROKER_URL=kafka-service:9092
ENV TOPIC_NAME=test-topic

# Run the API service
CMD ["python", "-m", "kafka_workflow.api.main"]