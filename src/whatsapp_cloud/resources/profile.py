"""Phone-number account resources: business profile, commerce settings,
compliance info, conversational automation, encryption, QR codes, block list.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from whatsapp_cloud.http import ApiRequest, clean_body, clean_params, merge_fields
from whatsapp_cloud.types.profiles import BlockedUser, BusinessProfile, CommerceSettings, QRCode

from .base import AsyncResource, Resource

__all__ = [
    "AsyncAutomation",
    "AsyncBlockedUsers",
    "AsyncCommerce",
    "AsyncCompliance",
    "AsyncEncryption",
    "AsyncProfile",
    "AsyncQRCodes",
    "Automation",
    "BlockedUsers",
    "Commerce",
    "Compliance",
    "Encryption",
    "Profile",
    "QRCodes",
]


class Profile(Resource):
    """``/{phone-number-id}/whatsapp_business_profile``."""

    def get(
        self,
        *,
        fields: Sequence[str] | str | None = None,
        phone_number_id: str | None = None,
    ) -> BusinessProfile:
        spec = ApiRequest(
            "GET",
            f"{self._pnid(phone_number_id)}/whatsapp_business_profile",
            params=clean_params({"fields": merge_fields(fields)}),
        )
        body = self._req(spec)
        data = body.get("data") or [{}]
        return BusinessProfile.model_validate(data[0] if data else {})

    def update(
        self,
        *,
        about: str | None = None,
        address: str | None = None,
        description: str | None = None,
        email: str | None = None,
        websites: Sequence[str] | None = None,
        vertical: str | None = None,
        profile_picture_handle: str | None = None,
        phone_number_id: str | None = None,
    ) -> dict[str, Any]:
        body = clean_body(
            dict(
                messaging_product="whatsapp",
                about=about,
                address=address,
                description=description,
                email=email,
                websites=websites,
                vertical=vertical,
                profile_picture_handle=profile_picture_handle,
            )
        )
        return self._req(
            ApiRequest(
                "POST", f"{self._pnid(phone_number_id)}/whatsapp_business_profile", json=body
            )
        )


class Commerce(Resource):
    """``/{phone-number-id}/whatsapp_commerce_settings``."""

    def get(self, *, phone_number_id: str | None = None) -> CommerceSettings:
        body = self._req(
            ApiRequest("GET", f"{self._pnid(phone_number_id)}/whatsapp_commerce_settings")
        )
        data = body.get("data") or [{}]
        return CommerceSettings.model_validate(data[0] if data else {})

    def update(
        self,
        *,
        is_cart_enabled: bool | None = None,
        is_catalog_visible: bool | None = None,
        phone_number_id: str | None = None,
    ) -> dict[str, Any]:
        params = clean_params(
            {"is_cart_enabled": is_cart_enabled, "is_catalog_visible": is_catalog_visible}
        )
        return self._req(
            ApiRequest(
                "POST", f"{self._pnid(phone_number_id)}/whatsapp_commerce_settings", params=params
            )
        )


class Compliance(Resource):
    """``/{phone-number-id}/business_compliance_info`` (India)."""

    def get(
        self, *, fields: Sequence[str] | str | None = None, phone_number_id: str | None = None
    ) -> dict[str, Any]:
        return self._req(
            ApiRequest(
                "GET",
                f"{self._pnid(phone_number_id)}/business_compliance_info",
                params=clean_params({"fields": merge_fields(fields)}),
            )
        )

    def update(
        self,
        *,
        entity_name: str,
        entity_type: str,
        grievance_officer_details: dict[str, Any],
        customer_care_details: dict[str, Any],
        is_registered: bool | None = None,
        entity_type_custom: str | None = None,
        phone_number_id: str | None = None,
    ) -> dict[str, Any]:
        body = clean_body(
            dict(
                messaging_product="whatsapp",
                entity_name=entity_name,
                entity_type=entity_type,
                entity_type_custom=entity_type_custom,
                is_registered=is_registered,
                grievance_officer_details=grievance_officer_details,
                customer_care_details=customer_care_details,
            )
        )
        return self._req(
            ApiRequest("POST", f"{self._pnid(phone_number_id)}/business_compliance_info", json=body)
        )


class Automation(Resource):
    """``/{phone-number-id}/conversational_automation`` — welcome messages."""

    def configure(
        self,
        *,
        enable_welcome_message: bool | None = None,
        prompts: Sequence[str] | None = None,
        commands: Sequence[dict[str, Any]] | None = None,
        phone_number_id: str | None = None,
    ) -> dict[str, Any]:
        body = clean_body(
            dict(enable_welcome_message=enable_welcome_message, prompts=prompts, commands=commands)
        )
        return self._req(
            ApiRequest(
                "POST", f"{self._pnid(phone_number_id)}/conversational_automation", json=body
            )
        )


class Encryption(Resource):
    """``/{phone-number-id}/whatsapp_business_encryption`` — Flows pubkey."""

    def get(
        self, *, fields: Sequence[str] | str | None = None, phone_number_id: str | None = None
    ) -> dict[str, Any]:
        return self._req(
            ApiRequest(
                "GET",
                f"{self._pnid(phone_number_id)}/whatsapp_business_encryption",
                params=clean_params({"fields": merge_fields(fields)}),
            )
        )

    def set_key(
        self, business_public_key: str, *, phone_number_id: str | None = None
    ) -> dict[str, Any]:
        return self._req(
            ApiRequest(
                "POST",
                f"{self._pnid(phone_number_id)}/whatsapp_business_encryption",
                json={"business_public_key": business_public_key},
            )
        )


class QRCodes(Resource):
    """``/{phone-number-id}/message_qrdls`` — QR codes & message links."""

    def list(
        self,
        *,
        fields: Sequence[str] | str | None = None,
        code: str | None = None,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
        phone_number_id: str | None = None,
    ) -> Any:
        spec = ApiRequest(
            "GET",
            f"{self._pnid(phone_number_id)}/message_qrdls",
            params=clean_params(
                dict(
                    fields=merge_fields(fields), code=code, limit=limit, after=after, before=before
                )
            ),
        )
        return self._page(spec, QRCode.model_validate)

    def get(
        self,
        qr_code_id: str,
        *,
        fields: Sequence[str] | str | None = None,
        phone_number_id: str | None = None,
    ) -> QRCode:
        spec = ApiRequest(
            "GET",
            f"{self._pnid(phone_number_id)}/message_qrdls/{qr_code_id}",
            params=clean_params({"fields": merge_fields(fields)}),
        )
        body = self._req(spec)
        data = body.get("data") or [{}]
        return QRCode.model_validate(data[0] if data else {})

    def create_or_update(
        self,
        *,
        prefilled_message: str,
        code: str | None = None,
        generate_qr_image: str | None = None,
        phone_number_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a QR code (or update it when ``code`` is given).
        ``generate_qr_image``: ``"PNG"`` or ``"SVG"`` to get ``qr_image_url``."""
        body = clean_body(
            dict(
                prefilled_message=prefilled_message, code=code, generate_qr_image=generate_qr_image
            )
        )
        return self._req(
            ApiRequest("POST", f"{self._pnid(phone_number_id)}/message_qrdls", json=body)
        )

    def delete(self, qr_code_id: str, *, phone_number_id: str | None = None) -> dict[str, Any]:
        return self._req(
            ApiRequest("DELETE", f"{self._pnid(phone_number_id)}/message_qrdls/{qr_code_id}")
        )


