"""``Client`` and ``AsyncClient`` — entry points to the WhatsApp Business Platform."""

from __future__ import annotations

from typing import Any, TypeVar

import httpx

from .http import (
    DEFAULT_API_VERSION,
    DEFAULT_BASE_URL,
    ApiRequest,
    Files,
    RetryPolicy,
    arequest_with_retry,
    auth_headers,
    build_url,
    handle_response,
    request_with_retry,
)
from .pagination import AsyncCursorIterator, CursorIterator
from .resources import (
    AsyncAutomation,
    AsyncBlockedUsers,
    AsyncCalls,
    AsyncCommerce,
    AsyncCompliance,
    AsyncEncryption,
    AsyncFlows,
    AsyncGroups,
    AsyncMarketing,
    AsyncMedia,
    AsyncMessages,
    AsyncPhoneNumbers,
    AsyncProfile,
    AsyncQRCodes,
    AsyncTemplates,
    AsyncWabaResource,
    Automation,
    BlockedUsers,
    Calls,
    Commerce,
    Compliance,
    Encryption,
    Flows,
    Groups,
    Marketing,
    Media,
    Messages,
    PhoneNumbers,
    Profile,
    QRCodes,
    Templates,
    WabaResource,
)

__all__ = ["AsyncClient", "Client"]

T = TypeVar("T")


class _BaseClient:
    """Configuration shared by both clients."""

    def __init__(
        self,
        access_token: str,
        *,
        phone_number_id: str | None = None,
        waba_id: str | None = None,
        app_id: str | None = None,
        api_version: str = DEFAULT_API_VERSION,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        max_retries: int = 3,
        user_agent: str | None = None,
    ) -> None:
        if not access_token:
            raise ValueError("access_token is required")
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.waba_id = waba_id
        self.app_id = app_id
        self.api_version = api_version
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retry = RetryPolicy(max_retries=max_retries)
        self.user_agent = user_agent or f"whatsapp-cloud/0.1 ({api_version})"

    def _headers(self) -> dict[str, str]:
        return auth_headers(self.access_token) | {"User-Agent": self.user_agent}


class Client(_BaseClient):
    """Synchronous WhatsApp Business Platform client.

    ::

        client = Client("EAAB...", phone_number_id="106540...", waba_id="102290...")
        resp = client.messages.send_text(to="15551234567", body="Hello!")
    """

    def __init__(
        self, access_token: str, *, http_client: httpx.Client | None = None, **kw: Any
    ) -> None:
        super().__init__(access_token, **kw)
        self._http = http_client or httpx.Client(timeout=self.timeout)
        self._owns_http = http_client is None

        self.messages = Messages(self)
        self.marketing = Marketing(self)
        self.media = Media(self)
        self.templates = Templates(self)
        self.phone_numbers = PhoneNumbers(self)
        self.profile = Profile(self)
        self.commerce = Commerce(self)
        self.compliance = Compliance(self)
        self.automation = Automation(self)
        self.encryption = Encryption(self)
        self.qr_codes = QRCodes(self)
        self.blocked = BlockedUsers(self)
        self.calls = Calls(self)
        self.groups = Groups(self)
        self.flows = Flows(self)
        self.waba = WabaResource(self)

    # --- transport -----------------------------------------------------------

    def _execute(self, spec: ApiRequest[T]) -> T:
        url = build_url(self.base_url, self.api_version, spec)
        response = request_with_retry(
            self._http, url=url, req=spec, headers=self._headers(), retry=self.retry
        )
        if spec.raw:
            return response  # type: ignore[return-value]
        body = handle_response(response)
        return spec.into(body) if spec.into else body  # type: ignore[return-value]

    def _cursor(self, spec: ApiRequest[Any], decode: Any) -> CursorIterator[Any]:
        def fetch(params: dict[str, Any] | None, url: str | None) -> dict[str, Any]:
            target: ApiRequest[Any] = ApiRequest(
                spec.method,
                url if url else spec.path,
                params=params or spec.params,
                absolute=bool(url),
            )
            return self._execute(target)

        return CursorIterator(fetch, params=spec.params, decode=decode)

    def _download(self, url: str) -> bytes:
        response = self._http.get(url, headers=self._headers())
        if not response.is_success:
            handle_response(response)  # raises ApiError
        return response.content

    def _resumable_upload(self, file: Any, *, mime_type: str | None, app_id: str | None) -> str:
        """Resumable Upload API — returns an ``h:`` asset handle."""
        app = app_id or self.app_id
        if not app:
            raise ValueError("app_id required for resumable uploads")
        name, content, guessed = Files.open(file, None)
        data = content if isinstance(content, bytes) else content.read()
        session: dict[str, Any] = self._execute(
            ApiRequest(
                "POST",
                f"{app}/uploads",
                params={
                    "file_name": name,
                    "file_length": len(data),
                    "file_type": mime_type or guessed or "application/octet-stream",
                },
            )
        )
        upload_id = session["id"]
        response = self._http.post(
            f"{self.base_url}/{self.api_version}/{upload_id}",
            headers={
                "Authorization": f"OAuth {self.access_token}",
                "file_offset": "0",
                "User-Agent": self.user_agent,
            },
            content=data,
        )
        body = handle_response(response)
        return str(body["h"])

    # --- escape hatches --------------------------------------------------------

    def raw_request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        absolute: bool = False,
    ) -> dict[str, Any]:
        """Call any Graph API endpoint not yet covered by a resource."""
        return self._execute(
            ApiRequest(
                method, path, params=params, json=json, data=data, files=files, absolute=absolute
            )
        )

    # --- lifecycle -------------------------------------------------------------

    def close(self) -> None:
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


