"""Message template types."""

from __future__ import annotations

from typing import Any, Literal

from .base import WapiModel

__all__ = [
    "QualityScore",
    "Template",
    "TemplateCategory",
    "TemplateComponent",
    "TemplateCreated",
    "TemplateStatus",
]

TemplateCategory = Literal["AUTHENTICATION", "MARKETING", "UTILITY"]
TemplateStatus = Literal[
    "APPROVED",
    "PENDING",
    "IN_APPEAL",
    "REJECTED",
    "PAUSED",
    "DISABLED",
    "PENDING_DELETION",
    "DELETED",
    "LIMIT_EXCEEDED",
    "ARCHIVED",
]
QualityScore = Literal["GREEN", "YELLOW", "RED", "UNKNOWN", "PENDING"]


class TemplateComponent(WapiModel):
    """A HEADER / BODY / FOOTER / BUTTONS / CAROUSEL / LIMITED_TIME_OFFER component.

    ``example`` and format-specific keys vary widely, so this model stays
    permissive — build components with the helpers in ``whatsapp_business_cloud.builders``.
    """

    type: str
    format: str | None = None
    text: str | None = None
    buttons: list[dict[str, Any]] | None = None
    example: dict[str, Any] | None = None
    cards: list[dict[str, Any]] | None = None
    limited_time_offer: dict[str, Any] | None = None


class Template(WapiModel):
    """A message template as returned by the Message Template API."""

    id: str
    name: str | None = None
    category: str | None = None
    language: str | None = None
    status: str | None = None
    parameter_format: str | None = None
    components: list[TemplateComponent] | None = None
    rejected_reason: str | None = None
    quality_score: dict[str, Any] | str | None = None
    library_template_name: str | None = None
    previous_category: str | None = None
    correct_category: str | None = None
    message_send_ttl_seconds: int | None = None
    sub_category: str | None = None


class TemplateCreated(WapiModel):
    """Response of ``POST /{waba-id}/message_templates``."""

    id: str
    status: str | None = None
    category: str | None = None
