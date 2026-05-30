from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional

from sdk_python.resources.base import BaseResource


class FilesResource(BaseResource):
    """
    High-level file resource.

    Handles:
    - upload
    - multipart upload
    - download
    - presigned urls
    - metadata
    - delete
    """

    resource_name = "files"

    #
    # sync
    #

    def upload(
        self,
        source: str | Path,
        *,
        key: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        storage = self.storage

        if storage and hasattr(storage, "uploader"):
            return storage.uploader.upload(
                source,
                key=key,
                metadata=metadata,
            )

        return self._request(
            "POST",
            self.endpoint("upload"),
            json={
                "key": key,
                "metadata": dict(metadata or {}),
            },
        )

    def multipart_upload(
        self,
        source: str | Path,
        *,
        key: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        storage = self.storage

        if storage and hasattr(storage, "multipart"):
            return storage.multipart.upload(
                source,
                key=key,
                metadata=metadata,
            )

        return self._request(
            "POST",
            self.endpoint("multipart"),
            json={
                "key": key,
                "metadata": dict(metadata or {}),
            },
        )

    def download(
        self,
        key: str,
        *,
        destination: str | Path,
    ) -> Any:
        storage = self.storage

        if storage and hasattr(storage, "downloader"):
            return storage.downloader.download(
                key,
                destination=destination,
            )

        return self._request(
            "GET",
            self.endpoint(key, "download"),
        )

    def presign_upload(
        self,
        key: str,
        *,
        expires_in: int = 3600,
    ) -> Any:
        storage = self.storage

        if storage and hasattr(storage, "presigned"):
            return storage.presigned.upload(
                key,
                expires_in=expires_in,
            )

        return self._request(
            "POST",
            self.endpoint("presigned", "upload"),
            json={
                "key": key,
                "expires_in": expires_in,
            },
        )

    def presign_download(
        self,
        key: str,
        *,
        expires_in: int = 3600,
    ) -> Any:
        storage = self.storage

        if storage and hasattr(storage, "presigned"):
            return storage.presigned.download(
                key,
                expires_in=expires_in,
            )

        return self._request(
            "POST",
            self.endpoint("presigned", "download"),
            json={
                "key": key,
                "expires_in": expires_in,
            },
        )

    def get(
        self,
        key: str,
    ) -> Any:
        return self._request(
            "GET",
            self.endpoint(key),
        )

    def list(
        self,
        *,
        prefix: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> Any:
        return self._request(
            "GET",
            self.endpoint(),
            params={
                "prefix": prefix,
                "limit": limit,
                "cursor": cursor,
            },
        )

    def delete(
        self,
        key: str,
    ) -> Any:
        return self._request(
            "DELETE",
            self.endpoint(key),
        )

    #
    # async
    #

    async def aupload(
        self,
        source: str | Path,
        *,
        key: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        storage = self.storage

        if storage and hasattr(storage, "uploader"):
            uploader = storage.uploader

            if hasattr(uploader, "aupload"):
                return await uploader.aupload(
                    source,
                    key=key,
                    metadata=metadata,
                )

        return await self._arequest(
            "POST",
            self.endpoint("upload"),
            json={
                "key": key,
                "metadata": dict(metadata or {}),
            },
        )

    async def amultipart_upload(
        self,
        source: str | Path,
        *,
        key: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        storage = self.storage

        if storage and hasattr(storage, "multipart"):
            multipart = storage.multipart

            if hasattr(multipart, "upload"):
                result = multipart.upload(
                    source,
                    key=key,
                    metadata=metadata,
                )

                if hasattr(result, "__await__"):
                    return await result

                return result

        return await self._arequest(
            "POST",
            self.endpoint("multipart"),
            json={
                "key": key,
                "metadata": dict(metadata or {}),
            },
        )

    async def adownload(
        self,
        key: str,
        *,
        destination: str | Path,
    ) -> Any:
        storage = self.storage

        if storage and hasattr(storage, "downloader"):
            downloader = storage.downloader

            if hasattr(downloader, "download"):
                result = downloader.download(
                    key,
                    destination=destination,
                )

                if hasattr(result, "__await__"):
                    return await result

                return result

        return await self._arequest(
            "GET",
            self.endpoint(key, "download"),
        )

    async def apresign_upload(
        self,
        key: str,
        *,
        expires_in: int = 3600,
    ) -> Any:
        return await self._arequest(
            "POST",
            self.endpoint("presigned", "upload"),
            json={
                "key": key,
                "expires_in": expires_in,
            },
        )

    async def apresign_download(
        self,
        key: str,
        *,
        expires_in: int = 3600,
    ) -> Any:
        return await self._arequest(
            "POST",
            self.endpoint("presigned", "download"),
            json={
                "key": key,
                "expires_in": expires_in,
            },
        )

    async def aget(
        self,
        key: str,
    ) -> Any:
        return await self._arequest(
            "GET",
            self.endpoint(key),
        )

    async def alist(
        self,
        *,
        prefix: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> Any:
        return await self._arequest(
            "GET",
            self.endpoint(),
            params={
                "prefix": prefix,
                "limit": limit,
                "cursor": cursor,
            },
        )

    async def adelete(
        self,
        key: str,
    ) -> Any:
        return await self._arequest(
            "DELETE",
            self.endpoint(key),
        )