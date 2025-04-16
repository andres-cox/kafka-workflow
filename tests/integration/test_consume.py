"""Integration tests for Kafka Workflow."""

import time
from http import HTTPStatus

import requests

from shared.utils.logger import logger


def test_consume_messages(api_url, test_message):
    """Test consuming messages from Kafka.

    Args:
        api_url (str): The URL of the API.
        test_message (dict): The test message to produce.
    """
    logger.info(f"Producing message: {test_message}")
    message = requests.post(f"{api_url}/produce/", json=test_message, timeout=5)
    logger.info(f"Message: {message.json()}")
    assert message.status_code == HTTPStatus.OK
    assert message.json()["status"] == "Message sent"

    # Allow some time for processing
    time.sleep(2)

    # Verify consumption
    logger.info(f"Consuming messages from {api_url}/consume/")
    response = requests.get(f"{api_url}/consume/")
    logger.info(f"Response: {response.json()}")
    assert response.status_code == HTTPStatus.OK
    messages = response.json()["messages"]
    assert any(msg["message_id"] == test_message["message_id"] for msg in messages)
