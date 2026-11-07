"""Marketing Messages (MM Lite) API — ``/{phone-number-id}/marketing_messages``."""

from __future__ import annotations

from typing import Any, Literal

from whatsapp_business_cloud.builders import Payload, as_dict
from whatsapp_business_cloud.http import ApiRequest, clean_body
from whatsapp_business_cloud.types.messages import MessageResponse

from .base import AsyncResource, Resource

__all__ = ["AsyncMarketing", "Marketing"]

ProductPolicy = Literal["CLOUD_API_FALLBACK", "STRICT"]


def _body(
    to: str,
    template: dict[str, Any],
    product_policy: str | None,
    message_activity_sharing: bool | None,
) -> dict[str, Any]:
    return clean_body(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "template",
            "template": template,
            "product_policy": product_policy,
            "message_activity_sharing": message_activity_sharing,
        }
    )


class Marketing(Resource):
    """Send marketing template messages with Meta-side delivery optimizations."""

    def send_template(
        self,
        to: str,
        template: dict[str, Any] | Payload,
        *,
        product_policy: ProductPolicy | None = None,
        message_activity_sharing: bool | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        spec = ApiRequest(
            "POST",
            f"{self._pnid(phone_number_id)}/marketing_messages",
            json=_body(to, as_dict(template), product_policy, message_activity_sharing),
            into=MessageResponse.model_validate,
        )
        return self._req(spec)


class AsyncMarketing(AsyncResource):
    """Async variant of :class:`Marketing`."""

    async def send_template(
        self,
        to: str,
        template: dict[str, Any] | Payload,
        *,
        product_policy: ProductPolicy | None = None,
        message_activity_sharing: bool | None = None,
        phone_number_id: str | None = None,
    ) -> MessageResponse:
        spec = ApiRequest(
            "POST",
            f"{self._pnid(phone_number_id)}/marketing_messages",
            json=_body(to, as_dict(template), product_policy, message_activity_sharing),
            into=MessageResponse.model_validate,
        )
        return await self._req(spec)
