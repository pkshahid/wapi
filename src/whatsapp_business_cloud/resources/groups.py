"""Groups API — ``/{phone-number-id}/groups`` and ``/{group-id}/*``."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from whatsapp_business_cloud.http import ApiRequest, clean_body, clean_params, merge_fields
from whatsapp_business_cloud.types.groups import Group, GroupCreated, JoinRequest

from .base import AsyncResource, Resource

__all__ = ["AsyncGroups", "Groups"]


def _group_body(**kw: Any) -> dict[str, Any]:
    return clean_body({"messaging_product": "whatsapp", **kw})


class Groups(Resource):
    """Create and manage WhatsApp groups for the business number."""

    def list(
        self,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
        phone_number_id: str | None = None,
    ) -> Any:
        spec = ApiRequest(
            "GET",
            f"{self._pnid(phone_number_id)}/groups",
            params=clean_params({"limit": limit, "after": after, "before": before}),
        )
        return self._page(spec, Group.model_validate)

    def create(
        self,
        *,
        subject: str,
        description: str | None = None,
        join_approval_mode: str | None = None,
        phone_number_id: str | None = None,
    ) -> GroupCreated:
        body = _group_body(
            subject=subject, description=description, join_approval_mode=join_approval_mode
        )
        spec = ApiRequest(
            "POST",
            f"{self._pnid(phone_number_id)}/groups",
            json=body,
            into=GroupCreated.model_validate,
        )
        return self._req(spec)

    def get(self, group_id: str, *, fields: Sequence[str] | str | None = None) -> Group:
        spec = ApiRequest(
            "GET",
            group_id,
            params=clean_params({"fields": merge_fields(fields)}),
            into=Group.model_validate,
        )
        return self._req(spec)

    def update(
        self,
        group_id: str,
        *,
        subject: str | None = None,
        description: str | None = None,
        profile_picture: str | Path | bytes | None = None,
        profile_picture_file: str | None = None,
    ) -> dict[str, Any]:
        """Update subject/description; set picture via ``profile_picture``
        (path/bytes → multipart) or a server-side ``profile_picture_file`` path."""
        if profile_picture is not None:
            import mimetypes

            name = getattr(profile_picture, "name", None) or "picture.jpg"
            if isinstance(profile_picture, (str, Path)):
                p = Path(profile_picture)
                content = p.read_bytes()
                name = p.name
            else:
                content = profile_picture
            spec = ApiRequest(
                "POST",
                group_id,
                data={"messaging_product": "whatsapp"},
                files={"file": (name, content, mimetypes.guess_type(str(name))[0] or "image/jpeg")},
            )
            return self._req(spec)
        body = _group_body(
            subject=subject, description=description, profile_picture_file=profile_picture_file
        )
        return self._req(ApiRequest("POST", group_id, json=body))

    def delete(self, group_id: str) -> dict[str, Any]:
        return self._req(ApiRequest("DELETE", group_id))

    # --- participants -------------------------------------------------------

    def add_participants(self, group_id: str, participants: Sequence[str]) -> dict[str, Any]:
        """Add up to 8 members per call (phone numbers or WA-IDs)."""
        body = _group_body(participants=participants)
        return self._req(ApiRequest("POST", f"{group_id}/participants", json=body))

    def remove_participants(self, group_id: str, participants: Sequence[str]) -> dict[str, Any]:
        body = _group_body(participants=participants)
        return self._req(ApiRequest("DELETE", f"{group_id}/participants", json=body))

    # --- invite links --------------------------------------------------------

    def create_invite_link(self, group_id: str) -> dict[str, Any]:
        return self._req(ApiRequest("POST", f"{group_id}/invite_link", json={}))

    def revoke_invite_link(self, group_id: str) -> dict[str, Any]:
        return self._req(ApiRequest("DELETE", f"{group_id}/invite_link"))

    # --- join requests --------------------------------------------------------

    def list_join_requests(self, group_id: str) -> Any:
        spec = ApiRequest("GET", f"{group_id}/join_requests")
        return self._page(spec, JoinRequest.model_validate)

    def approve_join_requests(self, group_id: str, request_ids: Sequence[str]) -> dict[str, Any]:
        return self._req(
            ApiRequest(
                "POST", f"{group_id}/join_requests", json=_group_body(join_requests=request_ids)
            )
        )

    def reject_join_requests(self, group_id: str, request_ids: Sequence[str]) -> dict[str, Any]:
        return self._req(
            ApiRequest(
                "DELETE", f"{group_id}/join_requests", json=_group_body(join_requests=request_ids)
            )
        )


class AsyncGroups(AsyncResource):
    """Async variant of :class:`Groups`."""

    def list(
        self,
        *,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
        phone_number_id: str | None = None,
    ) -> Any:
        spec = ApiRequest(
            "GET",
            f"{self._pnid(phone_number_id)}/groups",
            params=clean_params({"limit": limit, "after": after, "before": before}),
        )
        return self._page(spec, Group.model_validate)

    async def create(
        self,
        *,
        subject: str,
        description: str | None = None,
        join_approval_mode: str | None = None,
        phone_number_id: str | None = None,
    ) -> GroupCreated:
        body = _group_body(
            subject=subject, description=description, join_approval_mode=join_approval_mode
        )
        spec = ApiRequest(
            "POST",
            f"{self._pnid(phone_number_id)}/groups",
            json=body,
            into=GroupCreated.model_validate,
        )
        return await self._req(spec)

    async def get(self, group_id: str, *, fields: Sequence[str] | str | None = None) -> Group:
        spec = ApiRequest(
            "GET",
            group_id,
            params=clean_params({"fields": merge_fields(fields)}),
            into=Group.model_validate,
        )
        return await self._req(spec)

    async def update(
        self,
        group_id: str,
        *,
        subject: str | None = None,
        description: str | None = None,
        profile_picture: str | Path | bytes | None = None,
        profile_picture_file: str | None = None,
    ) -> dict[str, Any]:
        if profile_picture is not None:
            import mimetypes

            name = getattr(profile_picture, "name", None) or "picture.jpg"
            if isinstance(profile_picture, (str, Path)):
                p = Path(profile_picture)
                content = p.read_bytes()
                name = p.name
            else:
                content = profile_picture
            return await self._req(
                ApiRequest(
                    "POST",
                    group_id,
                    data={"messaging_product": "whatsapp"},
                    files={
                        "file": (name, content, mimetypes.guess_type(str(name))[0] or "image/jpeg")
                    },
                )
            )
        return await self._req(
            ApiRequest(
                "POST",
                group_id,
                json=_group_body(
                    subject=subject,
                    description=description,
                    profile_picture_file=profile_picture_file,
                ),
            )
        )

    async def delete(self, group_id: str) -> dict[str, Any]:
        return await self._req(ApiRequest("DELETE", group_id))

    async def add_participants(self, group_id: str, participants: Sequence[str]) -> dict[str, Any]:
        return await self._req(
            ApiRequest(
                "POST", f"{group_id}/participants", json=_group_body(participants=participants)
            )
        )

    async def remove_participants(
        self, group_id: str, participants: Sequence[str]
    ) -> dict[str, Any]:
        return await self._req(
            ApiRequest(
                "DELETE", f"{group_id}/participants", json=_group_body(participants=participants)
            )
        )

    async def create_invite_link(self, group_id: str) -> dict[str, Any]:
        return await self._req(ApiRequest("POST", f"{group_id}/invite_link", json={}))

    async def revoke_invite_link(self, group_id: str) -> dict[str, Any]:
        return await self._req(ApiRequest("DELETE", f"{group_id}/invite_link"))

    def list_join_requests(self, group_id: str) -> Any:
        return self._page(
            ApiRequest("GET", f"{group_id}/join_requests"), JoinRequest.model_validate
        )

    async def approve_join_requests(
        self, group_id: str, request_ids: Sequence[str]
    ) -> dict[str, Any]:
        return await self._req(
            ApiRequest(
                "POST", f"{group_id}/join_requests", json=_group_body(join_requests=request_ids)
            )
        )

    async def reject_join_requests(
        self, group_id: str, request_ids: Sequence[str]
    ) -> dict[str, Any]:
        return await self._req(
            ApiRequest(
                "DELETE", f"{group_id}/join_requests", json=_group_body(join_requests=request_ids)
            )
        )
