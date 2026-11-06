"""Calling API — ``/{phone-number-id}/calls`` and ``/call_permissions``."""

from __future__ import annotations

from typing import Any

from wapi.http import ApiRequest, clean_body, clean_params
from wapi.types.calls import CallPermission, CallResult

from .base import AsyncResource, Resource

__all__ = ["AsyncCalls", "Calls"]


def _call_body(
    action: str,
    *,
    to: str | None = None,
    call_id: str | None = None,
    sdp_type: str | None = None,
    sdp: str | None = None,
    biz_opaque_callback_data: str | None = None,
) -> dict[str, Any]:
    session = clean_body({"sdp_type": sdp_type, "sdp": sdp})
    return clean_body(
        {
            "messaging_product": "whatsapp",
            "to": to,
            "call_id": call_id,
            "action": action,
            "session": session or None,
            "biz_opaque_callback_data": biz_opaque_callback_data,
        }
    )


class Calls(Resource):
    """Initiate and manage WhatsApp VoIP calls (WebRTC SDP)."""

    def check_permissions(
        self, user_wa_id: str, *, phone_number_id: str | None = None
    ) -> CallPermission:
        """Whether you may call ``user_wa_id`` and which actions are available."""
        spec = ApiRequest(
            "GET",
            f"{self._pnid(phone_number_id)}/call_permissions",
            params=clean_params({"user_wa_id": user_wa_id}),
            into=CallPermission.model_validate,
        )
        return self._req(spec)

    def connect(
        self,
        to: str,
        sdp: str,
        *,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> CallResult:
        """Initiate a call — ``sdp`` is the local SDP *offer* (RFC 8866)."""
        body = _call_body(
            "connect",
            to=to,
            sdp_type="offer",
            sdp=sdp,
            biz_opaque_callback_data=biz_opaque_callback_data,
        )
        return self._req(self._spec(body, phone_number_id))

    def pre_accept(
        self, call_id: str, sdp: str, *, phone_number_id: str | None = None
    ) -> CallResult:
        return self._req(
            self._spec(
                _call_body("pre_accept", call_id=call_id, sdp_type="answer", sdp=sdp),
                phone_number_id,
            )
        )

    def accept(
        self,
        call_id: str,
        sdp: str,
        *,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> CallResult:
        """Accept an inbound call — ``sdp`` is the local SDP *answer*."""
        return self._req(
            self._spec(
                _call_body(
                    "accept",
                    call_id=call_id,
                    sdp_type="answer",
                    sdp=sdp,
                    biz_opaque_callback_data=biz_opaque_callback_data,
                ),
                phone_number_id,
            )
        )

    def reject(self, call_id: str, *, phone_number_id: str | None = None) -> CallResult:
        return self._req(self._spec(_call_body("reject", call_id=call_id), phone_number_id))

    def terminate(self, call_id: str, *, phone_number_id: str | None = None) -> CallResult:
        return self._req(self._spec(_call_body("terminate", call_id=call_id), phone_number_id))

    def media_update(
        self, call_id: str, sdp: str, *, phone_number_id: str | None = None
    ) -> CallResult:
        return self._req(
            self._spec(
                _call_body("media_update", call_id=call_id, sdp_type="offer", sdp=sdp),
                phone_number_id,
            )
        )

    def _spec(self, body: dict[str, Any], phone_number_id: str | None) -> ApiRequest[CallResult]:
        return ApiRequest(
            "POST",
            f"{self._pnid(phone_number_id)}/calls",
            json=body,
            into=CallResult.model_validate,
        )


class AsyncCalls(AsyncResource):
    """Async variant of :class:`Calls`."""

    async def check_permissions(
        self, user_wa_id: str, *, phone_number_id: str | None = None
    ) -> CallPermission:
        spec = ApiRequest(
            "GET",
            f"{self._pnid(phone_number_id)}/call_permissions",
            params=clean_params({"user_wa_id": user_wa_id}),
            into=CallPermission.model_validate,
        )
        return await self._req(spec)

    async def connect(
        self,
        to: str,
        sdp: str,
        *,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> CallResult:
        body = _call_body(
            "connect",
            to=to,
            sdp_type="offer",
            sdp=sdp,
            biz_opaque_callback_data=biz_opaque_callback_data,
        )
        return await self._req(self._spec(body, phone_number_id))

    async def pre_accept(
        self, call_id: str, sdp: str, *, phone_number_id: str | None = None
    ) -> CallResult:
        return await self._req(
            self._spec(
                _call_body("pre_accept", call_id=call_id, sdp_type="answer", sdp=sdp),
                phone_number_id,
            )
        )

    async def accept(
        self,
        call_id: str,
        sdp: str,
        *,
        biz_opaque_callback_data: str | None = None,
        phone_number_id: str | None = None,
    ) -> CallResult:
        return await self._req(
            self._spec(
                _call_body(
                    "accept",
                    call_id=call_id,
                    sdp_type="answer",
                    sdp=sdp,
                    biz_opaque_callback_data=biz_opaque_callback_data,
                ),
                phone_number_id,
            )
        )

    async def reject(self, call_id: str, *, phone_number_id: str | None = None) -> CallResult:
        return await self._req(self._spec(_call_body("reject", call_id=call_id), phone_number_id))

    async def terminate(self, call_id: str, *, phone_number_id: str | None = None) -> CallResult:
        return await self._req(
            self._spec(_call_body("terminate", call_id=call_id), phone_number_id)
        )

    async def media_update(
        self, call_id: str, sdp: str, *, phone_number_id: str | None = None
    ) -> CallResult:
        return await self._req(
            self._spec(
                _call_body("media_update", call_id=call_id, sdp_type="offer", sdp=sdp),
                phone_number_id,
            )
        )

    def _spec(self, body: dict[str, Any], phone_number_id: str | None) -> ApiRequest[CallResult]:
        return ApiRequest(
            "POST",
            f"{self._pnid(phone_number_id)}/calls",
            json=body,
            into=CallResult.model_validate,
        )
