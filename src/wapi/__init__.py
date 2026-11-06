"""wapi — Python client for the WhatsApp Business Platform (Cloud API).

::

    from wapi import Client

    client = Client(
        access_token="EAAB...",
        phone_number_id="106540352242922",
        waba_id="102290129340398",
    )
    client.messages.send_text(to="15551234567", body="Hello!")

See ``docs/api-reference.md`` for the full endpoint coverage.
"""

from .client import AsyncClient, Client
from .exceptions import (
    ApiError,
    AuthError,
    CallError,
    MediaError,
    MessagingError,
    NotFoundError,
    PermissionError_,
    RateLimitError,
    RegistrationError,
    TemplateError,
    ValidationError,
    WebhookSignatureError,
    WhatsAppError,
)
from .http import ApiRequest, RetryPolicy
from .pagination import AsyncCursorIterator, CursorIterator, Page

__version__ = "0.1.0"

__all__ = [
    "ApiError",
    "ApiRequest",
    "AsyncClient",
    "AsyncCursorIterator",
    "AuthError",
    "CallError",
    "Client",
    "CursorIterator",
    "MediaError",
    "MessagingError",
    "NotFoundError",
    "Page",
    "PermissionError_",
    "RateLimitError",
    "RegistrationError",
    "RetryPolicy",
    "TemplateError",
    "ValidationError",
    "WebhookSignatureError",
    "WhatsAppError",
    "__version__",
]
