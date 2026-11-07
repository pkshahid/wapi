from __future__ import annotations

import httpx
import pytest

from conftest import BASE, PNID, sent_json, sent_request
from whatsapp_cloud import ApiError, AuthError, NotFoundError, RateLimitError, ValidationError
from whatsapp_cloud.exceptions import MessagingError, RegistrationError


def test_auth_header_and_version_path(api, client):
    api.post(f"/{PNID}/messages").respond(200, json={"messages": [{"id": "wamid.1"}]})
    client.messages.send_text(to="1555", body="hi")
    req = sent_request(api)
    assert req.headers["authorization"] == "Bearer test-token"
    assert req.url.path == f"/v25.0/{PNID}/messages"


def test_raw_request(api, client):
    api.get("/some/path").respond(200, json={"ok": True})
    assert client.raw_request("GET", "some/path") == {"ok": True}


def test_error_mapping_auth(api, client):
    api.post(f"/{PNID}/messages").respond(
        401, json={"error": {"message": "bad token", "code": 190, "type": "OAuthException"}}
    )
    with pytest.raises(AuthError) as e:
        client.messages.send_text(to="x", body="y")
    assert e.value.code == 190
    assert e.value.status_code == 401


def test_error_mapping_rate_limit(api, client):
    api.post(f"/{PNID}/messages").respond(429, json={"error": {"message": "rate", "code": 131056}})
    with pytest.raises(RateLimitError):
        client.messages.send_text(to="x", body="y")


def test_error_mapping_validation(api, client):
    api.post(f"/{PNID}/messages").respond(
        400, json={"error": {"message": "(#132000) too many", "code": 132000}}
    )
    with pytest.raises(ValidationError):
        client.messages.send_text(to="x", body="y")


def test_error_mapping_messaging(api, client):
    api.post(f"/{PNID}/messages").respond(
        400, json={"error": {"message": "undeliverable", "code": 131026}}
    )
    with pytest.raises(MessagingError):
        client.messages.send_text(to="x", body="y")


def test_error_mapping_registration(api, client):
    api.post(f"/{PNID}/register").respond(400, json={"error": {"message": "pin", "code": 133004}})
    with pytest.raises(RegistrationError):
        client.phone_numbers.register(pin="123456")


def test_error_not_found(api, client):
    api.get("/nonexistent").respond(404, json={"error": {"message": "nope"}})
    with pytest.raises(NotFoundError):
        client.raw_request("GET", "nonexistent")


def test_retry_on_500(monkeypatch):
    import httpx
    import respx

    from whatsapp_cloud import Client

    sleeps: list[float] = []
    monkeypatch.setattr("whatsapp_cloud.http.sleep", lambda s: sleeps.append(s))

    c = Client("tok", phone_number_id=PNID, max_retries=2)
    with respx.mock(base_url=BASE) as router:
        route = router.post(f"/{PNID}/messages")
        route.side_effect = [
            httpx.Response(500, json={"error": {"message": "boom", "code": 1}}),
            httpx.Response(200, json={"messages": [{"id": "wamid.9"}]}),
        ]
        resp = c.messages.send_text(to="x", body="y")
        assert resp.message_id == "wamid.9"
        assert route.call_count == 2
        assert len(sleeps) == 1
    c.close()


def test_no_retry_on_permanent_error(api, client):
    route = api.post(f"/{PNID}/messages").respond(
        400, json={"error": {"message": "bad", "code": 132000}}
    )
    with pytest.raises(ApiError):
        client.messages.send_text(to="x", body="y")
    assert route.call_count == 1


def test_cursor_iterator_absolute_url(api, client):
    api.get(f"/{PNID}/message_qrdls").side_effect = [
        httpx.Response(
            200,
            json={
                "data": [{"code": "A"}],
                "paging": {"next": f"{BASE}/{PNID}/message_qrdls?after=xyz"},
            },
        ),
        httpx.Response(200, json={"data": [{"code": "B"}]}),
    ]
    codes = [q.code for q in client.qr_codes.list()]
    assert codes == ["A", "B"]


def test_group_recipient_type(api, client):
    api.post(f"/{PNID}/messages").respond(200, json={"messages": [{"id": "w"}]})
    client.messages.send_text(to="group-id-1", body="hi group", recipient_type="group")
    body = sent_json(api)
    assert body["recipient_type"] == "group"
    assert body["to"] == "group-id-1"
