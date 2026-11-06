"""Flows management types."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from .base import WapiModel

__all__ = [
    "Flow",
    "FlowAsset",
    "FlowCategory",
    "FlowCreated",
    "FlowMigrationResult",
    "FlowPreview",
    "FlowStatus",
    "FlowValidationError",
]

FlowCategory = Literal[
    "SIGN_UP",
    "SIGN_IN",
    "APPOINTMENT_BOOKING",
    "LEAD_GENERATION",
    "CONTACT_US",
    "CUSTOMER_SUPPORT",
    "SURVEY",
    "OTHER",
]

FlowStatus = Literal["DRAFT", "PUBLISHED", "DEPRECATED", "BLOCKED", "THROTTLED"]


class FlowValidationError(WapiModel):
    """One entry of a flow's ``validation_errors`` list."""

    error: str | None = None
    error_type: str | None = None
    message: str | None = None
    line_start: int | None = None
    line_end: int | None = None
    column_start: int | None = None
    column_end: int | None = None
    pointers: list[dict[str, Any]] | None = None


class FlowPreview(WapiModel):
    preview_url: str
    expires_at: str | None = None


class Flow(WapiModel):
    """A WhatsApp Flow."""

    id: str
    name: str | None = None
    categories: list[str] | None = None
    status: str | None = None
    json_version: str | None = None
    data_api_version: str | None = None
    endpoint_uri: str | None = None
    preview: FlowPreview | None = None
    validation_errors: list[FlowValidationError] | None = None
    health_status: dict[str, Any] | None = None
    application: dict[str, Any] | None = None
    whatsapp_business_account: dict[str, Any] | None = None


class FlowCreated(WapiModel):
    """Response of ``POST /{waba-id}/flows``."""

    id: str
    success: bool | None = None
    validation_errors: list[FlowValidationError] | None = None


class FlowAsset(WapiModel):
    name: str | None = None
    asset_type: str | None = None
    download_url: str | None = None


class _MigratedFlow(WapiModel):
    source_name: str | None = None
    source_id: str | None = None
    migrated_id: str | None = None


class _FailedFlow(WapiModel):
    source_name: str | None = None
    error_code: str | None = None
    error_message: str | None = None


class FlowMigrationResult(WapiModel):
    """Response of ``POST /{waba-id}/migrate_flows``."""

    migrated_flows: list[_MigratedFlow] = Field(default_factory=list)
    failed_flows: list[_FailedFlow] = Field(default_factory=list)
