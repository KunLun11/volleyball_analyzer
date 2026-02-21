import asyncio
import json
import logging

from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import datetime

from aiokafka import AIOKafkaConsumer
from asynch import Connection


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConsumerSettings(BaseSettings):
    KAFKA_URL: str = "kafka:9092"
    CLICKHOUSE_HOST: str = "clickhouse"
    CLICKHOUSE_PORT: int = 9000
    CLICKHOUSE_DB: str = "volleyball"
    CLICKHOUSE_USER: str = "default"
    CLICKHOUSE_PASSWORD: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = ConsumerSettings()


class KafkaToClickHouseConsumer:
    def __init__(self):
        self.consumer = None
        self.clickhouse = None

    async def start(self):
        self.clickhouse_conn = Connection(
            host=settings.CLICKHOUSE_HOST,
            port=settings.CLICKHOUSE_PORT,
            database=settings.CLICKHOUSE_DB,
            user=settings.CLICKHOUSE_USER,
            password=settings.CLICKHOUSE_PASSWORD,
        )
        await self.clickhouse_conn.connect()
        logger.info("Connected to ClickHouse")
        self.consumer = AIOKafkaConsumer(
            "match-started",
            "point-scored",
            "set-completed",
            "match-completed",
            bootstrap_servers=settings.KAFKA_URL,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            group_id="clickhouse-writer",
            auto_offset_reset="earliest",
        )
        await self.consumer.start()
        logger.info("Connected to Kafka")

    async def run(self):
        await self.start()
        try:
            async for msg in self.consumer:
                await self._process_event(msg)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
        finally:
            await self.stop()

    async def _process_event(self, msg):
        event_type = msg.topic
        data = msg.value
        occurred_at = data.get("occurred_at", datetime.now().isoformat())
        logger.info(f"Processing event: {event_type}, match: {data.get('match_id')}")
        query = """
            INSERT INTO domain_events 
            (event_id, event_type, match_id, payload, occurred_at)
            VALUES (generateUUIDv4(), %(event_type)s, %(match_id)s, %(payload)s, %(occurred_at)s)
        """
        await self.clickhouse_conn.execute(
            query,
            {
                "event_type": event_type,
                "match_id": data.get("match_id"),
                "payload": json.dumps(data),
                "occurred_at": datetime.fromisoformat(
                    occurred_at.replace("Z", "+00:00")
                ),
            },
        )
        # if event_type == "point-scored":
        #     await self._log_point_scored(data)

    # async def _log_point_scored(self, data):
    #     pass

    async def stop(self):
        if self.consumer:
            await self.consumer.stop()
        if self.clickhouse:
            await self.clickhouse_conn.close()
        logger.info("Consumer stopped")


if __name__ == "__main__":
    consumer = KafkaToClickHouseConsumer()
    asyncio.run(consumer.run())
