"""Media API response types."""

from __future__ import annotations

from .base import WapiModel

__all__ = ["MediaInfo", "MediaUploadResult"]


class MediaUploadResult(WapiModel):
    """Response of ``POST /{phone-number-id}/media`` — just the new ID."""

    id: str


class MediaInfo(WapiModel):
    """Response of ``GET /{media-id}``."""

    id: str | None = None
    messaging_product: str | None = None
    url: str | None = None
    mime_type: str | None = None
    sha256: str | None = None
    file_size: int | None = None
