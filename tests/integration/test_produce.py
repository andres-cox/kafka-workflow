"""Integration tests for Kafka Workflow."""

from http import HTTPStatus

import requests

from shared.utils.logger import logger


def test_produce_message(api_url, test_message):
    """Test producing a message to Kafka.

    Args:
        api_url (str): The URL of the API.
        test_message (dict): The test message to produce.
    """
    logger.info(f"Producing message: {test_message}")
    response = requests.post(f"{api_url}/produce/", json=test_message, timeout=5)
    logger.info(f"Response: {response.json()}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["status"] == "Message sent"
