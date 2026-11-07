"""Cursor-based pagination for Graph API list endpoints.

Meta paginates with ``paging.next`` (a full URL) plus ``paging.cursors``.
Iterators below yield decoded items lazily — a ``for`` loop just works::

    for template in client.templates.list():
        ...

Collect a bounded result with ``itertools.islice`` or ``list()``.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Iterator
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")
ItemDecoder = Callable[[dict[str, Any]], T]
Fetcher = Callable[[dict[str, Any] | None, str | None], dict[str, Any]]


def _passthrough(d: dict[str, Any]) -> Any:
    return d


@dataclass
class Page(Generic[T]):
    """One page of a cursor-paginated listing."""

    data: list[T]
    before: str | None = None
    after: str | None = None
    has_next: bool = False


def _cursors(payload: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    paging = payload.get("paging") or {}
    cursors = paging.get("cursors") or {}
    return cursors.get("before"), cursors.get("after"), paging.get("next")


class CursorIterator(Generic[T], Iterator[T]):
    """Lazy iterator over a cursor-paginated endpoint."""

    def __init__(
        self,
        fetch: Fetcher,
        *,
        params: dict[str, Any] | None = None,
        decode: ItemDecoder[T] | None = None,
    ) -> None:
        self._fetch = fetch
        self._params = dict(params or {})
        self._decode: ItemDecoder[T] = decode or _passthrough
        self._buffer: list[T] = []
        self._next_url: str | None = None
        self._first = True
        self._exhausted = False
        self._seen_urls: set[str] = set()

    def __iter__(self) -> CursorIterator[T]:
        return self

    def __next__(self) -> T:
        while not self._buffer:
            if self._exhausted:
                raise StopIteration
            self._load_page()
        return self._buffer.pop(0)

    def _load_page(self) -> None:
        if self._first:
            payload = self._fetch(self._params, None)
            self._first = False
        else:
            assert self._next_url is not None
            payload = self._fetch(None, self._next_url)
        _, _, nxt = _cursors(payload)
        self._buffer.extend(self._decode(item) for item in payload.get("data") or [])
        # Guard against a server/mock returning the same cursor twice.
        if nxt and nxt not in self._seen_urls:
            self._next_url = nxt
            self._seen_urls.add(nxt)
        else:
            self._exhausted = True

    def pages(self) -> Iterator[Page[T]]:
        """Iterate page-by-page instead of item-by-item."""
        params: dict[str, Any] | None = self._params
        url: str | None = None
        first = True
        while True:
            payload = self._fetch(params if first else None, url)
            first = False
            before, after, nxt = _cursors(payload)
            items = [self._decode(i) for i in payload.get("data") or []]
            yield Page(data=items, before=before, after=after, has_next=bool(nxt))
            if not nxt:
                return
            url = nxt


class AsyncCursorIterator(Generic[T], AsyncIterator[T]):
    """Async variant of :class:`CursorIterator`."""

    def __init__(
        self,
        fetch: Callable[[dict[str, Any] | None, str | None], Any],
        *,
        params: dict[str, Any] | None = None,
        decode: ItemDecoder[T] | None = None,
    ) -> None:
        self._fetch = fetch
        self._params = dict(params or {})
        self._decode: ItemDecoder[T] = decode or _passthrough
        self._buffer: list[T] = []
        self._next_url: str | None = None
        self._first = True
        self._exhausted = False
        self._seen_urls: set[str] = set()

    def __aiter__(self) -> AsyncCursorIterator[T]:
        return self

    async def __anext__(self) -> T:
        while not self._buffer:
            if self._exhausted:
                raise StopAsyncIteration
            await self._load_page()
        return self._buffer.pop(0)

    async def _load_page(self) -> None:
        if self._first:
            payload = await self._fetch(self._params, None)
            self._first = False
        else:
            assert self._next_url is not None
            payload = await self._fetch(None, self._next_url)
        _, _, nxt = _cursors(payload)
        self._buffer.extend(self._decode(item) for item in payload.get("data") or [])
        if nxt and nxt not in self._seen_urls:
            self._next_url = nxt
            self._seen_urls.add(nxt)
        else:
            self._exhausted = True
