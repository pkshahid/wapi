"""Exception hierarchy for the WhatsApp Business Platform.

Every non-2xx response from the Graph API raises an :class:`ApiError`
subclass. The subclass is chosen from the HTTP status and Meta's error
``code`` so callers can catch at whatever granularity they need::

    try:
        client.messages.send_text(to, "hi")
    except RateLimitError as e:
        time.sleep(e.retry_after or 1)
    except ApiError as e:
        log.error("Meta error %s (%s): %s", e.code, e.error_type, e)
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "ApiError",
    "AuthError",
    "CallError",
    "MediaError",
    "MessagingError",
    "NotFoundError",
    "PermissionError_",
    "RateLimitError",
    "RegistrationError",
    "TemplateError",
    "ValidationError",
    "WebhookSignatureError",
    "WhatsAppError",
]


class WhatsAppError(Exception):
    """Base class for every error raised by whatsapp_business_cloud."""


class ApiError(WhatsAppError):
    """An error response returned by the Graph API.

    Attributes mirror Meta's ``{"error": {...}}`` envelope.
    """

    def __init__(
        self,
        message: str,
        *,
        code: int | None = None,
        subcode: int | None = None,
        error_type: str | None = None,
        details: str | None = None,
        fbtrace_id: str | None = None,
        status_code: int | None = None,
        retry_after: float | None = None,
        raw: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.subcode = subcode
        self.error_type = error_type
        self.details = details
        self.fbtrace_id = fbtrace_id
        self.status_code = status_code
        self.retry_after = retry_after
        self.raw = raw or {}

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return (
            f"{type(self).__name__}(code={self.code!r}, subcode={self.subcode!r}, "
            f"type={self.error_type!r}, message={self.message!r})"
        )


class AuthError(ApiError):
    """Invalid, expired, or unauthorized access token (HTTP 401 / code 190)."""


class PermissionError_(ApiError):
    """The token lacks a required permission or WhatsApp capability (HTTP 403)."""


class NotFoundError(ApiError):
    """The requested object does not exist or is not reachable (HTTP 404)."""


class RateLimitError(ApiError):
    """A rate or throughput limit was hit. Honor :attr:`retry_after` if set."""


class ValidationError(ApiError):
    """Invalid parameters or malformed request body (132xxx family)."""


class MessagingError(ApiError):
    """A message could not be sent or delivered (131xxx family)."""


class TemplateError(ApiError):
    """Template creation/edit/deletion failed (e.g. duplicate, paused)."""


class MediaError(ApiError):
    """Media upload, retrieval, or download failed."""


class RegistrationError(ApiError):
    """Phone number registration/verification failed (133xxx family)."""


class CallError(ApiError):
    """Calling API operation failed (138xxx family)."""


class WebhookSignatureError(WhatsAppError):
    """An incoming webhook payload failed X-Hub-Signature-256 verification."""


# --- error classification -------------------------------------------------

# Codes Meta documents as rate/throughput limiting.
_RATE_LIMIT_CODES = {
    4,  # application-level rate limit
    17,  # user-level rate limit
    32,  # page-level rate limit
    341,  # per-user marketing template message limit
    368,  # temporarily blocked for policy violations
    613,  # call rate limit
    80007,  # WABA rate limit
    130429,  # pair rate limit (per business-user pair)
    131048,  # spam rate limit hit
    131056,  # (business, user) pair rate limit
}

# Codes Meta documents as transient/temporary — safe to retry.
_TRANSIENT_CODES = {1, 2, 120}


def _pick_class(code: int | None, status: int) -> type[ApiError]:
    if status == 401 or code == 190:
        return AuthError
    if status == 403 or code in (10, 200):
        return PermissionError_
    if status == 404 or (code == 100 and status == 404):
        return NotFoundError
    if code in _RATE_LIMIT_CODES:
        return RateLimitError
    if code is not None:
        if 131000 <= code < 132000:
            if code in (131051, 131052):
                return MediaError
            return MessagingError
        if 132000 <= code < 133000:
            return ValidationError
        if 133000 <= code < 134000:
            return RegistrationError
        if 138000 <= code < 139000:
            return CallError
    if status == 429:
        return RateLimitError
    if status >= 500:
        return ApiError
    return ApiError


def error_from_response(
    status: int, payload: dict[str, Any], retry_after: float | None
) -> ApiError:
    """Build the right :class:`ApiError` subclass from an error response body."""
    err = payload.get("error") or {}
    code = err.get("code")
    cls = _pick_class(code, status)
    data = err.get("error_data") or {}
    return cls(
        err.get("message") or f"HTTP {status}",
        code=code,
        subcode=err.get("error_subcode"),
        error_type=err.get("type"),
        details=data.get("details") or err.get("error_user_msg"),
        fbtrace_id=err.get("fbtrace_id"),
        status_code=status,
        retry_after=retry_after,
        raw=payload,
    )


def is_retryable(exc: ApiError) -> bool:
    """Whether the failed request is safe to retry."""
    if isinstance(exc, RateLimitError):
        return True
    if exc.status_code is not None and exc.status_code >= 500:
        return True
    return exc.code in _TRANSIENT_CODES
