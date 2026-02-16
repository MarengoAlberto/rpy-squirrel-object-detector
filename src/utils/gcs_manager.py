from __future__ import annotations

import mimetypes
import os
from dataclasses import dataclass
from typing import Optional, Union

from google.cloud import storage


BytesOrPath = Union[bytes, str]


@dataclass
class GCSClient:

    bucket_name: str
    project_id: Optional[str] = None

    def __post_init__(self) -> None:
        self._client = storage.Client(project=self.project_id)
        self._bucket = self._client.bucket(self.bucket_name)

    def save_image(
        self,
        source: BytesOrPath,
        destination_blob_name: str,
        content_type: Optional[str] = None,
        public: bool = False,
        cache_control: Optional[str] = "public, max-age=3600",
    ) -> str:
        """
        Upload an image to GCS. Returns gs://... URI.
        """
        return self._upload(
            source=source,
            destination_blob_name=destination_blob_name,
            content_type=content_type or self._guess_content_type(destination_blob_name, fallback="image/jpeg"),
            public=public,
            cache_control=cache_control,
        )

    def save_video(
        self,
        source: BytesOrPath,
        destination_blob_name: str,
        content_type: Optional[str] = None,
        public: bool = False,
        cache_control: Optional[str] = "public, max-age=3600",
    ) -> str:
        """
        Upload a video to GCS. Returns gs://... URI.
        """
        return self._upload(
            source=source,
            destination_blob_name=destination_blob_name,
            content_type=content_type or self._guess_content_type(destination_blob_name, fallback="video/mp4"),
            public=public,
            cache_control=cache_control,
        )

    def save_file(
        self,
        source: BytesOrPath,
        destination_blob_name: str,
        content_type: Optional[str] = None,
        public: bool = False,
        cache_control: Optional[str] = None,
    ) -> str:
        """
        Generic upload for any file type. Returns gs://... URI.
        """
        return self._upload(
            source=source,
            destination_blob_name=destination_blob_name,
            content_type=content_type or self._guess_content_type(destination_blob_name, fallback="application/octet-stream"),
            public=public,
            cache_control=cache_control,
        )

    def _upload(
        self,
        source: BytesOrPath,
        destination_blob_name: str,
        content_type: str,
        public: bool,
        cache_control: Optional[str],
    ) -> str:
        blob = self._bucket.blob(destination_blob_name)

        if cache_control:
            blob.cache_control = cache_control

        # Upload from local path or from bytes
        if isinstance(source, str):
            if not os.path.exists(source):
                raise FileNotFoundError(f"Local file not found: {source}")
            blob.upload_from_filename(source, content_type=content_type)
        elif isinstance(source, (bytes, bytearray)):
            blob.upload_from_string(bytes(source), content_type=content_type)
        else:
            raise TypeError("source must be a file path (str) or bytes")

        if public:
            blob.make_public()

        return f"gs://{self.bucket_name}/{destination_blob_name}"

    @staticmethod
    def _guess_content_type(name_or_path: str, fallback: str) -> str:
        # Guess based on filename extension
        ctype, _ = mimetypes.guess_type(name_or_path)
        return ctype or fallback