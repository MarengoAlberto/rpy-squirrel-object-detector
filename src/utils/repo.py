from dataclasses import dataclass
from typing import Union
from datetime import datetime

from .logging import get_logger, setup_logging
from .pubsub_manager import PubSubManager
from .gcs_manager import GCSClient
from .objects import ItemStats

logger = get_logger(__name__)
setup_logging()

@dataclass
class RepoManager:

    def __init__(self,
                 service_name: str,
                 gcs_client: GCSClient,
                 pubsub_client: PubSubManager,
                 push_frequency_threshold: int = 5,
                 target_label: str = "squirrel") -> None:

        self.service_name = service_name
        self.gcs_client = gcs_client
        self.pubsub_client = pubsub_client
        self.stats_by_id = dict[str, ItemStats] = {}
        self.push_frequency_threshold = push_frequency_threshold
        self.target_label = target_label

    def observe(self, id_: str, label: str) -> None:
        prev = self.stats_by_id.get(id_)
        if prev is None:
            self.stats_by_id[id_] = ItemStats(id=id_, label=label, frequency=1)
        else:
            # create a NEW object with frequency+1
            # keep existing label, or update it—your choice
            self.stats_by_id[id_] = ItemStats(id=id_, label=prev.label, frequency=prev.frequency + 1)

    def mark_as_pushed(self, id_: str) -> None:
        self.stats_by_id[id_].pushed = True

    def manage(self, detections, image_bytes, class_mapping) -> None:
        for detection in detections:
            label = class_mapping[int(detection.label)]
            id = detection.id
            self.observe(id_=id, label=label)
            if self.stats_by_id[id].frequency >= self.push_frequency_threshold and label == self.target_label and not self.stats_by_id[id].pushed:
                self.mark_as_pushed(id_=id)
                self.ship_detection(id=id, label=label, image_bytes=image_bytes)

    def ship_detection(self,
                       id: str,
                       label: str,
                       image_bytes: Union[bytes, None] = None,
                       video_bytes: Union[bytes, None] = None) -> None:

        message_data = dict()
        try:
            # Save image and video to GCS
            if image_bytes:
                image_uri = self.gcs_client.save_image(
                    source=image_bytes,
                    destination_blob_name=f"detections/{self.service_name}/image_{id}_{self._generate_timestamp()}.jpg",
                    public=True
                )
                message_data["image"] = image_uri
                message_data['detection_id'] = id
                message_data['label'] = label
                logger.info(f"Saved image to {image_uri}")
            if video_bytes:
                video_uri = self.gcs_client.save_video(
                    source=video_bytes,
                    destination_blob_name=f"detections/{self.service_name}/video_{id}_{self._generate_timestamp()}.mp4",
                    public=True
                )
                message_data["video"] = video_uri
                message_data['detection_id'] = id
                message_data['label'] = label
                logger.info(f"Saved video to {video_uri}")

            # Publish detection data to Pub/Sub
            topic_path = self.pubsub_client.publisher.topic_path(self.pubsub_client.project_id, self.pubsub_client.topic_name)
            self.pubsub_client.publish_detection(topic_path=topic_path, message_data=message_data, service_name=self.service_name)
        except Exception as e:
            logger.error(f"Error shipping detection: {str(e)}")
            raise

    def _generate_timestamp(self) -> str:
        return str(datetime.utcnow().isoformat() + "Z")
