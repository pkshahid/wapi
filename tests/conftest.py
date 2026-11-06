from __future__ import annotations

import httpx
import pytest
import respx

from wapi import Client

BASE = "https://graph.facebook.com/v25.0"
PNID = "1234567890"
WABA = "9876543210"
TOKEN = "test-token"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def api() -> respx.Router:
    with respx.mock(base_url=BASE, assert_all_called=False) as router:
        yield router


@pytest.fixture
def client() -> Client:
    c = Client(TOKEN, phone_number_id=PNID, waba_id=WABA, app_id="app1", max_retries=0)
    yield c
    c.close()


def sent_request(router: respx.Router, idx: int = -1) -> httpx.Request:
    return router.calls[idx].request


def sent_json(router: respx.Router, idx: int = -1) -> dict:
    import json as _json

    return _json.loads(router.calls[idx].request.content)
