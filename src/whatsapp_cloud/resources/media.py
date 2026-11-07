"""Media endpoints: upload, info, download, delete, resumable upload."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from whatsapp_cloud.http import ApiRequest, Files, clean_params
from whatsapp_cloud.types.media import MediaInfo, MediaUploadResult

from .base import AsyncResource, Resource

__all__ = ["AsyncMedia", "Media"]


def _upload_spec(pnid: str, file: Any, mime_type: str | None) -> ApiRequest[MediaUploadResult]:
    name, content, guessed = Files.open(file)
    return ApiRequest(
        "POST",
        f"{pnid}/media",
        data={"messaging_product": "whatsapp", "type": mime_type or guessed},
        files={"file": (name, content, mime_type or guessed or "application/octet-stream")},
        into=MediaUploadResult.model_validate,
    )


def _info_spec(media_id: str, pnid: str | None) -> ApiRequest[MediaInfo]:
    return ApiRequest(
        "GET",
        media_id,
        params=clean_params({"phone_number_id": pnid}),
        into=MediaInfo.model_validate,
    )


def _delete_spec(media_id: str, pnid: str | None) -> ApiRequest[dict[str, Any]]:
    return ApiRequest("DELETE", media_id, params=clean_params({"phone_number_id": pnid}))


class Media(Resource):
    """``/{phone-number-id}/media`` + ``/{media-id}`` operations."""

    def upload(
        self,
        file: Any,
        *,
        mime_type: str | None = None,
        phone_number_id: str | None = None,
    ) -> MediaUploadResult:
        """Upload media for use in messages.

        ``file`` accepts a path, ``bytes``, or an open binary file.
        Returns an object with a media ``id`` (valid ~30 days).
        """
        return self._req(_upload_spec(self._pnid(phone_number_id), file, mime_type))

    def get(self, media_id: str, *, phone_number_id: str | None = None) -> MediaInfo:
        """Retrieve a media object — includes a temporary download ``url``."""
        return self._req(_info_spec(media_id, phone_number_id))

    def delete(self, media_id: str, *, phone_number_id: str | None = None) -> bool:
        body = self._req(_delete_spec(media_id, phone_number_id))
        return bool(body.get("success"))

    def download(
        self,
        media: str | MediaInfo,
        dest: str | Path | None = None,
        *,
        phone_number_id: str | None = None,
    ) -> bytes | Path:
        """Download media bytes.

        ``media`` may be a media ID, a ``MediaInfo``, or a raw download URL.
        When ``dest`` is given the file is written and its path returned.
        """
        url: str | None
        if isinstance(media, MediaInfo):
            url = media.url
        elif media.startswith("http"):
            url = media
        else:
            url = self.get(media, phone_number_id=phone_number_id).url
        if not url:
            raise ValueError("no download URL available for this media")
        data = self._c._download(url)
        if dest is not None:
            path = Path(dest)
            path.write_bytes(data)
            return path
        return data

    def resumable_upload(
        self,
        file: Any,
        *,
        mime_type: str | None = None,
        app_id: str | None = None,
    ) -> str:
        """Resumable Upload API → an asset *handle* (``h:…``).

        Required for template header media and profile pictures.
        ``app_id`` defaults to the client's ``app_id``.
        """
        return self._c._resumable_upload(file, mime_type=mime_type, app_id=app_id)


class AsyncMedia(AsyncResource):
    """Async variant of :class:`Media`."""

    async def upload(
        self, file: Any, *, mime_type: str | None = None, phone_number_id: str | None = None
    ) -> MediaUploadResult:
        return await self._req(_upload_spec(self._pnid(phone_number_id), file, mime_type))

    async def get(self, media_id: str, *, phone_number_id: str | None = None) -> MediaInfo:
        return await self._req(_info_spec(media_id, phone_number_id))

    async def delete(self, media_id: str, *, phone_number_id: str | None = None) -> bool:
        body = await self._req(_delete_spec(media_id, phone_number_id))
        return bool(body.get("success"))

    async def download(
        self,
        media: str | MediaInfo,
        dest: str | Path | None = None,
        *,
        phone_number_id: str | None = None,
    ) -> bytes | Path:
        url: str | None
        if isinstance(media, MediaInfo):
            url = media.url
        elif media.startswith("http"):
            url = media
        else:
            url = (await self.get(media, phone_number_id=phone_number_id)).url
        if not url:
            raise ValueError("no download URL available for this media")
        data = await self._c._download(url)
        if dest is not None:
            path = Path(dest)
            path.write_bytes(data)
            return path
        return data

    async def resumable_upload(
        self, file: Any, *, mime_type: str | None = None, app_id: str | None = None
    ) -> str:
        return await self._c._resumable_upload(file, mime_type=mime_type, app_id=app_id)
