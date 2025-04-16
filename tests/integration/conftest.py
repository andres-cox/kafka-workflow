"""Integration tests for Kafka Workflow."""

from typing import Any

import pytest
from faker import Faker
from kubernetes import client, config

from shared.schemas.messages import MessageType

fake = Faker()


@pytest.fixture(scope="module")
def api_url():
    """Get the API service URL."""
    # Load kube config (works in-cluster and locally)
    try:
        config.load_kube_config()
    except Exception:
        config.load_incluster_config()

    # Get API service URL
    core_v1 = client.CoreV1Api()
    services = core_v1.list_service_for_all_namespaces(label_selector="app=api")

    if not services.items:
        return "http://localhost:8000"  # Fallback for local testing

    svc = services.items[0]
    return f"http://{svc.metadata.name}.{svc.metadata.namespace}:{svc.spec.ports[0].port}"


@pytest.fixture
def test_message() -> dict[str, Any]:
    """Generate a test message."""
    return {
        "message_id": fake.uuid4(),
        "message_type": MessageType.EVENT,
        "event_type": fake.word(),
        "payload": {"user_id": fake.uuid4(), "name": fake.name()},
        "metadata": {"source": "api", "version": "1.0"},
    }
