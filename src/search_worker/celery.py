from __future__ import annotations

import json
import os

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from celery import Celery
from meilisearch import Client

BROKER_URL = os.getenv("REDIS_URL", "redis://redis:6379/1")
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
MEILI_URL = os.getenv("MEILI_URL", "http://meili:7700")
MEILI_KEY = os.getenv("MEILI_MASTER_KEY", "masterKey")

celery_app = Celery("search_worker", broker=BROKER_URL)


@celery_app.task
def consume_and_index() -> None:
    import asyncio

    async def _run() -> None:
        consumer = AIOKafkaConsumer(
            "block_patch",
            bootstrap_servers=KAFKA_BOOTSTRAP,
            value_deserializer=lambda v: json.loads(v.decode()),
        )
        try:
            await consumer.start()
        except KafkaError:
            return

        client = Client(MEILI_URL, MEILI_KEY)
        try:
            client.create_index("blocks")
        except Exception:
            pass
        index = client.index("blocks")
        batch: list[dict] = []
        try:
            async for msg in consumer:
                batch.append(msg.value)
                if len(batch) >= 50:
                    index.add_documents(batch)
                    batch.clear()
        finally:
            if batch:
                index.add_documents(batch)
            await consumer.stop()

    asyncio.run(_run())
