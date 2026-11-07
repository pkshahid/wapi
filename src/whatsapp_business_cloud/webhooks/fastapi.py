"""Optional FastAPI webhook router (install ``whatsapp-business-cloud[fastapi]``).

::

    from fastapi import FastAPI
    from whatsapp_business_cloud.webhooks.fastapi import webhook_router

    app = FastAPI()

    async def on_event(event):
        if isinstance(event, InboundMessages):
            ...

    app.include_router(webhook_router(on_event, verify_token="tok", app_secret="sec"))
"""

from __future__ import annotations

import inspect
import json
from collections.abc import Callable
from typing import Any

from whatsapp_business_cloud.exceptions import WebhookSignatureError

from .events import WebhookEvent
from .parser import parse
from .signature import verify_signature

try:  # pragma: no cover - optional extra
    from fastapi import APIRouter, Request, Response
    from fastapi.responses import PlainTextResponse

    _HAS_FASTAPI = True
except ImportError:  # pragma: no cover
    _HAS_FASTAPI = False

__all__ = ["verify_webhook_challenge", "webhook_router"]

Handler = Callable[[WebhookEvent], Any]
BatchHandler = Callable[[list[WebhookEvent]], Any]


def verify_webhook_challenge(
    hub_mode: str | None,
    hub_verify_token: str | None,
    hub_challenge: str | None,
    verify_token: str,
) -> str | None:
    """Implement the ``GET`` handshake; returns the challenge to echo or ``None``."""
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        return hub_challenge
    return None


def webhook_router(
    handler: Handler | BatchHandler,
    *,
    verify_token: str,
    app_secret: str | None = None,
    path: str = "/webhook",
    per_event: bool = True,
) -> Any:
    """Build a FastAPI ``APIRouter`` handling webhook verification + dispatch.

    - ``GET {path}`` answers Meta's verification challenge.
    - ``POST {path}`` verifies ``X-Hub-Signature-256`` (when ``app_secret``
      is set), parses events, and calls ``handler``.

    With ``per_event=True`` (default) ``handler`` is invoked once per event;
    with ``False`` it receives the whole ``list[WebhookEvent]``.
    Sync and async handlers are both supported.
    """
    if not _HAS_FASTAPI:  # pragma: no cover
        raise ImportError("webhook_router requires the 'fastapi' extra: pip install whatsapp-business-cloud[fastapi]")

    router = APIRouter()

    async def _dispatch(events: list[WebhookEvent]) -> None:
        if per_event:
            for event in events:
                result = handler(event)  # type: ignore[arg-type]
                if inspect.isawaitable(result):
                    await result
        else:
            result = handler(events)  # type: ignore[arg-type]
            if inspect.isawaitable(result):
                await result

    @router.get(path)
    async def verify(request: Request) -> Response:
        challenge = verify_webhook_challenge(
            request.query_params.get("hub.mode"),
            request.query_params.get("hub.verify_token"),
            request.query_params.get("hub.challenge"),
            verify_token,
        )
        if challenge is not None:
            return PlainTextResponse(challenge)
        return PlainTextResponse("Forbidden", status_code=403)

    @router.post(path)
    async def receive(request: Request) -> Response:
        raw = await request.body()
        if app_secret is not None:
            sig = request.headers.get("x-hub-signature-256")
            if not verify_signature(raw, sig, app_secret):
                return PlainTextResponse("Invalid signature", status_code=401)
        try:
            events = parse(json.loads(raw))
        except (json.JSONDecodeError, ValueError) as e:
            raise WebhookSignatureError("malformed webhook payload") from e
        await _dispatch(events)
        return PlainTextResponse("OK")

    return router
