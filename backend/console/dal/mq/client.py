"""Kafka client wrapper for message queue operations."""

from typing import Optional

from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient

from backend.config.settings import Settings


class KafkaClient:
    """Kafka client wrapper providing producer/consumer instances."""

    _instance: Optional["KafkaClient"] = None

    def __init__(self, settings: Settings):
        self.settings = settings
        self._producer: Optional[Producer] = None
        self._consumer: Optional[Consumer] = None

        self._admin = AdminClient(self.settings.kafka_common_config)
        self._validate_connection()

    def _validate_connection(self) -> None:
        """Validate Kafka connectivity by fetching cluster metadata."""
        try:
            self._admin.list_topics(timeout=5)
        except Exception as exc:
            raise ConnectionError(
                f"Failed to connect to Kafka: {exc}") from exc

    @classmethod
    def get_instance(cls, settings: Settings) -> "KafkaClient":
        """Get or create Kafka client singleton."""
        if cls._instance is None:
            cls._instance = cls(settings)
        return cls._instance

    def get_producer(self) -> Producer:
        """Get or create Kafka producer."""
        if self._producer is None:
            self._producer = Producer(self.settings.kafka_common_config)
        return self._producer

    def get_consumer(self, group_id: str) -> Consumer:
        conf = self.settings.kafka_common_config
        conf['group.id'] = group_id
        return Consumer(conf)

    def close(self) -> None:
        """Close underlying Kafka connections and reset singleton."""
        if self._consumer is not None:
            self._consumer.close()
            self._consumer = None

        if self._producer is not None:
            self._producer.flush(timeout=10)
            self._producer = None

        KafkaClient._instance = None
