"""WABA node: details, analytics fields, activities, schedules, subscribed apps."""

from __future__ import annotations

from typing import Any

from whatsapp_business_cloud.http import (
    ApiRequest,
    clean_body,
    clean_params,
    dump_json_field,
    merge_fields,
)
from whatsapp_business_cloud.types.waba import Activity, Schedule, SubscribedApp, Waba

from .base import AsyncResource, Resource

__all__ = ["AsyncWabaResource", "WabaResource"]


def _analytics_fields(**kw: Any) -> str:
    """Build the ``analytics.start(...).end(...)...`` fields expression."""
    parts = []
    for key, value in kw.items():
        if value is None:
            continue
        if isinstance(value, list):
            value = (
                "["
                + ",".join(dump_json_field(v) if isinstance(v, str) else str(v) for v in value)
                + "]"
            )
        elif not isinstance(value, str):
            value = str(value)
        parts.append(f"{key}({value})")
    return "analytics." + ".".join(parts)


class WabaResource(Resource):
    """Operations on the WhatsApp Business Account node."""

    def get(self, *, fields: list[str] | str | None = None, waba_id: str | None = None) -> Waba:
        spec = ApiRequest(
            "GET",
            self._waba(waba_id),
            params=clean_params({"fields": merge_fields(fields)}),
            into=Waba.model_validate,
        )
        return self._req(spec)

    def update(
        self, *, name: str | None = None, timezone_id: str | None = None, waba_id: str | None = None
    ) -> dict[str, Any]:
        return self._req(
            ApiRequest(
                "POST",
                self._waba(waba_id),
                json=clean_body({"name": name, "timezone_id": timezone_id}),
            )
        )

    def analytics(
        self,
        *,
        start: int,
        end: int,
        granularity: str,
        phone_numbers: list[str] | None = None,
        metric_types: list[str] | None = None,
        waba_id: str | None = None,
    ) -> dict[str, Any]:
        """Conversation analytics (cost/volume) for the WABA."""
        return self._req(
            ApiRequest(
                "GET",
                self._waba(waba_id),
                params={
                    "fields": _analytics_fields(
                        start=start,
                        end=end,
                        granularity=granularity,
                        phone_numbers=phone_numbers,
                        metric_types=metric_types,
                    )
                },
            )
        )

    def template_analytics(
        self,
        *,
        start: int,
        end: int,
        granularity: str,
        template_ids: list[str] | None = None,
        waba_id: str | None = None,
    ) -> dict[str, Any]:
        """Per-template send/deliver/read/click metrics."""
        expr = "template_analytics." + ".".join(
            [f"start({start})", f"end({end})", f"granularity({granularity})"]
            + (["template_ids[" + ",".join(template_ids) + "]"] if template_ids else [])
        )
        return self._req(ApiRequest("GET", self._waba(waba_id), params={"fields": expr}))

    def activities(
        self,
        *,
        fields: list[str] | str | None = None,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
        waba_id: str | None = None,
    ) -> Any:
        spec = ApiRequest(
            "GET",
            f"{self._waba(waba_id)}/activities",
            params=clean_params(
                dict(fields=merge_fields(fields), limit=limit, after=after, before=before)
            ),
        )
        return self._page(spec, Activity.model_validate)

    # --- schedules (template campaigns) --------------------------------------

    def list_schedules(
        self,
        *,
        fields: list[str] | str | None = None,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
        waba_id: str | None = None,
    ) -> Any:
        spec = ApiRequest(
            "GET",
            f"{self._waba(waba_id)}/schedules",
            params=clean_params(
                dict(fields=merge_fields(fields), limit=limit, after=after, before=before)
            ),
        )
        return self._page(spec, Schedule.model_validate)

    def create_schedule(
        self,
        *,
        hsm_id: str,
        delivery_time: int,
        audience_id: str | None = None,
        waba_cs_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        waba_id: str | None = None,
    ) -> dict[str, Any]:
        body = clean_body(
            dict(
                hsm_id=hsm_id,
                delivery_time=delivery_time,
                audience_id=audience_id,
                waba_cs_id=waba_cs_id,
                name=name,
                description=description,
            )
        )
        return self._req(ApiRequest("POST", f"{self._waba(waba_id)}/schedules", json=body))

    # --- webhook app subscription ---------------------------------------------

    def subscribed_apps(self, *, waba_id: str | None = None) -> list[SubscribedApp]:
        body = self._req(ApiRequest("GET", f"{self._waba(waba_id)}/subscribed_apps"))
        return [SubscribedApp.model_validate(a) for a in body.get("data") or []]

    def subscribe_app(
        self,
        *,
        override_callback_uri: str | None = None,
        verify_token: str | None = None,
        waba_id: str | None = None,
    ) -> dict[str, Any]:
        """Subscribe the calling app to this WABA's webhooks (optionally
        overriding the app's default callback URL)."""
        body = clean_body(
            dict(override_callback_uri=override_callback_uri, verify_token=verify_token)
        )
        return self._req(ApiRequest("POST", f"{self._waba(waba_id)}/subscribed_apps", json=body))

    def unsubscribe_app(self, *, waba_id: str | None = None) -> dict[str, Any]:
        return self._req(ApiRequest("DELETE", f"{self._waba(waba_id)}/subscribed_apps"))


