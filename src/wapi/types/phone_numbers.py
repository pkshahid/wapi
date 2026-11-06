"""Phone-number and registration types."""

from __future__ import annotations

from typing import Any

from .base import WapiModel

__all__ = ["HealthStatus", "PhoneNumber", "PhoneNumberInfo"]


class PhoneNumber(WapiModel):
    """One row of ``GET /{waba-id}/phone_numbers``."""

    id: str
    verified_name: str | None = None
    display_phone_number: str | None = None
    quality_rating: str | None = None
    code_verification_status: str | None = None
    platform_type: str | None = None
    throughput: dict[str, Any] | None = None
    webhook_configuration: dict[str, Any] | None = None
    last_onboarded_time: str | None = None
    is_official_business_account: bool | None = None
    account_mode: str | None = None
    messaging_limit_tier: str | None = None
    status: str | None = None


class HealthStatus(WapiModel):
    """Messaging health status summary (``health_status`` field)."""

    can_send_message: str | None = None
    entities: list[dict[str, Any]] | None = None


class PhoneNumberInfo(PhoneNumber):
    """``GET /{phone-number-id}`` — everything above plus more fields."""

    certificate: str | None = None
    name_status: str | None = None
    new_name_status: str | None = None
    search_visibility: str | None = None
    health_status: dict[str, Any] | None = None
    eligibility_for_api_business_global_search: str | None = None
