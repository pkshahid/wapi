"""Phone number management, registration, verification, settings, OBA."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from whatsapp_business_cloud.http import ApiRequest, clean_body, clean_params, merge_fields
from whatsapp_business_cloud.types.phone_numbers import PhoneNumber, PhoneNumberInfo

from .base import AsyncResource, Resource

__all__ = ["AsyncPhoneNumbers", "PhoneNumbers"]

CodeMethod = Literal["SMS", "VOICE"]


def _register_body(pin: str, region: str | None, backup: dict[str, Any] | None) -> dict[str, Any]:
    return clean_body(
        {
            "messaging_product": "whatsapp",
            "pin": pin,
            "data_localization_region": region,
            "backup": backup,
        }
    )


class PhoneNumbers(Resource):
    """WABA phone numbers + per-number registration and settings."""

    def list(
        self,
        *,
        fields: Sequence[str] | str | None = None,
        filtering: Sequence[dict[str, Any]] | str | None = None,
        sort: str | None = None,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
        waba_id: str | None = None,
    ) -> Any:
        spec = ApiRequest(
            "GET",
            f"{self._waba(waba_id)}/phone_numbers",
            params=clean_params(
                dict(
                    fields=merge_fields(fields),
                    filtering=filtering,
                    sort=sort,
                    limit=limit,
                    after=after,
                    before=before,
                )
            ),
        )
        return self._page(spec, PhoneNumber.model_validate)

    def add(
        self,
        *,
        cc: str,
        phone_number: str,
        verified_name: str,
        migrate_phone_number: bool | None = None,
        preverified_id: str | None = None,
        waba_id: str | None = None,
    ) -> dict[str, Any]:
        """Add a phone number to the WABA (E.164 digits, no ``+``)."""
        body = clean_body(
            dict(
                cc=cc,
                phone_number=phone_number,
                verified_name=verified_name,
                migrate_phone_number=migrate_phone_number,
                preverified_id=preverified_id,
            )
        )
        return self._req(ApiRequest("POST", f"{self._waba(waba_id)}/phone_numbers", json=body))

    def get(
        self,
        *,
        fields: Sequence[str] | str | None = None,
        phone_number_id: str | None = None,
    ) -> PhoneNumberInfo:
        spec = ApiRequest(
            "GET",
            self._pnid(phone_number_id),
            params=clean_params({"fields": merge_fields(fields)}),
            into=PhoneNumberInfo.model_validate,
        )
        return self._req(spec)

    def update(self, *, phone_number_id: str | None = None, **fields: Any) -> dict[str, Any]:
        """Update number config: ``webhook_url``, ``webhook_configuration``,
        ``pin``, ``new_display_name``, ``username``, ``search_visibility``,
        ``connection_status``, ``whatsapp_business_api_data``."""
        return self._req(ApiRequest("POST", self._pnid(phone_number_id), json=clean_body(fields)))

    def request_code(
        self,
        *,
        code_method: CodeMethod = "SMS",
        language: str | None = None,
        phone_number_id: str | None = None,
    ) -> dict[str, Any]:
        body = clean_body({"code_method": code_method, "language": language})
        return self._req(
            ApiRequest("POST", f"{self._pnid(phone_number_id)}/request_code", json=body)
        )

    def verify_code(self, code: str, *, phone_number_id: str | None = None) -> dict[str, Any]:
        return self._req(
            ApiRequest("POST", f"{self._pnid(phone_number_id)}/verify_code", json={"code": code})
        )

    def register(
        self,
        *,
        pin: str,
        data_localization_region: str | None = None,
        backup: dict[str, Any] | None = None,
        phone_number_id: str | None = None,
    ) -> dict[str, Any]:
        """Register the number after verification. ``pin`` = 6-digit 2FA PIN."""
        return self._req(
            ApiRequest(
                "POST",
                f"{self._pnid(phone_number_id)}/register",
                json=_register_body(pin, data_localization_region, backup),
            )
        )

    def deregister(self, *, phone_number_id: str | None = None) -> dict[str, Any]:
        return self._req(ApiRequest("POST", f"{self._pnid(phone_number_id)}/deregister", json={}))

    def get_settings(
        self,
        *,
        include_sip_credentials: bool | None = None,
        phone_number_id: str | None = None,
    ) -> dict[str, Any]:
        return self._req(
            ApiRequest(
                "GET",
                f"{self._pnid(phone_number_id)}/settings",
                params=clean_params({"include_sip_credentials": include_sip_credentials}),
            )
        )

    def update_settings(
        self,
        *,
        calling: dict[str, Any] | None = None,
        user_identity_change: dict[str, Any] | None = None,
        payload_encryption: dict[str, Any] | None = None,
        storage_configuration: dict[str, Any] | None = None,
        phone_number_id: str | None = None,
    ) -> dict[str, Any]:
        """Update one settings group per call."""
        body = clean_body(
            dict(
                calling=calling,
                user_identity_change=user_identity_change,
                payload_encryption=payload_encryption,
                storage_configuration=storage_configuration,
            )
        )
        if not body:
            raise ValueError("at least one settings group is required")
        return self._req(ApiRequest("POST", f"{self._pnid(phone_number_id)}/settings", json=body))

    def get_official_status(
        self, *, phone_number_id: str | None = None, fields: Sequence[str] | str | None = None
    ) -> dict[str, Any]:
        return self._req(
            ApiRequest(
                "GET",
                f"{self._pnid(phone_number_id)}/official_business_account",
                params=clean_params({"fields": merge_fields(fields)}),
            )
        )

    def update_official_status(self, *, phone_number_id: str | None = None) -> dict[str, Any]:
        return self._req(
            ApiRequest("POST", f"{self._pnid(phone_number_id)}/official_business_account", json={})
        )


class AsyncPhoneNumbers(AsyncResource):
    """Async variant of :class:`PhoneNumbers`."""

    def list(
        self,
        *,
        fields: Sequence[str] | str | None = None,
        filtering: Sequence[dict[str, Any]] | str | None = None,
        sort: str | None = None,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
        waba_id: str | None = None,
    ) -> Any:
        spec = ApiRequest(
            "GET",
            f"{self._waba(waba_id)}/phone_numbers",
            params=clean_params(
                dict(
                    fields=merge_fields(fields),
                    filtering=filtering,
                    sort=sort,
                    limit=limit,
                    after=after,
                    before=before,
                )
            ),
        )
        return self._page(spec, PhoneNumber.model_validate)

    async def add(
        self,
        *,
        cc: str,
        phone_number: str,
        verified_name: str,
        migrate_phone_number: bool | None = None,
        preverified_id: str | None = None,
        waba_id: str | None = None,
    ) -> dict[str, Any]:
        body = clean_body(
            dict(
                cc=cc,
                phone_number=phone_number,
                verified_name=verified_name,
                migrate_phone_number=migrate_phone_number,
                preverified_id=preverified_id,
            )
        )
        return await self._req(
            ApiRequest("POST", f"{self._waba(waba_id)}/phone_numbers", json=body)
        )

    async def get(
        self, *, fields: Sequence[str] | str | None = None, phone_number_id: str | None = None
    ) -> PhoneNumberInfo:
        spec = ApiRequest(
            "GET",
            self._pnid(phone_number_id),
            params=clean_params({"fields": merge_fields(fields)}),
            into=PhoneNumberInfo.model_validate,
        )
        return await self._req(spec)

    async def update(self, *, phone_number_id: str | None = None, **fields: Any) -> dict[str, Any]:
        return await self._req(
            ApiRequest("POST", self._pnid(phone_number_id), json=clean_body(fields))
        )

    async def request_code(
        self,
        *,
        code_method: CodeMethod = "SMS",
        language: str | None = None,
        phone_number_id: str | None = None,
    ) -> dict[str, Any]:
        body = clean_body({"code_method": code_method, "language": language})
        return await self._req(
            ApiRequest("POST", f"{self._pnid(phone_number_id)}/request_code", json=body)
        )

    async def verify_code(self, code: str, *, phone_number_id: str | None = None) -> dict[str, Any]:
        return await self._req(
            ApiRequest("POST", f"{self._pnid(phone_number_id)}/verify_code", json={"code": code})
        )

    async def register(
        self,
        *,
        pin: str,
        data_localization_region: str | None = None,
        backup: dict[str, Any] | None = None,
        phone_number_id: str | None = None,
    ) -> dict[str, Any]:
        return await self._req(
            ApiRequest(
                "POST",
                f"{self._pnid(phone_number_id)}/register",
                json=_register_body(pin, data_localization_region, backup),
            )
        )

    async def deregister(self, *, phone_number_id: str | None = None) -> dict[str, Any]:
        return await self._req(
            ApiRequest("POST", f"{self._pnid(phone_number_id)}/deregister", json={})
        )

    async def get_settings(
        self, *, include_sip_credentials: bool | None = None, phone_number_id: str | None = None
    ) -> dict[str, Any]:
        return await self._req(
            ApiRequest(
                "GET",
                f"{self._pnid(phone_number_id)}/settings",
                params=clean_params({"include_sip_credentials": include_sip_credentials}),
            )
        )

    async def update_settings(
        self,
        *,
        calling: dict[str, Any] | None = None,
        user_identity_change: dict[str, Any] | None = None,
        payload_encryption: dict[str, Any] | None = None,
        storage_configuration: dict[str, Any] | None = None,
        phone_number_id: str | None = None,
    ) -> dict[str, Any]:
        body = clean_body(
            dict(
                calling=calling,
                user_identity_change=user_identity_change,
                payload_encryption=payload_encryption,
                storage_configuration=storage_configuration,
            )
        )
        if not body:
            raise ValueError("at least one settings group is required")
        return await self._req(
            ApiRequest("POST", f"{self._pnid(phone_number_id)}/settings", json=body)
        )

    async def get_official_status(
        self, *, phone_number_id: str | None = None, fields: Sequence[str] | str | None = None
    ) -> dict[str, Any]:
        return await self._req(
            ApiRequest(
                "GET",
                f"{self._pnid(phone_number_id)}/official_business_account",
                params=clean_params({"fields": merge_fields(fields)}),
            )
        )

    async def update_official_status(self, *, phone_number_id: str | None = None) -> dict[str, Any]:
        return await self._req(
            ApiRequest("POST", f"{self._pnid(phone_number_id)}/official_business_account", json={})
        )