class BlockedUsers(Resource):
    """``/{phone-number-id}/block_users``."""

    def list(self, *, phone_number_id: str | None = None) -> Sequence[BlockedUser]:
        body = self._req(ApiRequest("GET", f"{self._pnid(phone_number_id)}/block_users"))
        return [BlockedUser.model_validate(u) for u in body.get("users") or []]

    def _set(
        self, method: str, users: Sequence[str], phone_number_id: str | None
    ) -> dict[str, Any]:
        body = {
            "messaging_product": "whatsapp",
            "block_users": [{"user": u} for u in users],
        }
        return self._req(
            ApiRequest(method, f"{self._pnid(phone_number_id)}/block_users", json=body)
        )

    def block(
        self, users: Sequence[str] | str, *, phone_number_id: str | None = None
    ) -> dict[str, Any]:
        users = [users] if isinstance(users, str) else users
        return self._set("POST", users, phone_number_id)

    def unblock(
        self, users: Sequence[str] | str, *, phone_number_id: str | None = None
    ) -> dict[str, Any]:
        users = [users] if isinstance(users, str) else users
        return self._set("DELETE", users, phone_number_id)


# --- async twins -------------------------------------------------------------


class AsyncProfile(AsyncResource):
    async def get(
        self, *, fields: Sequence[str] | str | None = None, phone_number_id: str | None = None
    ) -> BusinessProfile:
        spec = ApiRequest(
            "GET",
            f"{self._pnid(phone_number_id)}/whatsapp_business_profile",
            params=clean_params({"fields": merge_fields(fields)}),
        )
        body = await self._req(spec)
        data = body.get("data") or [{}]
        return BusinessProfile.model_validate(data[0] if data else {})

    async def update(
        self,
        *,
        about: str | None = None,
        address: str | None = None,
        description: str | None = None,
        email: str | None = None,
        websites: Sequence[str] | None = None,
        vertical: str | None = None,
        profile_picture_handle: str | None = None,
        phone_number_id: str | None = None,
    ) -> dict[str, Any]:
        body = clean_body(
            dict(
                messaging_product="whatsapp",
                about=about,
                address=address,
                description=description,
                email=email,
                websites=websites,
                vertical=vertical,
                profile_picture_handle=profile_picture_handle,
            )
        )
        return await self._req(
            ApiRequest(
                "POST", f"{self._pnid(phone_number_id)}/whatsapp_business_profile", json=body
            )
        )


