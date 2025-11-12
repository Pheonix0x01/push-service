import aio_pika
import json
import httpx
from datetime import datetime
from app.core.fcm_client import send_push_notification
from app.worker.retry_handler import handle_retry
from app.api.v1.schemas import NotificationMessage
from app.core.config import settings
from app.utils.logger import logger

async def send_status_update(notification_id, status, error=None):
    async with httpx.AsyncClient() as client:
        try:
            await client.post(settings.status_callback_url, json={
                "notification_id": notification_id,
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "error": error
            })
        except Exception as e:
            logger.error(f"Failed to send status update: {e}")

async def start_consumer():
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    
    queue = await channel.declare_queue("push.queue", durable=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    data = json.loads(message.body)
                    msg = NotificationMessage(**data)
                    
                    await send_push_notification(msg)
                    await send_status_update(msg.request_id, "delivered")
                    logger.info(f"Push notification sent: {msg.request_id}")
                except Exception as e:
                    logger.error(f"Push failed: {e}")
                    await handle_retry(message, e)