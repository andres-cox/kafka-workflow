"""Message schemas for Kafka producer and consumer."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class MessageType(str, Enum):
    """Enumeration of possible message types."""

    EVENT = "event"
    COMMAND = "command"
    QUERY = "query"


class BaseMessage(BaseModel):
    """Base message model with common fields."""

    message_id: str = Field(
        ...,
        description="Unique identifier for the message",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Message creation timestamp",
    )
    message_type: MessageType = Field(
        ...,
        description="Type of the message",
        examples=[MessageType.EVENT],
    )


class EventMessage(BaseMessage):
    """Model for event messages."""

    event_type: str = Field(
        ...,
        description="Type of the event",
        examples=["user_created", "order_placed"],
    )
    payload: dict = Field(
        ...,
        description="Event payload data",
        examples=[{"user_id": "123", "name": "John Doe"}],
    )
    metadata: dict | None = Field(
        default=None,
        description="Additional metadata about the event",
        examples=[{"source": "api", "version": "1.0"}],
    )

    @field_validator("message_type")
    def validate_message_type(cls, v: MessageType) -> MessageType:
        """Validate that message type is EVENT."""
        if v != MessageType.EVENT:
            raise ValueError("Message type must be EVENT for EventMessage")
        return v


class CommandMessage(BaseMessage):
    """Model for command messages."""

    command: str = Field(
        ...,
        description="Command to execute",
        examples=["create_user", "update_order"],
    )
    parameters: dict = Field(
        ...,
        description="Command parameters",
        examples=[{"user_id": "123", "status": "active"}],
    )

    @field_validator("message_type")
    def validate_message_type(cls, v: MessageType) -> MessageType:
        """Validate that message type is COMMAND."""
        if v != MessageType.COMMAND:
            raise ValueError("Message type must be COMMAND for CommandMessage")
        return v


class QueryMessage(BaseMessage):
    """Model for query messages."""

    query: str = Field(
        ...,
        description="Query to execute",
        examples=["get_user", "list_orders"],
    )
    filters: dict | None = Field(
        default=None,
        description="Query filters",
        examples=[{"status": "active", "date": "2024-01-01"}],
    )

    @field_validator("message_type")
    def validate_message_type(cls, v: MessageType) -> MessageType:
        """Validate that message type is QUERY."""
        if v != MessageType.QUERY:
            raise ValueError("Message type must be QUERY for QueryMessage")
        return v
