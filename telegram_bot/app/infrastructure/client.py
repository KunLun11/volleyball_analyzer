import asyncio
import json
import logging
from typing import Any
import uuid

import aio_pika

from datetime import datetime, timezone

from app.config import settings


logger = logging.getLogger(__name__)


class RabbitMQClient:
    def __init__(
        self,
        url: str = settings.RABBITMQ_URL,
        timeout: int = settings.RABBITMQ_TIMEOUT,
    ):
        self._url = url
        self._timeout = timeout
        self._connection = None
        self._channel = None
        self._started = False
        self._response_futures: dict[str, asyncio.Future] = {}
        self._consumer_tags: dict[str, str] = {}

    async def start(self):
        if self._started:
            return
        try:
            self._connection = await aio_pika.connect_robust(self._url)
            self._channel = await self._connection.channel()
            await self._channel.set_qos(prefetch_count=1)

            await self._channel.declare_exchange(
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
        self._response_futures.clear()
        self._consumer_tags.clear()
        logger.info("RabbitMQ disconnected")

    async def publish_request(
        self, action: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        if not self._started:
            await self.start()

        if not self._channel:
            raise ConnectionError("Channel is not available")

        correlation_id = str(uuid.uuid4())
        queue = await self._channel.declare_queue("", exclusive=True, auto_delete=True)
        queue_name = queue.name

        future = asyncio.get_event_loop().create_future()
        self._response_futures[correlation_id] = future

        async def on_response(message: aio_pika.IncomingMessage):
            try:
                data = json.loads(message.body.decode())
                if data.get("correlation_id") == correlation_id:
                    future.set_result(data)
                    await message.ack()
                else:
                    await message.reject(requeue=True)
            except Exception as e:
                future.set_exception(e)

        consumer_tag = await queue.consume(on_response)
        self._consumer_tags[queue_name] = consumer_tag

        try:
            message_body = {
                "correlation_id": correlation_id,
                "action": action,
                **payload,
                "reply_to": queue_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            body = json.dumps(message_body).encode("utf-8")
            message = aio_pika.Message(
                body=body,
                correlation_id=correlation_id,
                reply_to=queue_name,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type="application/json",
            )
            await self._channel.default_exchange.publish(
                message,
                routing_key=settings.BOT_TO_BACKEND_QUEUE,
            )
            try:
                result = await asyncio.wait_for(future, timeout=self._timeout)
                return result
            except asyncio.TimeoutError:
                raise TimeoutError(f"No response after {self._timeout}s")
        finally:
            self._response_futures.pop(correlation_id, None)
            if queue_name in self._consumer_tags:
                await queue.cancel(self._consumer_tags.pop(queue_name))
            try:
                await queue.delete()
            except Exception:
                pass

    async def health(self) -> bool:
        try:
            if not self._started:
                await self.start()
            queue = await self._channel.declare_queue(
                "", exclusive=True, auto_delete=True
            )
            await queue.delete()
            return True
        except Exception:
            return False

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
