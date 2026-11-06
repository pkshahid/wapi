from __future__ import annotations

import json

import pytest

from wapi.exceptions import WebhookSignatureError
from wapi.webhooks import (
    InboundMessages,
    StatusUpdates,
    TemplateStatusUpdate,
    UnknownEvent,
    parse,
    verify_or_raise,
    verify_signature,
)
from wapi.webhooks.signature import compute_signature

SECRET = "shhh"
BODY = b'{"object":"whatsapp_business_account","entry":[]}'


def test_signature_verify():
    sig = compute_signature(BODY, SECRET)
    assert verify_signature(BODY, sig, SECRET) is True
    assert verify_signature(BODY, "sha256=bad", SECRET) is False
    assert verify_signature(BODY, None, SECRET) is False
    verify_or_raise(BODY, sig, SECRET)
    with pytest.raises(WebhookSignatureError):
        verify_or_raise(BODY, "sha256=bad", SECRET)


TEXT_WEBHOOK = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "waba-1",
            "changes": [
                {
                    "field": "messages",
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "1555000111",
                            "phone_number_id": "pn-1",
                        },
                        "contacts": [{"profile": {"name": "Ana"}, "wa_id": "1555999"}],
                        "messages": [
                            {
                                "from": "1555999",
                                "id": "wamid.in1",
                                "timestamp": "1700000000",
                                "type": "text",
                                "text": {"body": "hello there"},
                            }
                        ],
                    },
                }
            ],
        }
    ],
}


def test_parse_text_message():
    events = parse(TEXT_WEBHOOK)
    assert len(events) == 1
    e = events[0]
    assert isinstance(e, InboundMessages)
    msg = e.messages[0]
    assert msg.type == "text"
    assert msg.text.body == "hello there"
    assert msg.from_ == "1555999"
    assert e.contacts[0].name == "Ana"
    assert e.metadata.phone_number_id == "pn-1"
    assert e.sender_phone == "1555999"


def test_parse_interactive_reply():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "w",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messages": [
                                {
                                    "from": "1",
                                    "id": "m1",
                                    "type": "interactive",
                                    "interactive": {
                                        "type": "list_reply",
                                        "list_reply": {"id": "row-1", "title": "Pizza"},
                                    },
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }
    e = parse(payload)[0]
    assert isinstance(e, InboundMessages)
    assert e.messages[0].interactive.list_reply["id"] == "row-1"


def test_parse_statuses():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "w",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "statuses": [
                                {
                                    "id": "wamid.1",
                                    "status": "delivered",
                                    "timestamp": "1700000001",
                                    "recipient_id": "1555",
                                    "conversation": {"id": "c1", "origin": {"type": "service"}},
                                    "pricing": {
                                        "billable": True,
                                        "pricing_model": "PMP",
                                        "category": "service",
                                    },
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }
    e = parse(payload)[0]
    assert isinstance(e, StatusUpdates)
    st = e.statuses[0]
    assert st.status == "delivered"
    assert st.conversation.origin_type == "service"
    assert st.pricing.billable is True


def test_parse_failed_status_errors():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "w",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "statuses": [
                                {
                                    "id": "w1",
                                    "status": "failed",
                                    "errors": [
                                        {
                                            "code": 131047,
                                            "title": "Re-engagement",
                                            "error_data": {"details": "24h window closed"},
                                        }
                                    ],
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }
    e = parse(payload)[0]
    assert e.failed[0].code == 131047
    assert e.failed[0].details == "24h window closed"


def test_parse_template_status_update():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "w",
                "changes": [
                    {
                        "field": "message_template_status_update",
                        "value": {
                            "event": "APPROVED",
                            "message_template_id": 99,
                            "message_template_name": "otp",
                            "message_template_language": "en_US",
                        },
                    }
                ],
            }
        ],
    }
    e = parse(payload)[0]
    assert isinstance(e, TemplateStatusUpdate)
    assert e.event == "APPROVED"
    assert e.message_template_id == 99


def test_parse_unknown_field():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{"id": "w", "changes": [{"field": "future_field", "value": {"x": 1}}]}],
    }
    e = parse(payload)[0]
    assert isinstance(e, UnknownEvent)
    assert e.value == {"x": 1}


def test_parse_accepts_str_and_bytes():
    raw = json.dumps(TEXT_WEBHOOK)
    assert len(parse(raw)) == 1
    assert len(parse(raw.encode())) == 1


def test_parse_multiple_changes():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "w",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messages": [
                                {"from": "1", "id": "m", "type": "text", "text": {"body": "a"}}
                            ]
                        },
                    },
                    {"field": "messages", "value": {"statuses": [{"id": "s", "status": "read"}]}},
                ],
            }
        ],
    }
    events = parse(payload)
    assert isinstance(events[0], InboundMessages)
    assert isinstance(events[1], StatusUpdates)


# --- FastAPI router -------------------------------------------------------------


def test_fastapi_router_verification_and_dispatch():
    pytest.importorskip("fastapi")
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from wapi.webhooks.fastapi import webhook_router

    received = []
    app = FastAPI()
    app.include_router(webhook_router(received.append, verify_token="vt", app_secret=SECRET))
    tc = TestClient(app)

    # verification handshake
    r = tc.get(
        "/webhook",
        params={"hub.mode": "subscribe", "hub.verify_token": "vt", "hub.challenge": "CH42"},
    )
    assert r.status_code == 200
    assert r.text == "CH42"
    r = tc.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "bad"})
    assert r.status_code == 403

    # signed POST
    body = json.dumps(TEXT_WEBHOOK).encode()
    sig = compute_signature(body, SECRET)
    r = tc.post("/webhook", content=body, headers={"x-hub-signature-256": sig})
    assert r.status_code == 200
    assert isinstance(received[0], InboundMessages)

    # tampered POST
    r = tc.post("/webhook", content=body, headers={"x-hub-signature-256": "sha256=nope"})
    assert r.status_code == 401
