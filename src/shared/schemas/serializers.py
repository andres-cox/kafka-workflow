"""Serialization utilities for Kafka messages."""

import json
from datetime import datetime


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects.

    This encoder converts datetime objects to ISO format strings,
    making them JSON-serializable.
    """

    def default(self, obj):
        """Default method to handle datetime objects.

        Args:
            obj: The object to serialize

        Returns:
            The serialized object
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def serialize_message(message: dict) -> bytes:
    """Serialize a message dictionary to bytes using the custom encoder.

    Args:
        message: Dictionary containing the message data

    Returns:
        Serialized message as bytes
    """
    return json.dumps(message, cls=DateTimeEncoder).encode("utf-8")


def deserialize_message(message_bytes: bytes) -> dict:
    """Deserialize message bytes to a dictionary.

    Args:
        message_bytes: Serialized message as bytes

    Returns:
        Deserialized message as dictionary
    """
    return json.loads(message_bytes.decode("utf-8"))
