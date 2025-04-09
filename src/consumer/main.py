"""Kafka consumer module for processing messages from Kafka topics."""

import asyncio
import json
import sys

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError, KafkaError
from loguru import logger

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

# Configuration
KAFKA_BROKER_URL = "localhost:9092"
TOPIC_NAME = "test-topic"
GROUP_ID = "test-consumer-group"


async def create_consumer() -> AIOKafkaConsumer | None:
    """Creates, starts, and returns an AIOKafkaConsumer instance."""
    consumer = None
    try:
        logger.info(f"Attempting to connect consumer to Kafka broker at {KAFKA_BROKER_URL}")
        consumer = AIOKafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=KAFKA_BROKER_URL,
            group_id=GROUP_ID,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
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


async def consume_messages(consumer: AIOKafkaConsumer) -> None:
    """Continuously consumes and prints messages from the subscribed topic."""
    logger.info("Starting message consumption... Press Ctrl+C to stop.")
    try:
        # Consume messages
        async for msg in consumer:
            # Changed from DEBUG to INFO to ensure messages are visible
            logger.info(
                f"Consumed msg: topic={msg.topic}, "
                f"partition={msg.partition}, "
                f"offset={msg.offset}, "
                f"key={msg.key}, "
                f"value={msg.value}, "
                f"timestamp={msg.timestamp}"
            )
            # Add processing logic here
            # Example: logger.info(f"Processing message: {msg.value}")
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