class AsyncCommerce(AsyncResource):
    async def get(self, *, phone_number_id: str | None = None) -> CommerceSettings:
        body = await self._req(
            ApiRequest("GET", f"{self._pnid(phone_number_id)}/whatsapp_commerce_settings")
        )
        data = body.get("data") or [{}]
        return CommerceSettings.model_validate(data[0] if data else {})

    async def update(
        self,
        *,
        is_cart_enabled: bool | None = None,
        is_catalog_visible: bool | None = None,
        phone_number_id: str | None = None,
    ) -> dict[str, Any]:
        params = clean_params(
            {"is_cart_enabled": is_cart_enabled, "is_catalog_visible": is_catalog_visible}
        )
        return await self._req(
            ApiRequest(
                "POST", f"{self._pnid(phone_number_id)}/whatsapp_commerce_settings", params=params
            )
        )


class AsyncCompliance(AsyncResource):
    async def get(
        self, *, fields: Sequence[str] | str | None = None, phone_number_id: str | None = None
    ) -> dict[str, Any]:
        return await self._req(
            ApiRequest(
                "GET",
                f"{self._pnid(phone_number_id)}/business_compliance_info",
                params=clean_params({"fields": merge_fields(fields)}),
            )
        )

    async def update(
        self,
        *,
        entity_name: str,
        entity_type: str,
        grievance_officer_details: dict[str, Any],
        customer_care_details: dict[str, Any],
        is_registered: bool | None = None,
        entity_type_custom: str | None = None,
        phone_number_id: str | None = None,
    ) -> dict[str, Any]:
        body = clean_body(
            dict(
                messaging_product="whatsapp",
                entity_name=entity_name,
                entity_type=entity_type,
                entity_type_custom=entity_type_custom,
                is_registered=is_registered,
                grievance_officer_details=grievance_officer_details,
                customer_care_details=customer_care_details,
            )
        )
        return await self._req(
            ApiRequest("POST", f"{self._pnid(phone_number_id)}/business_compliance_info", json=body)
        )


