"""Base classes shared by all API resources."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from whatsapp_cloud.client import AsyncClient, Client
    from whatsapp_cloud.http import ApiRequest

T = TypeVar("T")


class Resource:
    """Sync resource bound to a :class:`whatsapp_cloud.Client`."""

    def __init__(self, client: Client) -> None:
        self._c = client

    def _req(self, spec: ApiRequest[T]) -> T:
        return self._c._execute(spec)

    def _page(
        self,
        spec: ApiRequest[Any],
        decode: Any,
    ) -> Any:
        return self._c._cursor(spec, decode)

    def _pnid(self, phone_number_id: str | None) -> str:
        value = phone_number_id or self._c.phone_number_id
        if not value:
            raise ValueError("phone_number_id required — pass it here or to the Client constructor")
        return value

    def _waba(self, waba_id: str | None) -> str:
        value = waba_id or self._c.waba_id
        if not value:
            raise ValueError("waba_id required — pass it here or to the Client constructor")
        return value


class AsyncResource:
    """Async resource bound to an :class:`whatsapp_cloud.AsyncClient`."""

    def __init__(self, client: AsyncClient) -> None:
        self._c = client

    async def _req(self, spec: ApiRequest[T]) -> T:
        return await self._c._execute(spec)

    def _page(self, spec: ApiRequest[Any], decode: Any) -> Any:
        return self._c._cursor(spec, decode)

    def _pnid(self, phone_number_id: str | None) -> str:
        value = phone_number_id or self._c.phone_number_id
        if not value:
            raise ValueError("phone_number_id required — pass it here or to the Client constructor")
        return value

    def _waba(self, waba_id: str | None) -> str:
        value = waba_id or self._c.waba_id
        if not value:
            raise ValueError("waba_id required — pass it here or to the Client constructor")
        return value
