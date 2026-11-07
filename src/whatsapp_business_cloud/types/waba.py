"""WABA node, analytics, and schedule types."""

from __future__ import annotations

from typing import Any

from .base import WapiModel

__all__ = ["Activity", "AnalyticsPoint", "Schedule", "SubscribedApp", "Waba"]


class Waba(WapiModel):
    """``GET /{waba-id}`` — account node details."""

    id: str
    name: str | None = None
    currency: str | None = None
    timezone_id: str | None = None
    message_template_namespace: str | None = None
    account_review_status: str | None = None
    business_capabilities: dict[str, Any] | None = None
    analytics: dict[str, Any] | None = None
    template_analytics: dict[str, Any] | None = None
    health_status: dict[str, Any] | None = None
    on_behalf_of_business_info: dict[str, Any] | None = None
    primary_business_location: str | None = None
    is_enabled_for_insights: bool | None = None


class AnalyticsPoint(WapiModel):
    """One datapoint inside an ``analytics`` response."""

    start: int | None = None
    end: int | None = None
    sent: int | None = None
    delivered: int | None = None
    cost: dict[str, Any] | None = None
    conversation: int | None = None
    phone_number: str | None = None
    granularity: str | None = None


class Activity(WapiModel):
    """A ``/{waba-id}/activities`` audit entry."""

    event_type: str | None = None
    event_time: int | None = None
    extra_info: dict[str, Any] | None = None


class Schedule(WapiModel):
    """A scheduled template campaign (``/{waba-id}/schedules``)."""

    id: str | None = None
    name: str | None = None
    description: str | None = None
    delivery_time: int | None = None
    hsm_id: str | None = None
    audience_id: str | None = None
    waba_cs_id: str | None = None
    status: str | None = None


class SubscribedApp(WapiModel):
    """An app subscribed to a WABA's webhooks."""

    whatsapp_business_api_data: dict[str, Any] | None = None
    id: str | None = None
    link: str | None = None
    name: str | None = None
