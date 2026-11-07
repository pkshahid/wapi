"""Response types for the messages endpoints."""

from __future__ import annotations

from pydantic import Field

from .base import WapiModel

__all__ = ["MessageContact", "MessageResponse", "SentMessage"]


class MessageContact(WapiModel):
    """Echoed recipient info in a send response."""

    input: str
    wa_id: str
    wa_id_v2: str | None = None


class SentMessage(WapiModel):
    """One sent-message handle."""

    id: str
    message_status: str | None = None


class MessageResponse(WapiModel):
    """Response of ``POST /{phone-number-id}/messages``."""

    messaging_product: str | None = None
    contacts: list[MessageContact] = Field(default_factory=list)
    messages: list[SentMessage] = Field(default_factory=list)

    @property
    def message_id(self) -> str | None:
        """Convenience: ID of the first returned message."""
        return self.messages[0].id if self.messages else None
