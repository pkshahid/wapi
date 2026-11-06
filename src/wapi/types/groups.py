"""Groups API types."""

from __future__ import annotations

from typing import Any, Literal

from .base import WapiModel

__all__ = ["Group", "GroupCreated", "JoinApprovalMode", "JoinRequest"]

JoinApprovalMode = Literal["approval_required", "auto_approve"]


class Group(WapiModel):
    """A WhatsApp group."""

    id: str
    subject: str | None = None
    description: str | None = None
    creation_timestamp: int | None = None
    invite_link: str | None = None
    join_approval_mode: str | None = None
    is_locked: bool | None = None
    participants: list[dict[str, Any]] | None = None


class GroupCreated(WapiModel):
    """Response of ``POST /{phone-number-id}/groups``."""

    id: str


class JoinRequest(WapiModel):
    """A pending ``/{group-id}/join_requests`` entry."""

    id: str
    phone_number: str | None = None
    user: str | None = None
    request_time: int | None = None
