"""Flows management API — ``/{waba-id}/flows`` and ``/{flow-id}/*``."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from wapi.http import ApiRequest, clean_body, clean_params, merge_fields
from wapi.types.flows import Flow, FlowCreated, FlowMigrationResult

from .base import AsyncResource, Resource

__all__ = ["AsyncFlows", "Flows"]


class Flows(Resource):
    """Create, update, publish, deprecate, and migrate WhatsApp Flows."""

    def list(
        self,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
        waba_id: str | None = None,
    ) -> Any:
        spec = ApiRequest(
            "GET",
            f"{self._waba(waba_id)}/flows",
            params=clean_params({"limit": limit, "after": after, "before": before}),
        )
        return self._page(spec, Flow.model_validate)

    def create(
        self,
        *,
        name: str,
        categories: Sequence[str],
        flow_json: str | dict[str, Any] | None = None,
        publish: bool | None = None,
        clone_flow_id: str | None = None,
        endpoint_uri: str | None = None,
        waba_id: str | None = None,
    ) -> FlowCreated:
        import json as _json

        if isinstance(flow_json, dict):
            flow_json = _json.dumps(flow_json)
        body = clean_body(
            dict(
                name=name,
                categories=categories,
                flow_json=flow_json,
                publish=publish,
                clone_flow_id=clone_flow_id,
                endpoint_uri=endpoint_uri,
            )
        )
        spec = ApiRequest(
            "POST", f"{self._waba(waba_id)}/flows", json=body, into=FlowCreated.model_validate
        )
        return self._req(spec)

    def get(self, flow_id: str, *, fields: Sequence[str] | str | None = None) -> Flow:
        spec = ApiRequest(
            "GET",
            flow_id,
            params=clean_params({"fields": merge_fields(fields)}),
            into=Flow.model_validate,
        )
        return self._req(spec)

    def update(
        self,
        flow_id: str,
        *,
        name: str | None = None,
        categories: Sequence[str] | None = None,
        endpoint_uri: str | None = None,
        application_id: str | None = None,
    ) -> dict[str, Any]:
        body = clean_body(
            dict(
                name=name,
                categories=categories,
                endpoint_uri=endpoint_uri,
                application_id=application_id,
            )
        )
        return self._req(ApiRequest("POST", flow_id, json=body))

    def delete(self, flow_id: str) -> dict[str, Any]:
        """Delete a DRAFT flow (published flows must be deprecated instead)."""
        return self._req(ApiRequest("DELETE", flow_id))

    def update_json(self, flow_id: str, flow_json: str | bytes | dict[str, Any]) -> dict[str, Any]:
        """Upload a new ``flow.json`` (DRAFT flows only). Returns validation errors if any."""
        import json as _json

        content: bytes
        if isinstance(flow_json, dict):
            content = _json.dumps(flow_json).encode()
        elif isinstance(flow_json, str):
            content = flow_json.encode()
        else:
            content = flow_json
        spec = ApiRequest(
            "POST",
            f"{flow_id}/assets",
            data={"name": "flow.json", "asset_type": "FLOW_JSON"},
            files={"file": ("flow.json", content, "application/json")},
        )
        return self._req(spec)

    def list_assets(self, flow_id: str) -> dict[str, Any]:
        return self._req(ApiRequest("GET", f"{flow_id}/assets"))

    def preview(self, flow_id: str, *, invalidate: bool = False) -> dict[str, Any]:
        """Get a shareable web preview URL for a flow."""
        spec = ApiRequest(
            "GET",
            flow_id,
            params={"fields": f"preview.invalidate({'true' if invalidate else 'false'})"},
        )
        return self._req(spec)

    def publish(self, flow_id: str) -> dict[str, Any]:
        return self._req(ApiRequest("POST", f"{flow_id}/publish", json={}))

    def deprecate(self, flow_id: str) -> dict[str, Any]:
        return self._req(ApiRequest("POST", f"{flow_id}/deprecate", json={}))

    def migrate(
        self,
        *,
        source_waba_id: str,
        source_flow_names: Sequence[str] | None = None,
        waba_id: str | None = None,
    ) -> FlowMigrationResult:
        """Copy flows from a source WABA into this WABA (same business)."""
        spec = ApiRequest(
            "POST",
            f"{self._waba(waba_id)}/migrate_flows",
            params=clean_params(
                {"source_waba_id": source_waba_id, "source_flow_names": source_flow_names}
            ),
            into=FlowMigrationResult.model_validate,
        )
        return self._req(spec)


class AsyncFlows(AsyncResource):
    """Async variant of :class:`Flows`."""

    def list(
        self,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
        waba_id: str | None = None,
    ) -> Any:
        spec = ApiRequest(
            "GET",
            f"{self._waba(waba_id)}/flows",
            params=clean_params({"limit": limit, "after": after, "before": before}),
        )
        return self._page(spec, Flow.model_validate)

    async def create(
        self,
        *,
        name: str,
        categories: Sequence[str],
        flow_json: str | dict[str, Any] | None = None,
        publish: bool | None = None,
        clone_flow_id: str | None = None,
        endpoint_uri: str | None = None,
        waba_id: str | None = None,
    ) -> FlowCreated:
        import json as _json

        if isinstance(flow_json, dict):
            flow_json = _json.dumps(flow_json)
        body = clean_body(
            dict(
                name=name,
                categories=categories,
                flow_json=flow_json,
                publish=publish,
                clone_flow_id=clone_flow_id,
                endpoint_uri=endpoint_uri,
            )
        )
        return await self._req(
            ApiRequest(
                "POST", f"{self._waba(waba_id)}/flows", json=body, into=FlowCreated.model_validate
            )
        )

    async def get(self, flow_id: str, *, fields: Sequence[str] | str | None = None) -> Flow:
        spec = ApiRequest(
            "GET",
            flow_id,
            params=clean_params({"fields": merge_fields(fields)}),
            into=Flow.model_validate,
        )
        return await self._req(spec)

    async def update(
        self,
        flow_id: str,
        *,
        name: str | None = None,
        categories: Sequence[str] | None = None,
        endpoint_uri: str | None = None,
        application_id: str | None = None,
    ) -> dict[str, Any]:
        body = clean_body(
            dict(
                name=name,
                categories=categories,
                endpoint_uri=endpoint_uri,
                application_id=application_id,
            )
        )
        return await self._req(ApiRequest("POST", flow_id, json=body))

    async def delete(self, flow_id: str) -> dict[str, Any]:
        return await self._req(ApiRequest("DELETE", flow_id))

    async def update_json(
        self, flow_id: str, flow_json: str | bytes | dict[str, Any]
    ) -> dict[str, Any]:
        import json as _json

        if isinstance(flow_json, dict):
            content = _json.dumps(flow_json).encode()
        elif isinstance(flow_json, str):
            content = flow_json.encode()
        else:
            content = flow_json
        return await self._req(
            ApiRequest(
                "POST",
                f"{flow_id}/assets",
                data={"name": "flow.json", "asset_type": "FLOW_JSON"},
                files={"file": ("flow.json", content, "application/json")},
            )
        )

    async def list_assets(self, flow_id: str) -> dict[str, Any]:
        return await self._req(ApiRequest("GET", f"{flow_id}/assets"))

    async def preview(self, flow_id: str, *, invalidate: bool = False) -> dict[str, Any]:
        return await self._req(
            ApiRequest(
                "GET",
                flow_id,
                params={"fields": f"preview.invalidate({'true' if invalidate else 'false'})"},
            )
        )

    async def publish(self, flow_id: str) -> dict[str, Any]:
        return await self._req(ApiRequest("POST", f"{flow_id}/publish", json={}))

    async def deprecate(self, flow_id: str) -> dict[str, Any]:
        return await self._req(ApiRequest("POST", f"{flow_id}/deprecate", json={}))

    async def migrate(
        self,
        *,
        source_waba_id: str,
        source_flow_names: Sequence[str] | None = None,
        waba_id: str | None = None,
    ) -> FlowMigrationResult:
        return await self._req(
            ApiRequest(
                "POST",
                f"{self._waba(waba_id)}/migrate_flows",
                params=clean_params(
                    {"source_waba_id": source_waba_id, "source_flow_names": source_flow_names}
                ),
                into=FlowMigrationResult.model_validate,
            )
        )
