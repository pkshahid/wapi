"""X-Hub-Signature-256 verification for inbound webhooks."""

from __future__ import annotations

import hashlib
import hmac

from whatsapp_cloud.exceptions import WebhookSignatureError

__all__ = ["compute_signature", "verify_or_raise", "verify_signature"]


def compute_signature(payload: bytes, app_secret: str) -> str:
    """Return the ``sha256=…`` signature string for a payload."""
    digest = hmac.new(app_secret.encode(), payload, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def verify_signature(payload: bytes, signature_header: str | None, app_secret: str) -> bool:
    """Constant-time check of ``X-Hub-Signature-256`` against the raw body."""
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = compute_signature(payload, app_secret)
    return hmac.compare_digest(expected, signature_header)


def verify_or_raise(payload: bytes, signature_header: str | None, app_secret: str) -> None:
    """Raise :class:`WebhookSignatureError` when verification fails."""
    if not verify_signature(payload, signature_header, app_secret):
        raise WebhookSignatureError("webhook signature verification failed")