class AsyncAutomation(AsyncResource):
    async def configure(
        self,
        *,
        enable_welcome_message: bool | None = None,
        prompts: Sequence[str] | None = None,
        commands: Sequence[dict[str, Any]] | None = None,
        phone_number_id: str | None = None,
    ) -> dict[str, Any]:
        body = clean_body(
            dict(enable_welcome_message=enable_welcome_message, prompts=prompts, commands=commands)
        )
        return await self._req(
            ApiRequest(
                "POST", f"{self._pnid(phone_number_id)}/conversational_automation", json=body
            )
        )


class AsyncEncryption(AsyncResource):
    async def get(
        self, *, fields: Sequence[str] | str | None = None, phone_number_id: str | None = None
    ) -> dict[str, Any]:
        return await self._req(
            ApiRequest(
                "GET",
                f"{self._pnid(phone_number_id)}/whatsapp_business_encryption",
                params=clean_params({"fields": merge_fields(fields)}),
            )
        )

    async def set_key(
        self, business_public_key: str, *, phone_number_id: str | None = None
    ) -> dict[str, Any]:
        return await self._req(
            ApiRequest(
                "POST",
                f"{self._pnid(phone_number_id)}/whatsapp_business_encryption",
                json={"business_public_key": business_public_key},
            )
        )


class AsyncQRCodes(AsyncResource):
    def list(
        self,
        *,
        fields: Sequence[str] | str | None = None,
        code: str | None = None,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
        phone_number_id: str | None = None,
    ) -> Any:
        spec = ApiRequest(
            "GET",
            f"{self._pnid(phone_number_id)}/message_qrdls",
            params=clean_params(
                dict(
                    fields=merge_fields(fields), code=code, limit=limit, after=after, before=before
                )
            ),
        )
        return self._page(spec, QRCode.model_validate)

    async def get(
        self,
        qr_code_id: str,
        *,
        fields: Sequence[str] | str | None = None,
        phone_number_id: str | None = None,
    ) -> QRCode:
        body = await self._req(
            ApiRequest(
                "GET",
                f"{self._pnid(phone_number_id)}/message_qrdls/{qr_code_id}",
                params=clean_params({"fields": merge_fields(fields)}),
            )
        )
        data = body.get("data") or [{}]
        return QRCode.model_validate(data[0] if data else {})

    async def create_or_update(
        self,
        *,
        prefilled_message: str,
        code: str | None = None,
        generate_qr_image: str | None = None,
        phone_number_id: str | None = None,
    ) -> dict[str, Any]:
        body = clean_body(
            dict(
                prefilled_message=prefilled_message, code=code, generate_qr_image=generate_qr_image
            )
        )
        return await self._req(
            ApiRequest("POST", f"{self._pnid(phone_number_id)}/message_qrdls", json=body)
        )

    async def delete(
        self, qr_code_id: str, *, phone_number_id: str | None = None
    ) -> dict[str, Any]:
        return await self._req(
            ApiRequest("DELETE", f"{self._pnid(phone_number_id)}/message_qrdls/{qr_code_id}")
        )


class AsyncBlockedUsers(AsyncResource):
    async def list(self, *, phone_number_id: str | None = None) -> Sequence[BlockedUser]:
        body = await self._req(ApiRequest("GET", f"{self._pnid(phone_number_id)}/block_users"))
        return [BlockedUser.model_validate(u) for u in body.get("users") or []]

    async def _set(
        self, method: str, users: Sequence[str], phone_number_id: str | None
    ) -> dict[str, Any]:
        body = {"messaging_product": "whatsapp", "block_users": [{"user": u} for u in users]}
        return await self._req(
            ApiRequest(method, f"{self._pnid(phone_number_id)}/block_users", json=body)
        )

    async def block(
        self, users: Sequence[str] | str, *, phone_number_id: str | None = None
    ) -> dict[str, Any]:
        users = [users] if isinstance(users, str) else users
        return await self._set("POST", users, phone_number_id)

    async def unblock(
        self, users: Sequence[str] | str, *, phone_number_id: str | None = None
    ) -> dict[str, Any]:
        users = [users] if isinstance(users, str) else users
        return await self._set("DELETE", users, phone_number_id)
