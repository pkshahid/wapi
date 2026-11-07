"""Transport layer: request specs, retry policy, response handling.

Resource methods build :class:`ApiRequest` objects; the client executes them.
This module knows nothing about WhatsApp resources — only HTTP mechanics.
"""

from __future__ import annotations

import json
import random
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

import httpx

from .exceptions import ApiError, error_from_response, is_retryable

T = TypeVar("T", default=dict[str, Any])
Decoder = Callable[[dict[str, Any]], T]

DEFAULT_BASE_URL = "https://graph.facebook.com"
DEFAULT_API_VERSION = "v25.0"


@dataclass
class ApiRequest(Generic[T]):
    """A single Graph API call to execute.

    ``into`` optionally decodes the JSON body into a typed result.
    ``raw=True`` returns the :class:`httpx.Response` untouched (downloads).
    """

    method: str
    path: str  # path after "/{version}/", e.g. "{Phone-Number-ID}/messages"
    params: dict[str, Any] | None = None
    json: Any = None
    data: dict[str, Any] | None = None  # form fields (multipart)
    files: dict[str, Any] | None = None  # multipart files
    headers: dict[str, str] | None = None
    absolute: bool = False  # path is a full URL (media download / OAuth)
    into: Decoder[T] | None = None
    raw: bool = False


@dataclass
class RetryPolicy:
    """Exponential backoff with jitter for retryable failures."""

    max_retries: int = 3
    base_delay: float = 0.5
    max_delay: float = 30.0

    def delay_for(self, attempt: int, retry_after: float | None) -> float:
        if retry_after is not None:
            return min(float(retry_after), self.max_delay)
        backoff = min(self.base_delay * (2**attempt), self.max_delay)
        return float(backoff * (0.5 + random.random() * 0.5))


def _retry_after(headers: httpx.Headers) -> float | None:
    value = headers.get("Retry-After")
    if value and value.isdigit():
        return float(value)
    return None


def handle_response(response: httpx.Response) -> dict[str, Any]:
    """Decode a Graph API response or raise the mapped :class:`ApiError`."""
    if response.is_success:
        if not response.content:
            return {}
        try:
            body = response.json()
        except json.JSONDecodeError:
            body = {"raw": response.text}
        return body if isinstance(body, dict) else {"data": body}
    payload: dict[str, Any]
    try:
        parsed = response.json()
        payload = parsed if isinstance(parsed, dict) else {"data": parsed}
    except json.JSONDecodeError:
        payload = {"error": {"message": response.text or f"HTTP {response.status_code}"}}
    raise error_from_response(response.status_code, payload, _retry_after(response.headers))


def build_url(base_url: str, api_version: str, req: ApiRequest[Any]) -> str:
    if req.absolute:
        return req.path
    return f"{base_url}/{api_version}/{req.path.lstrip('/')}"


def auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


class _Sleep:
    """Indirection so tests can monkeypatch sleeping."""

    def __call__(self, seconds: float) -> None:
        time.sleep(seconds)


sleep: Callable[[float], None] = _Sleep()


def request_with_retry(
    http: httpx.Client,
    *,
    url: str,
    req: ApiRequest[T],
    headers: dict[str, str],
    retry: RetryPolicy,
) -> httpx.Response:
    """Execute one request, retrying retryable failures with backoff."""
    last_exc: ApiError | None = None
    for attempt in range(retry.max_retries + 1):
        response = http.request(
            req.method,
            url,
            params=req.params,
            json=req.json,
            data=req.data,
            files=req.files,
            headers=headers | (req.headers or {}),
        )
        if response.is_success:
            return response
        try:
            raise error_from_response(
                response.status_code,
                _safe_json(response),
                _retry_after(response.headers),
            )
        except ApiError as exc:
            last_exc = exc
            if attempt >= retry.max_retries or not is_retryable(exc):
                raise
            sleep(retry.delay_for(attempt, exc.retry_after))
    assert last_exc is not None  # unreachable
    raise last_exc


async def arequest_with_retry(
    http: httpx.AsyncClient,
    *,
    url: str,
    req: ApiRequest[T],
    headers: dict[str, str],
    retry: RetryPolicy,
) -> httpx.Response:
    import asyncio

    last_exc: ApiError | None = None
    for attempt in range(retry.max_retries + 1):
        response = await http.request(
            req.method,
            url,
            params=req.params,
            json=req.json,
            data=req.data,
            files=req.files,
            headers=headers | (req.headers or {}),
        )
        if response.is_success:
            return response
        try:
            raise error_from_response(
                response.status_code,
                _safe_json(response),
                _retry_after(response.headers),
            )
        except ApiError as exc:
            last_exc = exc
            if attempt >= retry.max_retries or not is_retryable(exc):
                raise
            await asyncio.sleep(retry.delay_for(attempt, exc.retry_after))
    assert last_exc is not None
    raise last_exc


def _safe_json(response: httpx.Response) -> dict[str, Any]:
    try:
        parsed = response.json()
        return parsed if isinstance(parsed, dict) else {"data": parsed}
    except json.JSONDecodeError:
        return {"error": {"message": response.text or f"HTTP {response.status_code}"}}


@dataclass
class Files:
    """Helper to build httpx multipart ``files`` payloads from user input.

    Accepts a path (str/Path), raw bytes, or an open binary file object.
    """

    @staticmethod
    def open(file: Any, filename: str | None = None) -> tuple[str, Any, str | None]:
        from pathlib import Path

        if isinstance(file, (str, Path)):
            path = Path(file)
            return (path.name, path.read_bytes(), _guess_mime(path.name))
        if isinstance(file, bytes):
            return (filename or "file", file, _guess_mime(filename or ""))
        # file-like object
        name = filename or getattr(file, "name", "file") or "file"
        name = str(name).rsplit("/", 1)[-1]
        return (name, file, _guess_mime(name))


def _guess_mime(name: str) -> str | None:
    import mimetypes

    return mimetypes.guess_type(name)[0]


def dump_json_field(value: Any) -> Any:
    """Graph API wants list/dict params JSON-encoded in query strings."""
    if isinstance(value, (list, dict)):
        return json.dumps(value)
    return value


def clean_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
    """Drop ``None`` values and JSON-encode containers for query params."""
    if not params:
        return None
    return {k: dump_json_field(v) for k, v in params.items() if v is not None}


def clean_body(body: dict[str, Any]) -> dict[str, Any]:
    """Recursively drop ``None`` values from a JSON body."""
    out: dict[str, Any] = {}
    for key, value in body.items():
        if value is None:
            continue
        if isinstance(value, dict):
            out[key] = clean_body(value)
        elif isinstance(value, list):
            out[key] = [clean_body(v) if isinstance(v, dict) else v for v in value]
        else:
            out[key] = value
    return out


def merge_fields(fields: Sequence[str] | str | None) -> str | None:
    if fields is None:
        return None
    if isinstance(fields, str):
        return fields
    return ",".join(fields)
