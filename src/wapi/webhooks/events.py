"""Typed webhook events produced by :func:`wapi.webhooks.parse`.

Every event carries the ``field`` that produced it, the WABA ``id`` (entry id),
and the raw ``value`` dict. Subclasses add typed accessors for known fields.
Pattern-match on them::

    for event in parse(body):
        match event:
            case InboundMessages() as m:
                for msg in m.messages: ...
            case StatusUpdates() as s:
                for st in s.statuses: ...
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from wapi.types.webhooks import (
    InboundMessage,
    MessageStatus,
    StatusError,
    WebhookContact,
    WebhookMetadata,
)

__all__ = [
    "AccountAlert",
    "AccountReviewUpdate",
    "AccountUpdate",
    "BusinessCapabilityUpdate",
    "CallEvent",
    "GroupMessage",
    "History",
    "InboundMessages",
    "MessagingHandover",
    "PaymentConfigurationUpdate",
    "PhoneNumberNameUpdate",
    "PhoneNumberQualityUpdate",
    "Security",
    "SmbAppStateSync",
    "SmbMessageEcho",
    "StatusUpdates",
    "TemplateCategoryUpdate",
    "TemplateComponentsUpdate",
    "TemplateQualityUpdate",
    "TemplateStatusUpdate",
    "UnknownEvent",
    "UserPreferences",
    "WebhookEvent",
]


@dataclass
class WebhookEvent:
    """Base class — one ``entry[].changes[]`` item, typed."""

    field: str
    waba_id: str
    value: dict[str, Any]


@dataclass
class InboundMessages(WebhookEvent):
    """``messages`` change containing inbound user messages."""

    messages: list[InboundMessage] = field(default_factory=list)
    contacts: list[WebhookContact] = field(default_factory=list)
    metadata: WebhookMetadata | None = None

    @property
    def sender_phone(self) -> str | None:
        return self.messages[0].from_ if self.messages else None


@dataclass
class StatusUpdates(WebhookEvent):
    """``messages`` change containing delivery statuses."""

    statuses: list[MessageStatus] = field(default_factory=list)
    metadata: WebhookMetadata | None = None

    @property
    def failed(self) -> list[StatusError]:
        """All errors across failed statuses."""
        return [e for s in self.statuses if s.status == "failed" for e in (s.errors or [])]


@dataclass
class TemplateStatusUpdate(WebhookEvent):
    """Template approved/rejected/paused etc."""

    @property
    def message_template_id(self) -> int | None:
        return self.value.get("message_template_id")

    @property
    def message_template_name(self) -> str | None:
        return self.value.get("message_template_name")

    @property
    def event(self) -> str | None:
        return self.value.get("event")

    @property
    def reason(self) -> str | None:
        return self.value.get("reason")


@dataclass
class TemplateQualityUpdate(WebhookEvent):
    """Template quality-score change."""


@dataclass
class TemplateComponentsUpdate(WebhookEvent):
    """Template component content changed (e.g. button URL edited)."""


@dataclass
class TemplateCategoryUpdate(WebhookEvent):
    """Template re-categorized by Meta."""


@dataclass
class AccountUpdate(WebhookEvent):
    """WABA-level account updates (ban, review, restriction)."""

    @property
    def event(self) -> str | None:
        return self.value.get("event")


@dataclass
class AccountAlert(WebhookEvent):
    pass


@dataclass
class AccountReviewUpdate(WebhookEvent):
    pass


@dataclass
class PhoneNumberNameUpdate(WebhookEvent):
    """Display-name review outcome."""

    @property
    def display_phone_number(self) -> str | None:
        return self.value.get("display_phone_number")

    @property
    def decision(self) -> str | None:
        return self.value.get("decision")


@dataclass
class PhoneNumberQualityUpdate(WebhookEvent):
    """Quality-rating or messaging-limit change."""

    @property
    def event(self) -> str | None:
        return self.value.get("event")


@dataclass
class BusinessCapabilityUpdate(WebhookEvent):
    pass


@dataclass
class History(WebhookEvent):
    """Chat-history sync chunk (coexistence/onboarding)."""


@dataclass
class UserPreferences(WebhookEvent):
    """User marketing-preference (opt-in/out) updates."""

    @property
    def detail(self) -> str | None:
        return self.value.get("detail")


@dataclass
class MessagingHandover(WebhookEvent):
    """Conversation thread-control handover between apps/partners."""


@dataclass
class SmbAppStateSync(WebhookEvent):
    """Coexistence state-sync (WhatsApp Business app contacts/chats)."""


@dataclass
class SmbMessageEcho(WebhookEvent):
    """Message echoes for coexistence (sent from the Business app)."""

    message_echoes: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Security(WebhookEvent):
    """Security notifications (identity changes, etc.)."""


@dataclass
class PaymentConfigurationUpdate(WebhookEvent):
    pass


@dataclass
class CallEvent(WebhookEvent):
    """``calls`` webhook — SDP offers/answers, connects, terminates."""

    calls: list[dict[str, Any]] = field(default_factory=list)
    metadata: WebhookMetadata | None = None


@dataclass
class GroupMessage(WebhookEvent):
    """Group-related message events."""


@dataclass
class UnknownEvent(WebhookEvent):
    """Fallback for fields wapi doesn't model yet — ``value`` stays raw."""