class AsyncWabaResource(AsyncResource):
    """Async variant of :class:`WabaResource`."""

    async def get(
        self, *, fields: list[str] | str | None = None, waba_id: str | None = None
    ) -> Waba:
        spec = ApiRequest(
            "GET",
            self._waba(waba_id),
            params=clean_params({"fields": merge_fields(fields)}),
            into=Waba.model_validate,
        )
        return await self._req(spec)

    async def update(
        self, *, name: str | None = None, timezone_id: str | None = None, waba_id: str | None = None
    ) -> dict[str, Any]:
        return await self._req(
            ApiRequest(
                "POST",
                self._waba(waba_id),
                json=clean_body({"name": name, "timezone_id": timezone_id}),
            )
        )

    async def analytics(
        self,
        *,
        start: int,
        end: int,
        granularity: str,
        phone_numbers: list[str] | None = None,
        metric_types: list[str] | None = None,
        waba_id: str | None = None,
    ) -> dict[str, Any]:
        return await self._req(
            ApiRequest(
                "GET",
                self._waba(waba_id),
                params={
                    "fields": _analytics_fields(
                        start=start,
                        end=end,
                        granularity=granularity,
                        phone_numbers=phone_numbers,
                        metric_types=metric_types,
                    )
                },
            )
        )

    async def template_analytics(
        self,
        *,
        start: int,
        end: int,
        granularity: str,
        template_ids: list[str] | None = None,
        waba_id: str | None = None,
    ) -> dict[str, Any]:
        expr = "template_analytics." + ".".join(
            [f"start({start})", f"end({end})", f"granularity({granularity})"]
            + (["template_ids[" + ",".join(template_ids) + "]"] if template_ids else [])
        )
        return await self._req(ApiRequest("GET", self._waba(waba_id), params={"fields": expr}))

    def activities(
        self,
        *,
        fields: list[str] | str | None = None,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
        waba_id: str | None = None,
    ) -> Any:
        spec = ApiRequest(
            "GET",
            f"{self._waba(waba_id)}/activities",
            params=clean_params(
                dict(fields=merge_fields(fields), limit=limit, after=after, before=before)
            ),
        )
        return self._page(spec, Activity.model_validate)

    def list_schedules(
        self,
        *,
        fields: list[str] | str | None = None,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
        waba_id: str | None = None,
    ) -> Any:
        spec = ApiRequest(
            "GET",
            f"{self._waba(waba_id)}/schedules",
            params=clean_params(
                dict(fields=merge_fields(fields), limit=limit, after=after, before=before)
            ),
        )
        return self._page(spec, Schedule.model_validate)

    async def create_schedule(
        self,
        *,
        hsm_id: str,
        delivery_time: int,
        audience_id: str | None = None,
        waba_cs_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        waba_id: str | None = None,
    ) -> dict[str, Any]:
        body = clean_body(
            dict(
                hsm_id=hsm_id,
                delivery_time=delivery_time,
                audience_id=audience_id,
                waba_cs_id=waba_cs_id,
                name=name,
                description=description,
            )
        )
        return await self._req(ApiRequest("POST", f"{self._waba(waba_id)}/schedules", json=body))

    async def subscribed_apps(self, *, waba_id: str | None = None) -> list[SubscribedApp]:
        body = await self._req(ApiRequest("GET", f"{self._waba(waba_id)}/subscribed_apps"))
        return [SubscribedApp.model_validate(a) for a in body.get("data") or []]

    async def subscribe_app(
        self,
        *,
        override_callback_uri: str | None = None,
        verify_token: str | None = None,
        waba_id: str | None = None,
    ) -> dict[str, Any]:
        body = clean_body(
            dict(override_callback_uri=override_callback_uri, verify_token=verify_token)
        )
        return await self._req(
            ApiRequest("POST", f"{self._waba(waba_id)}/subscribed_apps", json=body)
        )

    async def unsubscribe_app(self, *, waba_id: str | None = None) -> dict[str, Any]:
        return await self._req(ApiRequest("DELETE", f"{self._waba(waba_id)}/subscribed_apps"))
