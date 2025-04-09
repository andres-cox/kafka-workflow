"""Kafka producer module for sending messages to Kafka topics."""

import asyncio
import sys
import uuid
from datetime import datetime, timezone

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError, KafkaError
from loguru import logger

from schemas.messages import EventMessage, MessageType
from schemas.serializers import serialize_message

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


async def create_producer() -> AIOKafkaProducer | None:
    """Creates and returns an AIOKafkaProducer instance."""
    producer = None
    try:
        logger.info(f"Attempting to connect producer to Kafka broker at {KAFKA_BROKER_URL}")
        producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BROKER_URL,
            value_serializer=serialize_message,
            acks="all",
        )
        # Start the producer
        # The start() method will wait until the connection is established.
        await producer.start()
        logger.success(f"Successfully connected producer to Kafka broker at {KAFKA_BROKER_URL}")
        return producer
    except KafkaConnectionError as e:
        logger.error(f"Producer connection error: {e}")
        if producer:
            await producer.stop()
        return None
    except KafkaError as e:
        logger.error(f"Producer Kafka error: {e}")
        if producer:
            await producer.stop()
        return None
    except Exception:
        logger.exception("An unexpected error occurred during producer creation")
        if producer:
            await producer.stop()
        return None


async def send_message(producer: AIOKafkaProducer, topic: str, message: EventMessage) -> bool:
    """Sends a message asynchronously to the specified Kafka topic."""
    try:
        logger.debug(f"Sending message with id {message.message_id} to topic '{topic}'")
        # Send message and wait for acknowledgement
        metadata = await producer.send_and_wait(topic, value=message.model_dump())
        logger.info(
            f"Message id={message.message_id} sent successfully: "
            f"topic='{topic}', "
            f"partition={metadata.partition}, "
            f"offset={metadata.offset}"
        )
        return True
    except KafkaError as e:
        logger.error(f"Error sending message id={message.message_id}: {e}")
        return False
    except Exception:
        logger.exception(f"An unexpected error occurred sending message id={message.message_id}")
        return False


async def main() -> None:
    """Main async function to create producer and send a test message."""
    producer = await create_producer()
    if not producer:
        logger.warning("Producer creation failed, exiting.")
        return

    try:
        test_message = EventMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.EVENT,
            event_type="test_event",
            payload={"content": "Hello Kafka from Async Python producer!!!!"},
            metadata={
                "source": "test",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
        logger.info(f"Attempting to send test message id={test_message.message_id}")
        success = await send_message(producer, TOPIC_NAME, test_message)
        if success:
            logger.success("Async message processing complete.")
        else:
            logger.error("Async message sending failed.")
    finally:
        if producer:
            logger.info("Stopping async producer...")
            await producer.stop()
            logger.success("Async Kafka producer stopped.")


if __name__ == "__main__":
    logger.info("Starting async producer application...")
    asyncio.run(main())
    logger.info("Async producer application finished.")
