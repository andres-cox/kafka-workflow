"""Kafka consumer module for processing messages from Kafka topics."""

import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError, KafkaError
from dotenv import load_dotenv
from loguru import logger

from schemas.messages import EventMessage, MessageType
from schemas.serializers import deserialize_message

# --- Logger Configuration ---
# Remove default handler
logger.remove()
# Add a new handler that logs INFO level messages to stderr
logger.add(
    sys.stderr,
    level="INFO",
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
)

# Load environment variables from .env file
load_dotenv()

KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
TOPIC_NAME = os.getenv("TOPIC_NAME", "test-topic")
GROUP_ID = os.getenv("GROUP_ID", "test-consumer-group")


async def create_consumer() -> AIOKafkaConsumer | None:
    """Creates, starts, and returns an AIOKafkaConsumer instance."""
    consumer = None
    try:
        logger.info(f"Attempting to connect consumer to Kafka broker at {KAFKA_BROKER_URL}")
        consumer = AIOKafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=KAFKA_BROKER_URL,
            group_id=GROUP_ID,
            value_deserializer=deserialize_message,
            auto_offset_reset="earliest",  # Start reading from the earliest message
            enable_auto_commit=True,  # Automatically commit offsets
            request_timeout_ms=30000,  # Increase request timeout to 30 seconds
        )
        # Start the consumer
        await consumer.start()
        logger.success(f"Successfully connected consumer to Kafka broker at {KAFKA_BROKER_URL}")
        logger.info(f"Subscribed to topic '{TOPIC_NAME}' with group ID '{GROUP_ID}'")
        return consumer
    except KafkaConnectionError as e:
        logger.error(f"Consumer connection error: {e}")
        if consumer:
            await consumer.stop()
        return None
    except KafkaError as e:
        logger.error(f"Consumer Kafka error: {e}")
        if consumer:
            await consumer.stop()
        return None
    except Exception:
        logger.exception("An unexpected error occurred during consumer creation")
        if consumer:
            await consumer.stop()
        return None


async def process_message(message_data: dict) -> None:
    """Process a received message using Pydantic models.

    Args:
        message_data: Raw message data from Kafka
    """
    try:
        # Check if this is an old format message
        if "message_type" not in message_data:
            logger.warning("Received message in old format, converting to new format")
            # Convert old format to new format
            message_data = {
                "message_id": str(message_data.get("message_id", str(uuid.uuid4()))),
                "message_type": MessageType.EVENT,
                "event_type": "legacy_event",
                "payload": {"content": message_data.get("payload", "")},
                "metadata": {"timestamp": datetime.now(timezone.utc).isoformat()},
            }

        # Validate and parse the message using Pydantic
        message = EventMessage.model_validate(message_data)
        logger.info(
            f"Processing message: id={message.message_id}, "
            f"type={message.message_type}, "
            f"event_type={message.event_type}, "
            f"created_at={message.timestamp.isoformat()}"
        )
        # Add your message processing logic here
        logger.info(f"Message payload: {message.payload}")
        if message.metadata:
            # Format metadata for better readability
            formatted_metadata = {
                k: v.isoformat() if isinstance(v, datetime) else v for k, v in message.metadata.items()
            }
            logger.info(f"Message metadata: {formatted_metadata}")
    except Exception as e:
        logger.error(f"Error processing message: {e!s}")
        raise


async def consume_messages(consumer: AIOKafkaConsumer) -> None:
    """Continuously consumes and processes messages from the subscribed topic."""
    logger.info("Starting message consumption... Press Ctrl+C to stop.")
    try:
        # Consume messages
        async for msg in consumer:
            logger.info(
                f"Received message: topic={msg.topic}, "
                f"partition={msg.partition}, "
                f"offset={msg.offset}, "
                f"key={msg.key}, "
                f"timestamp={msg.timestamp}"
            )
            await process_message(msg.value)
    except asyncio.CancelledError:
        logger.info("Consumption task cancelled.")  # Info level, expected during shutdown
    except Exception:
        logger.exception("An error occurred during consumption")  # Log stack trace for unexpected errors
    finally:
        logger.info("Stopped consuming messages.")


async def main() -> None:
    """Main async function to create, run, and gracefully shutdown the Kafka consumer."""
    consumer = await create_consumer()
    if not consumer:
        logger.warning("Consumer creation failed, exiting.")
        return  # Exit if consumer creation failed

    consume_task = asyncio.create_task(consume_messages(consumer))

    try:
        # Wait for the consumption task to complete (or be cancelled)
        await consume_task
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, initiating graceful shutdown...")
        consume_task.cancel()
        # Wait for the task to actually cancel
        try:
            await consume_task
        except asyncio.CancelledError:
            logger.success("Consume task successfully cancelled.")
    finally:
        # Ensure consumer is stopped properly
        logger.info("Stopping async consumer...")
        await consumer.stop()
        logger.success("Async Kafka consumer stopped.")


if __name__ == "__main__":
    logger.info("Starting async consumer application...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # This handles Ctrl+C if it happens VERY early
        logger.warning("KeyboardInterrupt during startup/shutdown.")
    logger.info("Async consumer application finished.")
