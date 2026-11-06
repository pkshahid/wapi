"""``POST /{phone-number-id}/messages`` — every outbound message type."""

from __future__ import annotations

from typing import Any, Literal

from wapi.builders import Media, Payload, Text, as_dict
from wapi.http import ApiRequest, clean_body
from wapi.types.messages import MessageResponse

from .base import AsyncResource, Resource

__all__ = ["AsyncMessages", "Messages"]

RecipientType = Literal["individual", "group"]


def _payload(
    to: str,
    type_: str,
    content: dict[str, Any],
    *,
    recipient_type: str = "individual",
    reply_to: str | None = None,
    biz_opaque_callback_data: str | None = None,
) -> dict[str, Any]:
    return clean_body(
        {
            "messaging_product": "whatsapp",
            "recipient_type": recipient_type,
            "to": to,
            "type": type_,
            "context": {"message_id": reply_to} if reply_to else None,
            "biz_opaque_callback_data": biz_opaque_callback_data,
            type_: content,
        }
    )


def _spec(pnid: str, body: dict[str, Any]) -> ApiRequest[MessageResponse]:
    return ApiRequest("POST", f"{pnid}/messages", json=body, into=MessageResponse.model_validate)


def _common(
    to: str,
    type_: str,
    content: Any,
    kw: dict[str, Any],
) -> dict[str, Any]:
    if isinstance(content, Payload):
        content = content.to_dict()
    return _payload(to, type_, content, **kw)


