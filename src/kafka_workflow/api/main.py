"""A simple API to produce and consume messages from Kafka."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from kafka_workflow.consumer.main import KafkaConsumer
from kafka_workflow.producer.main import KafkaProducer
from shared.schemas.messages import EventMessage

from shared.utils.logger import logger


# Load environment variables from .env file
load_dotenv()

KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
TOPIC_NAME = os.getenv("TOPIC_NAME", "test-topic")
GROUP_ID = os.getenv("GROUP_ID", "test-consumer-group")

# Initialize producer and consumer
producer = KafkaProducer(
    broker_url=KAFKA_BROKER_URL,
    topic_name=TOPIC_NAME,
)
consumer = KafkaConsumer(
    broker_url=KAFKA_BROKER_URL,
    topic_name=TOPIC_NAME,
    group_id=GROUP_ID,
)


async def lifespan(app: FastAPI):
    """Manage startup and shutdown events."""
    # Startup
    await producer.start()
    await consumer.start()
    logger.info("Kafka producer and consumer started.")

    yield  # This will pause here until the app is shutting down

    # Shutdown
    await producer.stop()
    await consumer.stop()
    logger.info("Kafka producer and consumer stopped.")

app = FastAPI(lifespan=lifespan)

@app.post("/produce/")
async def produce_message(message: EventMessage):
    """Produce a message to the Kafka topic."""
    try:
        await producer.send_message(message)
        logger.info(f"Message sent: {message.message_id}")
        logger.info(f"Message payload: {message.payload}")
        return {"status": "Message sent", "message_id": message.message_id}
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from None


@app.get("/consume/")
async def consume_messages():
    """Consume messages from the Kafka topic."""
    try:
        messages = await consumer.consume_messages()  # Get the messages
        return {"messages": messages}  # Return as JSON
    except Exception as e:
        logger.error(f"Error consuming messages: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
