"""Business profile, commerce, compliance, and QR-code types."""

from __future__ import annotations

from typing import Any

from .base import WapiModel

__all__ = [
    "BlockedUser",
    "BusinessProfile",
    "CommerceSettings",
    "ComplianceInfo",
    "QRCode",
]


class BusinessProfile(WapiModel):
    """``whatsapp_business_profile`` node contents."""

    about: str | None = None
    address: str | None = None
    description: str | None = None
    email: str | None = None
    profile_picture_url: str | None = None
    websites: list[str] | None = None
    vertical: str | None = None
    messaging_product: str | None = None


class CommerceSettings(WapiModel):
    """``whatsapp_commerce_settings`` node."""

    id: str | None = None
    is_cart_enabled: bool | None = None
    is_catalog_visible: bool | None = None


class ComplianceInfo(WapiModel):
    """``business_compliance_info`` node (India regulatory info)."""

    entity_name: str | None = None
    entity_type: str | None = None
    entity_type_custom: str | None = None
    is_registered: bool | None = None
    grievance_officer_details: dict[str, Any] | None = None
    customer_care_details: dict[str, Any] | None = None


class QRCode(WapiModel):
    """A ``message_qrdls`` QR-code entry."""

    code: str
    prefilled_message: str | None = None
    deep_link_url: str | None = None
    qr_image_url: str | None = None


class BlockedUser(WapiModel):
    """A ``block_users`` entry."""

    user: str
    created_time: str | None = None
