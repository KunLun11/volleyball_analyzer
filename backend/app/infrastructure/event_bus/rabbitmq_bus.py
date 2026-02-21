import json
import logging
from datetime import datetime
from typing import Awaitable, Callable

import aio_pika
from aio_pika import DeliveryMode, Message

from app.config import settings
from app.domain.events import DomainEvent

logger = logging.getLogger(__name__)


class RabbitMQEventBus:
    def __init__(self, url: str = settings.RABBITMQ_URL):
        self._url = url
        self._connection = None
        self._channel = None
        self._started = False
        self._consumer_tag = None

    async def start(self):
        if self._started:
            return
        try:
            self._connection = await aio_pika.connect_robust(self._url)
            self._channel = await self._connection.channel()
            await self._channel.set_qos(prefetch_count=1)

            await self._channel.declare_queue(
                settings.BOT_TO_BACKEND_QUEUE,
                durable=True,
                auto_delete=False,
            )
            await self._channel.declare_queue(
                settings.BOT_RESPONSES_QUEUE,
                durable=True,
                auto_delete=False,
            )
            self._started = True
            logger.info("RabbitMQ connected and queues declared")
        except Exception as e:
            logger.error(f"Failed to start RabbitMQ: {e}")
            raise

    async def stop(self):
        if not self._started:
            return
        if self._channel:
            await self._channel.close()
        if self._connection:
            await self._connection.close()
        self._started = False
        logger.info("RabbitMQ disconnected")

    async def publish(self, events: list[DomainEvent]):
        """Publish domain events to Kafka (for analytics)"""
        if not self._started:
            await self.start()
        
        for event in events:
            message = Message(
                body=json.dumps(event.to_dict()).encode("utf-8"),
                content_type="application/json",
                delivery_mode=DeliveryMode.PERSISTENT,
            )
            await self._channel.default_exchange.publish(
                message,
                routing_key="domain_events",
            )
        logger.debug(f"Published {len(events)} domain events")

    async def publish_to_bot(
        self,
        chat_id: int,
        advice: str,
        correlation_id: str,
        match_id: str,
        reply_to: str,
    ):
        if not self._started:
            await self.start()

        payload = {
            "correlation_id": correlation_id,
            "chat_id": chat_id,
            "advice": advice,
            "timestamp": datetime.now().isoformat(),
            "status": "success",
        }

        message = Message(
            body=json.dumps(payload).encode("utf-8"),
            correlation_id=correlation_id,
            content_type="application/json",
            delivery_mode=DeliveryMode.PERSISTENT,
        )
        await self._channel.default_exchange.publish(
            message,
            routing_key=reply_to,
        )
        logger.debug(f"Published advice to bot: {correlation_id}")

    async def consume_bot_requests(
        self,
        handler: Callable[[dict, aio_pika.IncomingMessage], Awaitable[None]],
    ):
        if not self._started:
            await self.start()

        queue = await self._channel.get_queue(settings.BOT_TO_BACKEND_QUEUE)

        async def on_message(message: aio_pika.IncomingMessage):
            try:
                body = json.loads(message.body.decode())
                logger.debug(f"Received message: {body.get('action')}")
                await handler(body, message)
                await message.ack()
                logger.debug(f"Message acknowledged")
            except json.JSONDecodeError:
                logger.error("Failed to decode message")
                await message.reject(requeue=False)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await message.reject(requeue=True)

        self._consumer_tag = await queue.consume(on_message)
        logger.info(f"Consuming from {settings.BOT_TO_BACKEND_QUEUE}")

    async def stop_consuming(self):
        if self._consumer_tag and self._channel:
            await self._channel.cancel(self._consumer_tag)
            self._consumer_tag = None
