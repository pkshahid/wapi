"""Message Template API — ``/{waba-id}/message_templates``."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from whatsapp_cloud.http import ApiRequest, clean_body, clean_params, merge_fields
from whatsapp_cloud.types.templates import Template, TemplateCreated

from .base import AsyncResource, Resource

__all__ = ["AsyncTemplates", "Templates"]


def _list_params(kw: dict[str, Any]) -> dict[str, Any] | None:
    kw["fields"] = merge_fields(kw.get("fields"))
    return clean_params(kw)


def _create_body(kw: dict[str, Any]) -> dict[str, Any]:
    return clean_body(kw)


class Templates(Resource):
    """Create, list, edit, delete and migrate message templates."""

    def list(
        self,
        *,
        fields: Sequence[str] | str | None = None,
        status: str | None = None,
        category: str | None = None,
        content: str | None = None,
        language: str | None = None,
        name: str | None = None,
        quality_score: str | None = None,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
        waba_id: str | None = None,
    ) -> Any:
        """Iterate templates (auto-paginates)."""
        spec = ApiRequest(
            "GET",
            f"{self._waba(waba_id)}/message_templates",
            params=_list_params(
                dict(
                    fields=fields,
                    status=status,
                    category=category,
                    content=content,
                    language=language,
                    name=name,
                    quality_score=quality_score,
                    limit=limit,
                    after=after,
                    before=before,
                )
            ),
        )
        return self._page(spec, Template.model_validate)

    def get(self, template_id: str, *, fields: Sequence[str] | str | None = None) -> Template:
        spec = ApiRequest(
            "GET",
            template_id,
            params=clean_params({"fields": merge_fields(fields)}),
            into=Template.model_validate,
        )
        return self._req(spec)

    def create(
        self,
        *,
        name: str,
        language: str,
        category: str,
        components: Sequence[dict[str, Any]],
        parameter_format: str | None = None,
        allow_category_change: bool | None = None,
        cta_url_link_tracking_opted_out: bool | None = None,
        message_send_ttl_seconds: int | None = None,
        sub_category: str | None = None,
        display_format: str | None = None,
        library_template_name: str | None = None,
        library_template_body_inputs: dict[str, Any] | None = None,
        library_template_button_inputs: Sequence[dict[str, Any]] | None = None,
        is_primary_device_delivery_only: bool | None = None,
        send_type: str | None = None,
        waba_id: str | None = None,
    ) -> TemplateCreated:
        body = _create_body(
            dict(
                name=name,
                language=language,
                category=category,
                components=components,
                parameter_format=parameter_format,
                allow_category_change=allow_category_change,
                cta_url_link_tracking_opted_out=cta_url_link_tracking_opted_out,
                message_send_ttl_seconds=message_send_ttl_seconds,
                sub_category=sub_category,
                display_format=display_format,
                library_template_name=library_template_name,
                library_template_body_inputs=library_template_body_inputs,
                library_template_button_inputs=library_template_button_inputs,
                is_primary_device_delivery_only=is_primary_device_delivery_only,
                send_type=send_type,
            )
        )
        spec = ApiRequest(
            "POST",
            f"{self._waba(waba_id)}/message_templates",
            json=body,
            into=TemplateCreated.model_validate,
        )
        return self._req(spec)

    def edit(
        self,
        template_id: str,
        *,
        components: Sequence[dict[str, Any]] | None = None,
        category: str | None = None,
        parameter_format: str | None = None,
        allow_category_change: bool | None = None,
        cta_url_link_tracking_opted_out: bool | None = None,
        message_send_ttl_seconds: int | None = None,
        sub_category: str | None = None,
        display_format: str | None = None,
        is_primary_device_delivery_only: bool | None = None,
    ) -> dict[str, Any]:
        body = _create_body(
            dict(
                components=components,
                category=category,
                parameter_format=parameter_format,
                allow_category_change=allow_category_change,
                cta_url_link_tracking_opted_out=cta_url_link_tracking_opted_out,
                message_send_ttl_seconds=message_send_ttl_seconds,
                sub_category=sub_category,
                display_format=display_format,
                is_primary_device_delivery_only=is_primary_device_delivery_only,
            )
        )
        return self._req(ApiRequest("POST", template_id, json=body))

    def delete(
        self,
        *,
        name: str | None = None,
        hsm_id: str | None = None,
        hsm_ids: Sequence[str] | None = None,
        waba_id: str | None = None,
    ) -> dict[str, Any]:
        """Delete by ``name`` (all languages), ``name`` + ``hsm_id`` (one
        language), or ``hsm_ids`` (up to 100 templates)."""
        params = clean_params({"name": name, "hsm_id": hsm_id, "hsm_ids": hsm_ids})
        return self._req(
            ApiRequest("DELETE", f"{self._waba(waba_id)}/message_templates", params=params)
        )

    def migrate(
        self,
        *,
        source_waba_id: str,
        template_names: Sequence[str] | None = None,
        waba_id: str | None = None,
    ) -> dict[str, Any]:
        """Copy templates from another WABA owned by the same business."""
        params = clean_params(
            {"source_waba_id": source_waba_id, "source_template_names": template_names}
        )
        return self._req(
            ApiRequest("POST", f"{self._waba(waba_id)}/migrate_message_templates", params=params)
        )


class AsyncTemplates(AsyncResource):
    """Async variant of :class:`Templates`."""

    def list(
        self,
        *,
        fields: Sequence[str] | str | None = None,
        status: str | None = None,
        category: str | None = None,
        content: str | None = None,
        language: str | None = None,
        name: str | None = None,
        quality_score: str | None = None,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
        waba_id: str | None = None,
    ) -> Any:
        spec = ApiRequest(
            "GET",
            f"{self._waba(waba_id)}/message_templates",
            params=_list_params(
                dict(
                    fields=fields,
                    status=status,
                    category=category,
                    content=content,
                    language=language,
                    name=name,
                    quality_score=quality_score,
                    limit=limit,
                    after=after,
                    before=before,
                )
            ),
        )
        return self._page(spec, Template.model_validate)

    async def get(self, template_id: str, *, fields: Sequence[str] | str | None = None) -> Template:
        spec = ApiRequest(
            "GET",
            template_id,
            params=clean_params({"fields": merge_fields(fields)}),
            into=Template.model_validate,
        )
        return await self._req(spec)

    async def create(
        self,
        *,
        name: str,
        language: str,
        category: str,
        components: Sequence[dict[str, Any]],
        parameter_format: str | None = None,
        allow_category_change: bool | None = None,
        cta_url_link_tracking_opted_out: bool | None = None,
        message_send_ttl_seconds: int | None = None,
        sub_category: str | None = None,
        display_format: str | None = None,
        library_template_name: str | None = None,
        library_template_body_inputs: dict[str, Any] | None = None,
        library_template_button_inputs: Sequence[dict[str, Any]] | None = None,
        is_primary_device_delivery_only: bool | None = None,
        send_type: str | None = None,
        waba_id: str | None = None,
    ) -> TemplateCreated:
        body = _create_body(
            dict(
                name=name,
                language=language,
                category=category,
                components=components,
                parameter_format=parameter_format,
                allow_category_change=allow_category_change,
                cta_url_link_tracking_opted_out=cta_url_link_tracking_opted_out,
                message_send_ttl_seconds=message_send_ttl_seconds,
                sub_category=sub_category,
                display_format=display_format,
                library_template_name=library_template_name,
                library_template_body_inputs=library_template_body_inputs,
                library_template_button_inputs=library_template_button_inputs,
                is_primary_device_delivery_only=is_primary_device_delivery_only,
                send_type=send_type,
            )
        )
        spec = ApiRequest(
            "POST",
            f"{self._waba(waba_id)}/message_templates",
            json=body,
            into=TemplateCreated.model_validate,
        )
        return await self._req(spec)

    async def edit(
        self,
        template_id: str,
        *,
        components: Sequence[dict[str, Any]] | None = None,
        category: str | None = None,
        parameter_format: str | None = None,
        allow_category_change: bool | None = None,
        cta_url_link_tracking_opted_out: bool | None = None,
        message_send_ttl_seconds: int | None = None,
        sub_category: str | None = None,
        display_format: str | None = None,
        is_primary_device_delivery_only: bool | None = None,
    ) -> dict[str, Any]:
        body = _create_body(
            dict(
                components=components,
                category=category,
                parameter_format=parameter_format,
                allow_category_change=allow_category_change,
                cta_url_link_tracking_opted_out=cta_url_link_tracking_opted_out,
                message_send_ttl_seconds=message_send_ttl_seconds,
                sub_category=sub_category,
                display_format=display_format,
                is_primary_device_delivery_only=is_primary_device_delivery_only,
            )
        )
        return await self._req(ApiRequest("POST", template_id, json=body))

    async def delete(
        self,
        *,
        name: str | None = None,
        hsm_id: str | None = None,
        hsm_ids: Sequence[str] | None = None,
        waba_id: str | None = None,
    ) -> dict[str, Any]:
        params = clean_params({"name": name, "hsm_id": hsm_id, "hsm_ids": hsm_ids})
        return await self._req(
            ApiRequest("DELETE", f"{self._waba(waba_id)}/message_templates", params=params)
        )

    async def migrate(
        self,
        *,
        source_waba_id: str,
        template_names: Sequence[str] | None = None,
        waba_id: str | None = None,
    ) -> dict[str, Any]:
        params = clean_params(
            {"source_waba_id": source_waba_id, "source_template_names": template_names}
        )
        return await self._req(
            ApiRequest("POST", f"{self._waba(waba_id)}/migrate_message_templates", params=params)
        )