class AsyncClient(_BaseClient):
    """Asynchronous variant of :class:`Client` — same resources, awaited calls.

    ::

        async with AsyncClient("EAAB...", phone_number_id="...") as client:
            await client.messages.send_text(to="1555...", body="hi")
    """

    def __init__(
        self, access_token: str, *, http_client: httpx.AsyncClient | None = None, **kw: Any
    ) -> None:
        super().__init__(access_token, **kw)
        self._http = http_client or httpx.AsyncClient(timeout=self.timeout)
        self._owns_http = http_client is None

        self.messages = AsyncMessages(self)
        self.marketing = AsyncMarketing(self)
        self.media = AsyncMedia(self)
        self.templates = AsyncTemplates(self)
        self.phone_numbers = AsyncPhoneNumbers(self)
        self.profile = AsyncProfile(self)
        self.commerce = AsyncCommerce(self)
        self.compliance = AsyncCompliance(self)
        self.automation = AsyncAutomation(self)
        self.encryption = AsyncEncryption(self)
        self.qr_codes = AsyncQRCodes(self)
        self.blocked = AsyncBlockedUsers(self)
        self.calls = AsyncCalls(self)
        self.groups = AsyncGroups(self)
        self.flows = AsyncFlows(self)
        self.waba = AsyncWabaResource(self)

    async def _execute(self, spec: ApiRequest[T]) -> T:
        url = build_url(self.base_url, self.api_version, spec)
        response = await arequest_with_retry(
            self._http, url=url, req=spec, headers=self._headers(), retry=self.retry
        )
        if spec.raw:
            return response  # type: ignore[return-value]
        body = handle_response(response)
        return spec.into(body) if spec.into else body  # type: ignore[return-value]

    def _cursor(self, spec: ApiRequest[Any], decode: Any) -> AsyncCursorIterator[Any]:
        async def fetch(params: dict[str, Any] | None, url: str | None) -> dict[str, Any]:
            target: ApiRequest[Any] = ApiRequest(
                spec.method,
                url if url else spec.path,
                params=params or spec.params,
                absolute=bool(url),
            )
            return await self._execute(target)

        return AsyncCursorIterator(fetch, params=spec.params, decode=decode)

    async def _download(self, url: str) -> bytes:
        response = await self._http.get(url, headers=self._headers())
        if not response.is_success:
            handle_response(response)  # raises ApiError
        return response.content

    async def _resumable_upload(
        self, file: Any, *, mime_type: str | None, app_id: str | None
    ) -> str:
        app = app_id or self.app_id
        if not app:
            raise ValueError("app_id required for resumable uploads")
        name, content, guessed = Files.open(file, None)
        data = content if isinstance(content, bytes) else content.read()
        session: dict[str, Any] = await self._execute(
            ApiRequest(
                "POST",
                f"{app}/uploads",
                params={
                    "file_name": name,
                    "file_length": len(data),
                    "file_type": mime_type or guessed or "application/octet-stream",
                },
            )
        )
        upload_id = session["id"]
        response = await self._http.post(
            f"{self.base_url}/{self.api_version}/{upload_id}",
            headers={
                "Authorization": f"OAuth {self.access_token}",
                "file_offset": "0",
                "User-Agent": self.user_agent,
            },
            content=data,
        )
        body = handle_response(response)
        return str(body["h"])

    async def raw_request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        absolute: bool = False,
    ) -> dict[str, Any]:
        return await self._execute(
            ApiRequest(
                method, path, params=params, json=json, data=data, files=files, absolute=absolute
            )
        )

    async def close(self) -> None:
        if self._owns_http:
            await self._http.aclose()

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()