class Messages(Resource):
    """Send messages and read receipts.

    Every ``send_*`` returns :class:`MessageResponse` (use ``.message_id``).
    ``reply_to`` quotes a message; ``biz_opaque_callback_data`` is echoed back
    in status webhooks.
    """

    # --- generic -----------------------------------------------------------

    def send(
        self,
        to: str,
        type: str,
        content: Any,
        *,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        """Send any message type with a raw/built content payload."""
        kw = dict(
            recipient_type=recipient_type,
            reply_to=reply_to,
            biz_opaque_callback_data=biz_opaque_callback_data,
        )
        return self._req(_spec(self._pnid(phone_number_id), _common(to, type, content, kw)))

    def send_raw(
        self, payload: dict[str, Any], *, phone_number_id: str | None = None
    ) -> MessageResponse:
        """Send a fully-formed JSON payload (escape hatch)."""
        body = {"messaging_product": "whatsapp", **payload}
        return self._req(_spec(self._pnid(phone_number_id), clean_body(body)))

    # --- text --------------------------------------------------------------

    def send_text(
        self,
        to: str,
        body: str,
        *,
        preview_url: bool = False,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        return self.send(
            to,
            "text",
            Text(body, preview_url=preview_url),
            recipient_type=recipient_type,
            reply_to=reply_to,
            biz_opaque_callback_data=biz_opaque_callback_data,
            phone_number_id=phone_number_id,
        )

    # --- media -------------------------------------------------------------

    def _send_media(
        self,
        type_: str,
        to: str,
        kw: dict[str, Any],
    ) -> MessageResponse:
        kw_media = {k: kw.pop(k) for k in ("media_id", "link", "caption", "filename") if k in kw}
        return self.send(to, type_, Media(**kw_media), **kw)

    def send_image(
        self,
        to: str,
        *,
        media_id: str | None = None,
        link: str | None = None,
        caption: str | None = None,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        return self._send_media(
            "image",
            to,
            dict(
                media_id=media_id,
                link=link,
                caption=caption,
                recipient_type=recipient_type,
                reply_to=reply_to,
                biz_opaque_callback_data=biz_opaque_callback_data,
                phone_number_id=phone_number_id,
            ),
        )

    def send_audio(
        self,
        to: str,
        *,
        media_id: str | None = None,
        link: str | None = None,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        return self._send_media(
            "audio",
            to,
            dict(
                media_id=media_id,
                link=link,
                recipient_type=recipient_type,
                reply_to=reply_to,
                biz_opaque_callback_data=biz_opaque_callback_data,
                phone_number_id=phone_number_id,
            ),
        )

    def send_video(
        self,
        to: str,
        *,
        media_id: str | None = None,
        link: str | None = None,
        caption: str | None = None,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        return self._send_media(
            "video",
            to,
            dict(
                media_id=media_id,
                link=link,
                caption=caption,
                recipient_type=recipient_type,
                reply_to=reply_to,
                biz_opaque_callback_data=biz_opaque_callback_data,
                phone_number_id=phone_number_id,
            ),
        )

    def send_document(
        self,
        to: str,
        *,
        media_id: str | None = None,
        link: str | None = None,
        caption: str | None = None,
        filename: str | None = None,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        return self._send_media(
            "document",
            to,
            dict(
                media_id=media_id,
                link=link,
                caption=caption,
                filename=filename,
                recipient_type=recipient_type,
                reply_to=reply_to,
                biz_opaque_callback_data=biz_opaque_callback_data,
                phone_number_id=phone_number_id,
            ),
        )

    def send_sticker(
        self,
        to: str,
        *,
        media_id: str | None = None,
        link: str | None = None,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        return self._send_media(
            "sticker",
            to,
            dict(
                media_id=media_id,
                link=link,
                recipient_type=recipient_type,
                reply_to=reply_to,
                biz_opaque_callback_data=biz_opaque_callback_data,
                phone_number_id=phone_number_id,
            ),
        )

    # --- other content types ------------------------------------------------

    def send_location(
        self,
        to: str,
        *,
        latitude: float,
        longitude: float,
        name: str | None = None,
        address: str | None = None,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        content = clean_body(
            {"latitude": latitude, "longitude": longitude, "name": name, "address": address}
        )
        return self.send(
            to,
            "location",
            content,
            recipient_type=recipient_type,
            reply_to=reply_to,
            biz_opaque_callback_data=biz_opaque_callback_data,
            phone_number_id=phone_number_id,
        )

    def send_contacts(
        self,
        to: str,
        contacts: list[dict[str, Any] | Payload],
        *,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        return self.send(
            to,
            "contacts",
            [as_dict(c) for c in contacts],
            recipient_type=recipient_type,
            reply_to=reply_to,
            biz_opaque_callback_data=biz_opaque_callback_data,
            phone_number_id=phone_number_id,
        )

    def send_reaction(
        self,
        to: str,
        *,
        message_id: str,
        emoji: str,
        recipient_type: RecipientType = "individual",
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        return self.send(
            to,
            "reaction",
            {"message_id": message_id, "emoji": emoji},
            recipient_type=recipient_type,
            biz_opaque_callback_data=biz_opaque_callback_data,
            phone_number_id=phone_number_id,
        )

    def send_interactive(
        self,
        to: str,
        interactive: dict[str, Any] | Payload,
        *,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        """Send any interactive message — pass a builder (``Buttons``,
        ``ListMessage``, ``FlowMessage``…) or a raw dict."""
        return self.send(
            to,
            "interactive",
            as_dict(interactive),
            recipient_type=recipient_type,
            reply_to=reply_to,
            biz_opaque_callback_data=biz_opaque_callback_data,
            phone_number_id=phone_number_id,
        )

    def send_template(
        self,
        to: str,
        template: dict[str, Any] | Payload,
        *,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        return self.send(
            to,
            "template",
            as_dict(template),
            recipient_type=recipient_type,
            reply_to=reply_to,
            biz_opaque_callback_data=biz_opaque_callback_data,
            phone_number_id=phone_number_id,
        )

    # --- receipts / indicators ----------------------------------------------

    def mark_read(
        self,
        message_id: str,
        *,
        typing: bool = False,
        phone_number_id: str | None = None,
    ) -> dict[str, Any]:
        """Mark a message read; optionally show a typing indicator."""
        body = clean_body(
            {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id,
                "typing_indicator": {"type": "text"} if typing else None,
            }
        )
        spec = ApiRequest("POST", f"{self._pnid(phone_number_id)}/messages", json=body)
        return self._req(spec)


class AsyncMessages(AsyncResource):
    """Async variant of :class:`Messages`. Same methods, awaitable results."""

    async def send(
        self,
        to: str,
        type: str,
        content: Any,
        *,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        kw = dict(
            recipient_type=recipient_type,
            reply_to=reply_to,
            biz_opaque_callback_data=biz_opaque_callback_data,
        )
        return await self._req(_spec(self._pnid(phone_number_id), _common(to, type, content, kw)))

    async def send_raw(
        self, payload: dict[str, Any], *, phone_number_id: str | None = None
    ) -> MessageResponse:
        body = {"messaging_product": "whatsapp", **payload}
        return await self._req(_spec(self._pnid(phone_number_id), clean_body(body)))

    async def send_text(
        self,
        to: str,
        body: str,
        *,
        preview_url: bool = False,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        return await self.send(
            to,
            "text",
            Text(body, preview_url=preview_url),
            recipient_type=recipient_type,
            reply_to=reply_to,
            biz_opaque_callback_data=biz_opaque_callback_data,
            phone_number_id=phone_number_id,
        )

    async def _send_media(self, type_: str, to: str, kw: dict[str, Any]) -> MessageResponse:
        kw_media = {k: kw.pop(k) for k in ("media_id", "link", "caption", "filename") if k in kw}
        return await self.send(to, type_, Media(**kw_media), **kw)

    async def send_image(
        self,
        to: str,
        *,
        media_id: str | None = None,
        link: str | None = None,
        caption: str | None = None,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        return await self._send_media(
            "image",
            to,
            dict(
                media_id=media_id,
                link=link,
                caption=caption,
                recipient_type=recipient_type,
                reply_to=reply_to,
                biz_opaque_callback_data=biz_opaque_callback_data,
                phone_number_id=phone_number_id,
            ),
        )

    async def send_audio(
        self,
        to: str,
        *,
        media_id: str | None = None,
        link: str | None = None,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        return await self._send_media(
            "audio",
            to,
            dict(
                media_id=media_id,
                link=link,
                recipient_type=recipient_type,
                reply_to=reply_to,
                biz_opaque_callback_data=biz_opaque_callback_data,
                phone_number_id=phone_number_id,
            ),
        )

    async def send_video(
        self,
        to: str,
        *,
        media_id: str | None = None,
        link: str | None = None,
        caption: str | None = None,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        return await self._send_media(
            "video",
            to,
            dict(
                media_id=media_id,
                link=link,
                caption=caption,
                recipient_type=recipient_type,
                reply_to=reply_to,
                biz_opaque_callback_data=biz_opaque_callback_data,
                phone_number_id=phone_number_id,
            ),
        )

    async def send_document(
        self,
        to: str,
        *,
        media_id: str | None = None,
        link: str | None = None,
        caption: str | None = None,
        filename: str | None = None,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        return await self._send_media(
            "document",
            to,
            dict(
                media_id=media_id,
                link=link,
                caption=caption,
                filename=filename,
                recipient_type=recipient_type,
                reply_to=reply_to,
                biz_opaque_callback_data=biz_opaque_callback_data,
                phone_number_id=phone_number_id,
            ),
        )

    async def send_sticker(
        self,
        to: str,
        *,
        media_id: str | None = None,
        link: str | None = None,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        return await self._send_media(
            "sticker",
            to,
            dict(
                media_id=media_id,
                link=link,
                recipient_type=recipient_type,
                reply_to=reply_to,
                biz_opaque_callback_data=biz_opaque_callback_data,
                phone_number_id=phone_number_id,
            ),
        )

    async def send_location(
        self,
        to: str,
        *,
        latitude: float,
        longitude: float,
        name: str | None = None,
        address: str | None = None,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        content = clean_body(
            {"latitude": latitude, "longitude": longitude, "name": name, "address": address}
        )
        return await self.send(
            to,
            "location",
            content,
            recipient_type=recipient_type,
            reply_to=reply_to,
            biz_opaque_callback_data=biz_opaque_callback_data,
            phone_number_id=phone_number_id,
        )

    async def send_contacts(
        self,
        to: str,
        contacts: list[dict[str, Any] | Payload],
        *,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        return await self.send(
            to,
            "contacts",
            [as_dict(c) for c in contacts],
            recipient_type=recipient_type,
            reply_to=reply_to,
            biz_opaque_callback_data=biz_opaque_callback_data,
            phone_number_id=phone_number_id,
        )

    async def send_reaction(
        self,
        to: str,
        *,
        message_id: str,
        emoji: str,
        recipient_type: RecipientType = "individual",
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        return await self.send(
            to,
            "reaction",
            {"message_id": message_id, "emoji": emoji},
            recipient_type=recipient_type,
            biz_opaque_callback_data=biz_opaque_callback_data,
            phone_number_id=phone_number_id,
        )

    async def send_interactive(
        self,
        to: str,
        interactive: dict[str, Any] | Payload,
        *,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        return await self.send(
            to,
            "interactive",
            as_dict(interactive),
            recipient_type=recipient_type,
            reply_to=reply_to,
            biz_opaque_callback_data=biz_opaque_callback_data,
            phone_number_id=phone_number_id,
        )

    async def send_template(
        self,
        to: str,
        template: dict[str, Any] | Payload,
        *,
        recipient_type: RecipientType = "individual",
        reply_to: str | None = None,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        return await self.send(
            to,
            "template",
            as_dict(template),
            recipient_type=recipient_type,
            reply_to=reply_to,
            biz_opaque_callback_data=biz_opaque_callback_data,
            phone_number_id=phone_number_id,
        )

    async def mark_read(
        self, message_id: str, *, typing: bool = False, phone_number_id: str | None = None
    ) -> dict[str, Any]:
        body = clean_body(
            {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id,
                "typing_indicator": {"type": "text"} if typing else None,
            }
        )
        return await self._req(
            ApiRequest("POST", f"{self._pnid(phone_number_id)}/messages", json=body)
        )
