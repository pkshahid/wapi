"""Calling API types."""

from __future__ import annotations

from typing import Any, Literal

from .base import WapiModel

__all__ = [
    "AvailableCallAction",
    "CallAction",
    "CallActionLimit",
    "CallPermission",
    "CallPermissionStatus",
    "CallResult",
]

CallAction = Literal["connect", "pre_accept", "accept", "reject", "terminate", "media_update"]
CallPermissionStatus = Literal["granted", "pending", "denied", "expired"]


class CallActionLimit(WapiModel):
    time_period: str | None = None
    current_usage: int | None = None
    max_allowed: int | None = None
    limit_expiration_time: int | None = None


class AvailableCallAction(WapiModel):
    action_name: str | None = None
    can_perform_action: bool | None = None
    limits: list[CallActionLimit] | None = None


class _Permission(WapiModel):
    status: CallPermissionStatus | str | None = None
    expiration_time: int | None = None


class CallPermission(WapiModel):
    """Response of ``GET /{phone-number-id}/call_permissions``."""

    messaging_product: str | None = None
    permission: _Permission | None = None
    actions: list[AvailableCallAction] | None = None

    @property
    def status(self) -> str | None:
        return self.permission.status if self.permission else None


class CallResult(WapiModel):
    """Response of ``POST /{phone-number-id}/calls``."""

    messaging_product: str | None = None
    calls: list[dict[str, Any]] | None = None
    success: bool | None = None

    @property
    def call_id(self) -> str | None:
        if self.calls:
            first = self.calls[0]
            return first.get("id")
        return None
