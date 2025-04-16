"""Kafka consumer module for processing messages from Kafka topics."""

import asyncio
from datetime import datetime

from aiokafka import AIOKafkaConsumer, TopicPartition

from shared.schemas.messages import EventMessage
from shared.schemas.serializers import deserialize_message
from shared.utils.logger import logger


class KafkaConsumer:
    """Kafka consumer class for processing messages from Kafka topics."""

    def __init__(self, broker_url: str, topic_name: str, group_id: str):
        """Initialize the Kafka consumer."""
        self.broker_url = broker_url
        self.topic_name = topic_name
        self.group_id = group_id
        self.consumer = None

    async def start(self):
        """Start the Kafka consumer."""
        self.consumer = AIOKafkaConsumer(
            self.topic_name,
            bootstrap_servers=self.broker_url,
            auto_offset_reset="earliest",
            group_id=self.group_id,
            value_deserializer=deserialize_message,
        )
        await self.consumer.start()
        logger.success(f"Successfully connected consumer to Kafka broker at {self.broker_url}")

    async def stop(self):
        """Stop the Kafka consumer."""
        await self.consumer.stop()
        logger.success("Async Kafka consumer stopped.")

    async def process_message(self, message_data: dict) -> None:
        """Process a received message using Pydantic models."""
        try:
            # Validate and parse the message using Pydantic
            message = EventMessage.model_validate(message_data)
            logger.info(
                f"Processing message: id={message.message_id}, "
                f"type={message.message_type}, "
                f"event_type={message.event_type}, "
                f"created_at={message.timestamp.isoformat()}"
            )
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

    async def consume_messages(self):
        """Continuously consumes and processes messages from the subscribed topic."""
        logger.info("Starting message consumption...")
        messages = []
        try:
            # Get current end offsets (latest available messages)
            partitions = self.consumer.assignment()
            end_offsets = await self.consumer.end_offsets(partitions)
            logger.info(f"Partitions: {partitions}")
            logger.info(f"End offsets: {end_offsets}")
            async for msg in self.consumer:
                await self.process_message(msg.value)
                messages.append(msg.value)
                
                # Create a TopicPartition object for lookup
                tp = TopicPartition(msg.topic, msg.partition)
                if msg.offset >= end_offsets[tp] - 1:
                    logger.info(f"Reached latest offset for partition {msg.partition}")
                    break
            logger.info(f"Messages: {messages}")
            return messages  # Return the list of message
        except asyncio.CancelledError:
            logger.info("Consumption task cancelled.")  # Info level, expected during shutdown
        except Exception:
            logger.exception("An error occurred during consumption")  # Log stack trace for unexpected errors
        finally:
            logger.info("Stopped consuming messages.")
