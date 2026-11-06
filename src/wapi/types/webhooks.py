"""Typed models for inbound webhook payloads.

Structure: ``{object, entry: [{id, changes: [{field, value}]}]}``.
The ``value`` object differs per ``field`` — see ``wapi.webhooks.parser``
which dispatches into the event types in ``wapi.webhooks.events``.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from .base import WapiModel

__all__ = [
    "Change",
    "ConversationInfo",
    "Entry",
    "InboundIdentity",
    "InboundLocation",
    "InboundMedia",
    "InboundMessage",
    "InboundReferral",
    "InboundText",
    "InteractiveReply",
    "MessageStatus",
    "PricingInfo",
    "StatusError",
    "WebhookContact",
    "WebhookMetadata",
    "WebhookPayload",
]


class WebhookPayload(WapiModel):
    """Top-level body POSTed to the webhook endpoint."""

    object: str
    entry: list[Entry]


class Entry(WapiModel):
    id: str
    changes: list[Change]


class Change(WapiModel):
    field: str
    value: dict[str, Any]


# --- messages field --------------------------------------------------------


class WebhookMetadata(WapiModel):
    display_phone_number: str | None = None
    phone_number_id: str | None = None


class WebhookContact(WapiModel):
    """Sender info attached to inbound messages."""

    wa_id: str
    profile: dict[str, Any] | None = None

    @property
    def name(self) -> str | None:
        return (self.profile or {}).get("name")


class InboundMedia(WapiModel):
    """image/audio/video/document/sticker media descriptor."""

    id: str | None = None
    mime_type: str | None = None
    sha256: str | None = None
    caption: str | None = None
    filename: str | None = None  # documents only
    voice: bool | None = None  # audio: True if voice note


class InboundText(WapiModel):
    body: str


class InboundLocation(WapiModel):
    latitude: float
    longitude: float
    name: str | None = None
    address: str | None = None


class InteractiveReply(WapiModel):
    """interactive replies: button_reply / list_reply / nfm_reply."""

    type: str
    button_reply: dict[str, Any] | None = None
    list_reply: dict[str, Any] | None = None
    nfm_reply: dict[str, Any] | None = None


class InboundReferral(WapiModel):
    """Referral data (click-to-WhatsApp ads, QR codes)."""

    source_url: str | None = None
    source_type: str | None = None
    source_id: str | None = None
    headline: str | None = None
    body: str | None = None
    media_type: str | None = None
    video_url: str | None = None
    image_url: str | None = None
    thumbnail_url: str | None = None
    ctwa_clid: str | None = None


class InboundIdentity(WapiModel):
    """User identity-change marker (``value.identity``)."""

    acknowledged: str | None = None
    hash: str | None = None


class InboundContext(WapiModel):
    """Present when the inbound message quotes a previous one."""

    from_: str | None = Field(default=None, alias="from")
    id: str | None = None
    referred_product: dict[str, Any] | None = None
    forwarded: bool | None = None
    frequently_forwarded: bool | None = None


class InboundMessage(WapiModel):
    """One entry of ``value.messages[]``.

    ``type`` discriminates which content attribute is populated:
    text/image/audio/video/document/sticker/location/contacts/reaction/
    interactive/button/order/system/referral/unknown/group_*.
    """

    from_: str = Field(default="", alias="from")
    id: str = ""
    timestamp: str | None = None
    type: str
    text: InboundText | None = None
    image: InboundMedia | None = None
    audio: InboundMedia | None = None
    video: InboundMedia | None = None
    document: InboundMedia | None = None
    sticker: InboundMedia | None = None
    location: InboundLocation | None = None
    contacts: list[dict[str, Any]] | None = None
    reaction: dict[str, Any] | None = None
    interactive: InteractiveReply | None = None
    button: dict[str, Any] | None = None
    order: dict[str, Any] | None = None
    system: dict[str, Any] | None = None
    referral: InboundReferral | dict[str, Any] | None = None
    context: InboundContext | None = None
    errors: list[dict[str, Any]] | None = None
    group_id: str | None = None


# --- statuses --------------------------------------------------------------


class ConversationInfo(WapiModel):
    id: str | None = None
    origin: dict[str, Any] | None = None
    expiration_timestamp: str | None = None

    @property
    def origin_type(self) -> str | None:
        return (self.origin or {}).get("type")


class PricingInfo(WapiModel):
    billable: bool | None = None
    pricing_model: str | None = None
    category: str | None = None
    type: str | None = None


class StatusError(WapiModel):
    code: int | None = None
    title: str | None = None
    message: str | None = None
    href: str | None = None
    error_data: dict[str, Any] | None = None

    @property
    def details(self) -> str | None:
        return (self.error_data or {}).get("details")


class MessageStatus(WapiModel):
    """One entry of ``value.statuses[]``."""

    id: str
    status: Literal["sent", "delivered", "read", "failed", "warning"] | str
    timestamp: str | None = None
    recipient_id: str | None = None
    recipient_type: str | None = None
    conversation: ConversationInfo | None = None
    pricing: PricingInfo | None = None
    errors: list[StatusError] | None = None
    biz_opaque_callback_data: str | None = None
    type: str | None = None
