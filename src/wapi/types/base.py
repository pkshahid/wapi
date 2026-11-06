"""Shared base types for API responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

__all__ = ["SuccessResponse", "WapiModel"]


class WapiModel(BaseModel):
    """Base model: tolerate unknown fields so Meta can add keys freely."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class SuccessResponse(WapiModel):
    """The ubiquitous ``{"success": true}`` envelope."""

    success: bool = False
    raw: dict[str, Any] | None = None
