from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import BinaryIO

import boto3
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import BotoCoreError
from botocore.exceptions import ClientError
from django.conf import settings

logger = logging.getLogger(__name__)


# =========================================================
# Exceptions
# =========================================================

class S3StorageError(Exception):
    """Base S3 storage exception."""


class S3UploadError(S3StorageError):
    """Upload failure."""


class S3DownloadError(S3StorageError):
    """Download failure."""


class S3DeleteError(S3StorageError):
    """Delete failure."""


# =========================================================
# Settings
# =========================================================

@dataclass(slots=True)
class S3StorageSettings:
    bucket: str
    endpoint_url: str | None
    access_key: str
    secret_key: str
    region: str
    public_base_url: str | None
    use_ssl: bool
    verify_ssl: bool
    presign_expiry: int
    connect_timeout: int
    read_timeout: int
    max_pool_connections: int

    @classmethod
    def from_django(cls) -> "S3StorageSettings":
        cfg = getattr(settings, "WAY_STORAGE", {})
        s3 = cfg.get("s3", {})

        return cls(
            bucket=s3["bucket"],
            endpoint_url=s3.get("endpoint_url"),
            access_key=s3["access_key"],
            secret_key=s3["secret_key"],
            region=s3.get("region", "auto"),
            public_base_url=s3.get("public_base_url"),
            use_ssl=s3.get("use_ssl", True),
            verify_ssl=s3.get("verify_ssl", True),
            presign_expiry=s3.get("presign_expiry", 3600),
            connect_timeout=s3.get("connect_timeout", 5),
            read_timeout=s3.get("read_timeout", 30),
            max_pool_connections=s3.get("max_pool_connections", 50),
        )


# =========================================================
# Main Storage
# =========================================================

