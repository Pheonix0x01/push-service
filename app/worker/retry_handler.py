import asyncio
import aio_pika
from app.core.config import settings
from app.utils.logger import logger

async def handle_retry(message, error):
    retry_count = message.headers.get("x-retry-count", 0) if message.headers else 0
    retry_count += 1
    
    if retry_count > settings.max_retries:
        await move_to_dead_letter(message, error)
        return

    delay = settings.retry_backoff_base ** retry_count
    logger.info(f"Retrying in {delay} seconds (attempt {retry_count})")
    await asyncio.sleep(delay)
    await republish(message, retry_count)

async def republish(message, retry_count):
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=message.body,
            headers={"x-retry-count": retry_count},
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        ),
        routing_key="push.queue"
    )
    await connection.close()

async def move_to_dead_letter(message, error):
    logger.error(f"Moving to dead letter queue: {error}")
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=message.body,
            headers={"error": str(error)},
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        ),
        routing_key="failed.queue"
    )
    await connection.close()