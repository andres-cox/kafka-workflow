"""Kafka producer module for sending messages to Kafka topics."""

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from schemas.messages import EventMessage
from schemas.serializers import serialize_message
from src.utils.logger import logger


class KafkaProducer:
    """Kafka producer class for sending messages to Kafka topics."""

    def __init__(self, broker_url: str, topic_name: str):
        """Initialize the Kafka producer."""
        self.broker_url = broker_url
        self.topic_name = topic_name
        self.producer = None

    async def start(self):
        """Start the Kafka producer."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.broker_url,
            value_serializer=serialize_message,
            acks="all",
        )
        await self.producer.start()
        logger.success(f"Successfully connected producer to Kafka broker at {self.broker_url}")

    async def stop(self):
        """Stop the Kafka producer."""
        await self.producer.stop()
        logger.success("Async Kafka producer stopped.")

    async def send_message(self, message: EventMessage) -> bool:
        """Sends a message asynchronously to the specified Kafka topic."""
        try:
            logger.debug(f"Sending message with id {message.message_id} to topic '{self.topic_name}'")
            # Send message and wait for acknowledgement
            metadata = await self.producer.send_and_wait(self.topic_name, value=message.model_dump())
            logger.info(
                f"Message id={message.message_id} sent successfully: "
                f"topic='{self.topic_name}', "
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
