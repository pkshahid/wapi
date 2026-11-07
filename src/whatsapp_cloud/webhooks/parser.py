"""Parse raw webhook bodies into typed :class:`WebhookEvent` objects."""

from __future__ import annotations

import json
from typing import Any

from whatsapp_cloud.types.webhooks import (
    InboundMessage,
    MessageStatus,
    WebhookContact,
    WebhookMetadata,
    WebhookPayload,
)

from . import events as ev

__all__ = ["parse", "parse_change"]

# field name → event class (messages handled specially below).
_FIELD_MAP: dict[str, type[ev.WebhookEvent]] = {
    "message_template_status_update": ev.TemplateStatusUpdate,
    "message_template_quality_update": ev.TemplateQualityUpdate,
    "message_template_components_update": ev.TemplateComponentsUpdate,
    "template_category_update": ev.TemplateCategoryUpdate,
    "account_update": ev.AccountUpdate,
    "account_alerts": ev.AccountAlert,
    "account_review_update": ev.AccountReviewUpdate,
    "phone_number_name_update": ev.PhoneNumberNameUpdate,
    "phone_number_quality_update": ev.PhoneNumberQualityUpdate,
    "business_capability_update": ev.BusinessCapabilityUpdate,
    "history": ev.History,
    "user_preferences": ev.UserPreferences,
    "messaging_handovers": ev.MessagingHandover,
    "smb_app_state_sync": ev.SmbAppStateSync,
    "smb_message_echoes": ev.SmbMessageEcho,
    "security": ev.Security,
    "payment_configuration_update": ev.PaymentConfigurationUpdate,
    "calls": ev.CallEvent,
}


def parse(payload: dict[str, Any] | str | bytes) -> list[ev.WebhookEvent]:
    """Parse a webhook body into one typed event per change.

    A ``messages`` change produces an :class:`InboundMessages` event when it
    contains ``messages`` and a :class:`StatusUpdates` event when it contains
    ``statuses`` (they may both come from the same change).
    """
    if isinstance(payload, (str, bytes)):
        payload = json.loads(payload)
    body = WebhookPayload.model_validate(payload)
    out: list[ev.WebhookEvent] = []
    for entry in body.entry:
        for change in entry.changes:
            out.extend(parse_change(entry.id, change.field, change.value))
    return out


def parse_change(waba_id: str, field: str, value: dict[str, Any]) -> list[ev.WebhookEvent]:
    """Dispatch a single ``change`` into events."""
    if field in ("messages", "group_text_messages"):
        return _parse_messages(waba_id, field, value)
    cls = _FIELD_MAP.get(field, ev.UnknownEvent)
    return [cls(field=field, waba_id=waba_id, value=value)]


def _parse_messages(waba_id: str, field: str, value: dict[str, Any]) -> list[ev.WebhookEvent]:
    out: list[ev.WebhookEvent] = []
    metadata = None
    if isinstance(value.get("metadata"), dict):
        metadata = WebhookMetadata.model_validate(value["metadata"])

    if value.get("messages"):
        messages = [InboundMessage.model_validate(m) for m in value["messages"]]
        contacts = [WebhookContact.model_validate(c) for c in value.get("contacts") or []]
        out.append(
            ev.InboundMessages(
                field=field,
                waba_id=waba_id,
                value=value,
                messages=messages,
                contacts=contacts,
                metadata=metadata,
            )
        )
    if value.get("statuses"):
        statuses = [MessageStatus.model_validate(s) for s in value["statuses"]]
        out.append(
            ev.StatusUpdates(
                field=field,
                waba_id=waba_id,
                value=value,
                statuses=statuses,
                metadata=metadata,
            )
        )
    if value.get("message_echoes"):
        out.append(
            ev.SmbMessageEcho(
                field=field,
                waba_id=waba_id,
                value=value,
                message_echoes=list(value["message_echoes"]),
            )
        )
    if value.get("calls"):
        out.append(
            ev.CallEvent(
                field=field,
                waba_id=waba_id,
                value=value,
                calls=list(value["calls"]),
                metadata=metadata,
            )
        )
    if not out:
        out.append(ev.UnknownEvent(field=field, waba_id=waba_id, value=value))
    return out
