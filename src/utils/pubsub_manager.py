from google.cloud import pubsub_v1
from dataclasses import dataclass
from typing import Optional
import json
from datetime import datetime

from .logging import get_logger, setup_logging

logger = get_logger(__name__)
setup_logging()

@dataclass
class PubSubManager:

    topic_name: str
    service_name: Optional[str] = None

    def __post_init__(self) -> None:
        self.publisher = pubsub_v1.PublisherClient()

    def publish_detection(self, topic_path, message_data, service_name=None):
        try:
            enriched_data = {
                "payload": message_data,
            }
            attributes = {
                "service": service_name,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            wrapped_data = {"data": enriched_data, "attributes": attributes}
            message_json = json.dumps(wrapped_data).encode("utf-8")
            future = self.publisher.publish(topic_path, message_json)
            message_id = future.result()
            logger.info(f"Published message to {topic_path} with ID: {message_id}")
            return message_id
        except Exception as e:
            logger.error(f"Error publishing to Pub/Sub: {str(e)}")
            raise