class S3Storage:
    """
    Generic S3-compatible object storage.

    Supports:
    - AWS S3
    - MinIO
    - Cloudflare R2
    - DigitalOcean Spaces
    """

    def __init__(
        self,
        config: S3StorageSettings | None = None,
    ) -> None:
        self.config = config or S3StorageSettings.from_django()
        self._client: BaseClient | None = None

    # -----------------------------------------------------
    # Client
    # -----------------------------------------------------

    @property
    def client(self) -> BaseClient:
        if self._client is None:
            logger.info("Initializing S3 storage client")

            self._client = boto3.client(
                "s3",
                endpoint_url=self.config.endpoint_url,
                region_name=self.config.region,
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                verify=self.config.verify_ssl,
                use_ssl=self.config.use_ssl,
                config=Config(
                    connect_timeout=self.config.connect_timeout,
                    read_timeout=self.config.read_timeout,
                    max_pool_connections=self.config.max_pool_connections,
                    retries={
                        "max_attempts": 5,
                        "mode": "adaptive",
                    },
                ),
            )

        return self._client

    # -----------------------------------------------------
    # Path helpers
    # -----------------------------------------------------

    def normalize_key(self, key: str | Path) -> str:
        return str(key).strip("/")

    def public_url(self, key: str) -> str | None:
        if not self.config.public_base_url:
            return None

        key = self.normalize_key(key)
        return f"{self.config.public_base_url.rstrip('/')}/{key}"

    # -----------------------------------------------------
    # Upload
    # -----------------------------------------------------

    def upload_bytes(
        self,
        key: str,
        data: bytes,
        *,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> str:
        key = self.normalize_key(key)

        extra: dict[str, Any] = {}

        if content_type:
            extra["ContentType"] = content_type

        if metadata:
            extra["Metadata"] = metadata

        try:
            self.client.put_object(
                Bucket=self.config.bucket,
                Key=key,
                Body=data,
                **extra,
            )

            logger.info("S3 uploaded %s", key)
            return key

        except (ClientError, BotoCoreError) as exc:
            logger.exception("Upload failed")
            raise S3UploadError(str(exc)) from exc

    def upload_file(
        self,
        key: str,
        file_path: str | Path,
        *,
        content_type: str | None = None,
    ) -> str:
        key = self.normalize_key(key)

        extra: dict[str, Any] = {}

        if content_type:
            extra["ContentType"] = content_type

        try:
            self.client.upload_file(
                str(file_path),
                self.config.bucket,
                key,
                ExtraArgs=extra or None,
            )

            logger.info("S3 uploaded file %s", key)
            return key

        except (ClientError, BotoCoreError) as exc:
            logger.exception("Upload file failed")
            raise S3UploadError(str(exc)) from exc

    def upload_stream(
        self,
        key: str,
        stream: BinaryIO,
        *,
        content_type: str | None = None,
    ) -> str:
        key = self.normalize_key(key)

        extra: dict[str, Any] = {}

        if content_type:
            extra["ContentType"] = content_type

        try:
            self.client.upload_fileobj(
                stream,
                self.config.bucket,
                key,
                ExtraArgs=extra or None,
            )

            logger.info("S3 uploaded stream %s", key)
            return key

        except (ClientError, BotoCoreError) as exc:
            logger.exception("Upload stream failed")
            raise S3UploadError(str(exc)) from exc

    # -----------------------------------------------------
    # Read
    # -----------------------------------------------------

    def exists(self, key: str) -> bool:
        key = self.normalize_key(key)

        try:
            self.client.head_object(
                Bucket=self.config.bucket,
                Key=key,
            )
            return True

        except ClientError:
            return False

    def read_bytes(self, key: str) -> bytes:
        key = self.normalize_key(key)

        try:
            obj = self.client.get_object(
                Bucket=self.config.bucket,
                Key=key,
            )

            return obj["Body"].read()

        except (ClientError, BotoCoreError) as exc:
            logger.exception("Read failed")
            raise S3DownloadError(str(exc)) from exc

    def download_file(
        self,
        key: str,
        destination: str | Path,
    ) -> Path:
        key = self.normalize_key(key)
        path = Path(destination)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            self.client.download_file(
                self.config.bucket,
                key,
                str(path),
            )

            return path

        except (ClientError, BotoCoreError) as exc:
            logger.exception("Download failed")
            raise S3DownloadError(str(exc)) from exc

    # -----------------------------------------------------
    # Delete
    # -----------------------------------------------------

    def delete(self, key: str) -> bool:
        key = self.normalize_key(key)

        try:
            self.client.delete_object(
                Bucket=self.config.bucket,
                Key=key,
            )

            logger.info("Deleted %s", key)
            return True

        except (ClientError, BotoCoreError) as exc:
            logger.exception("Delete failed")
            raise S3DeleteError(str(exc)) from exc

    # -----------------------------------------------------
    # Listing
    # -----------------------------------------------------

    def list(
        self,
        prefix: str = "",
        *,
        limit: int = 100,
    ) -> list[str]:
        prefix = self.normalize_key(prefix)

        try:
            result = self.client.list_objects_v2(
                Bucket=self.config.bucket,
                Prefix=prefix,
                MaxKeys=limit,
            )

            return [
                item["Key"]
                for item in result.get("Contents", [])
            ]

        except (ClientError, BotoCoreError):
            logger.exception("List failed")
            return []

    # -----------------------------------------------------
    # Presigned URLs
    # -----------------------------------------------------

    def presigned_get_url(
        self,
        key: str,
        *,
        expires_in: int | None = None,
    ) -> str:
        key = self.normalize_key(key)

        return self.client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.config.bucket,
                "Key": key,
            },
            ExpiresIn=expires_in or self.config.presign_expiry,
        )

    def presigned_put_url(
        self,
        key: str,
        *,
        expires_in: int | None = None,
    ) -> str:
        key = self.normalize_key(key)

        return self.client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self.config.bucket,
                "Key": key,
            },
            ExpiresIn=expires_in or self.config.presign_expiry,
        )

    # -----------------------------------------------------
    # Health
    # -----------------------------------------------------

    def health(self) -> dict[str, Any]:
        try:
            self.client.head_bucket(
                Bucket=self.config.bucket,
            )

            return {
                "backend": "s3",
                "bucket": self.config.bucket,
                "healthy": True,
            }

        except Exception as exc:
            logger.exception("S3 health failed")

            return {
                "backend": "s3",
                "bucket": self.config.bucket,
                "healthy": False,
                "error": str(exc),
            }