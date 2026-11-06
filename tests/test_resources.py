"""Coverage for media, templates, phone numbers, profile resources,
calls, groups, flows, marketing, and WABA endpoints."""

from __future__ import annotations

import json

import pytest

from conftest import BASE, PNID, WABA, sent_json, sent_request

# --- media -------------------------------------------------------------------


def test_media_upload(api, client, tmp_path):
    f = tmp_path / "pic.png"
    f.write_bytes(b"\x89PNG")
    api.post(f"/{PNID}/media").respond(200, json={"id": "m-42"})
    result = client.media.upload(f)
    assert result.id == "m-42"
    req = sent_request(api)
    assert "multipart/form-data" in req.headers["content-type"]
    assert b"messaging_product" in req.content


def test_media_get_and_download(api, client):
    api.get("/m-42").respond(
        200,
        json={
            "messaging_product": "whatsapp",
            "url": f"{BASE}/dl/m-42",
            "mime_type": "image/png",
            "sha256": "x",
            "file_size": 4,
        },
    )
    api.get("/dl/m-42").respond(200, content=b"\x89PNG")
    info = client.media.get("m-42")
    assert info.url.endswith("/dl/m-42")
    assert client.media.download(info) == b"\x89PNG"


def test_media_download_to_file(api, client, tmp_path):
    api.get("/m-1").respond(200, json={"url": f"{BASE}/dl/1"})
    api.get("/dl/1").respond(200, content=b"data")
    out = client.media.download("m-1", dest=tmp_path / "f.bin")
    assert out.read_bytes() == b"data"


def test_media_delete(api, client):
    api.delete("/m-1").respond(200, json={"success": True})
    assert client.media.delete("m-1") is True


def test_resumable_upload(api, client):
    api.post("/app1/uploads").respond(200, json={"id": "upload:sess"})
    api.post("/upload:sess").respond(200, json={"h": "h:abc123"})
    handle = client.media.resumable_upload(b"img-bytes", mime_type="image/png")
    assert handle == "h:abc123"
    upload_req = api.calls[1].request
    assert upload_req.headers["authorization"] == "OAuth test-token"


# --- templates ----------------------------------------------------------------


def test_templates_list_pagination(api, client):
    api.get(f"/{WABA}/message_templates").respond(
        200,
        json={
            "data": [{"id": "t1", "name": "a"}, {"id": "t2", "name": "b"}],
        },
    )
    names = [t.name for t in client.templates.list(status="APPROVED")]
    assert names == ["a", "b"]
    assert "status=APPROVED" in str(sent_request(api).url)


def test_template_get(api, client):
    api.get("/t-9").respond(200, json={"id": "t-9", "name": "otp", "status": "APPROVED"})
    t = client.templates.get("t-9")
    assert t.name == "otp"


def test_template_create(api, client):
    api.post(f"/{WABA}/message_templates").respond(
        200, json={"id": "t-1", "status": "PENDING", "category": "UTILITY"}
    )
    result = client.templates.create(
        name="order_conf",
        language="en_US",
        category="UTILITY",
        components=[{"type": "BODY", "text": "Hi {{1}}", "example": {"body_text": [["Ana"]]}}],
    )
    assert result.id == "t-1"
    body = sent_json(api)
    assert body["name"] == "order_conf"
    assert body["components"][0]["type"] == "BODY"


def test_template_edit(api, client):
    api.post("/t-1").respond(200, json={"success": True})
    client.templates.edit("t-1", category="MARKETING", allow_category_change=True)
    assert sent_json(api)["category"] == "MARKETING"


def test_template_delete_by_name(api, client):
    api.delete(f"/{WABA}/message_templates").respond(200, json={"success": True})
    client.templates.delete(name="old_one")
    assert "name=old_one" in str(sent_request(api).url)


def test_template_migrate(api, client):
    api.post(f"/{WABA}/migrate_message_templates").respond(200, json={"migrated": ["t1"]})
    client.templates.migrate(source_waba_id="src-1", template_names=["t1"])
    assert "source_waba_id=src-1" in str(sent_request(api).url)


# --- phone numbers -------------------------------------------------------------


def test_phone_numbers_list(api, client):
    api.get(f"/{WABA}/phone_numbers").respond(
        200,
        json={
            "data": [{"id": "p1", "display_phone_number": "+1555", "verified_name": "Biz"}],
        },
    )
    nums = list(client.phone_numbers.list())
    assert nums[0].display_phone_number == "+1555"


def test_phone_number_get_fields(api, client):
    api.get(f"/{PNID}").respond(200, json={"id": PNID, "quality_rating": "GREEN"})
    info = client.phone_numbers.get(fields=["quality_rating", "verified_name"])
    assert info.quality_rating == "GREEN"
    assert "fields=" in str(sent_request(api).url)


def test_register(api, client):
    api.post(f"/{PNID}/register").respond(200, json={"success": True})
    client.phone_numbers.register(pin="123456", data_localization_region="IN")
    body = sent_json(api)
    assert body == {
        "messaging_product": "whatsapp",
        "pin": "123456",
        "data_localization_region": "IN",
    }


def test_verify_flow(api, client):
    api.post(f"/{PNID}/request_code").respond(200, json={"success": True})
    api.post(f"/{PNID}/verify_code").respond(200, json={"success": True})
    client.phone_numbers.request_code(code_method="VOICE", language="en_US")
    assert sent_json(api)["code_method"] == "VOICE"
    client.phone_numbers.verify_code("654321")
    assert sent_json(api)["code"] == "654321"


def test_deregister(api, client):
    api.post(f"/{PNID}/deregister").respond(200, json={"success": True})
    client.phone_numbers.deregister()


def test_update_settings(api, client):
    api.post(f"/{PNID}/settings").respond(200, json={"success": True})
    client.phone_numbers.update_settings(calling={"status": "ENABLED"})
    assert sent_json(api) == {"calling": {"status": "ENABLED"}}


def test_update_settings_requires_one(api, client):
    with pytest.raises(ValueError):
        client.phone_numbers.update_settings()


def test_add_phone_number(api, client):
    api.post(f"/{WABA}/phone_numbers").respond(200, json={"id": "new-pn"})
    client.phone_numbers.add(cc="1", phone_number="5551234567", verified_name="Shop")
    assert sent_json(api)["verified_name"] == "Shop"


# --- profile & account ---------------------------------------------------------


def test_profile_get(api, client):
    api.get(f"/{PNID}/whatsapp_business_profile").respond(
        200,
        json={
            "data": [{"about": "We sell", "vertical": "RETAIL", "websites": ["https://x"]}],
        },
    )
    p = client.profile.get()
    assert p.vertical == "RETAIL"


def test_profile_update(api, client):
    api.post(f"/{PNID}/whatsapp_business_profile").respond(200, json={"success": True})
    client.profile.update(about="New", websites=["https://a", "https://b"])
    body = sent_json(api)
    assert body["messaging_product"] == "whatsapp"
    assert body["websites"] == ["https://a", "https://b"]


def test_commerce_settings(api, client):
    api.post(f"/{PNID}/whatsapp_commerce_settings").respond(200, json={"success": True})
    client.commerce.update(is_cart_enabled=True, is_catalog_visible=False)
    assert "is_cart_enabled=true" in str(sent_request(api).url)


def test_automation(api, client):
    api.post(f"/{PNID}/conversational_automation").respond(200, json={"success": True})
    client.automation.configure(enable_welcome_message=True, prompts=["Hi", "Help"])
    assert sent_json(api)["prompts"] == ["Hi", "Help"]


def test_encryption(api, client):
    api.post(f"/{PNID}/whatsapp_business_encryption").respond(200, json={"success": True})
    client.encryption.set_key("-----BEGIN PUBLIC KEY-----\nX\n-----END PUBLIC KEY-----")
    assert "business_public_key" in sent_json(api)


def test_qr_create(api, client):
    api.post(f"/{PNID}/message_qrdls").respond(200, json={"code": "ABC", "qr_image_url": "u"})
    client.qr_codes.create_or_update(prefilled_message="Hi!", generate_qr_image="PNG")
    assert sent_json(api)["prefilled_message"] == "Hi!"


def test_blocked_users(api, client):
    api.get(f"/{PNID}/block_users").respond(200, json={"users": [{"user": "1555"}]})
    api.post(f"/{PNID}/block_users").respond(200, json={"success": True})
    api.delete(f"/{PNID}/block_users").respond(200, json={"success": True})
    assert client.blocked.list()[0].user == "1555"
    client.blocked.block(["1555", "1666"])
    assert len(sent_json(api)["block_users"]) == 2
    client.blocked.unblock("1555")
    assert sent_json(api)["block_users"] == [{"user": "1555"}]


# --- calls ---------------------------------------------------------------------


def test_call_permissions(api, client):
    api.get(f"/{PNID}/call_permissions").respond(
        200,
        json={
            "messaging_product": "whatsapp",
            "permission": {"status": "granted"},
            "actions": [{"action_name": "start_call", "can_perform_action": True}],
        },
    )
    p = client.calls.check_permissions("1555")
    assert p.status == "granted"
    assert p.actions[0].can_perform_action is True


def test_call_connect(api, client):
    api.post(f"/{PNID}/calls").respond(
        200,
        json={
            "messaging_product": "whatsapp",
            "calls": [{"id": "call-1"}],
        },
    )
    r = client.calls.connect("1555", sdp="v=0 o=...")
    assert r.call_id == "call-1"
    body = sent_json(api)
    assert body["action"] == "connect"
    assert body["session"] == {"sdp_type": "offer", "sdp": "v=0 o=..."}


def test_call_terminate(api, client):
    api.post(f"/{PNID}/calls").respond(200, json={"success": True})
    client.calls.terminate("call-1")
    body = sent_json(api)
    assert body == {"messaging_product": "whatsapp", "call_id": "call-1", "action": "terminate"}


# --- groups ---------------------------------------------------------------------


def test_group_create(api, client):
    api.post(f"/{PNID}/groups").respond(200, json={"id": "g-1"})
    g = client.groups.create(subject="VIP", join_approval_mode="auto_approve")
    assert g.id == "g-1"
    body = sent_json(api)
    assert body["subject"] == "VIP"
    assert body["messaging_product"] == "whatsapp"


def test_group_lifecycle(api, client):
    api.post("/g-1/invite_link").respond(200, json={"invite_link": "https://chat.whatsapp.com/x"})
    api.post("/g-1/participants").respond(200, json={"success": True})
    api.get("/g-1/join_requests").respond(200, json={"data": [{"id": "jr1"}]})
    api.post("/g-1/join_requests").respond(200, json={"success": True})
    client.groups.create_invite_link("g-1")
    client.groups.add_participants("g-1", ["1555"])
    assert next(iter(client.groups.list_join_requests("g-1"))).id == "jr1"
    client.groups.approve_join_requests("g-1", ["jr1"])
    assert sent_json(api)["join_requests"] == ["jr1"]


def test_group_update_and_delete(api, client):
    api.post("/g-1").respond(200, json={"success": True})
    api.delete("/g-1").respond(200, json={"success": True})
    client.groups.update("g-1", subject="New name")
    assert sent_json(api)["subject"] == "New name"
    client.groups.delete("g-1")


# --- flows ---------------------------------------------------------------------


def test_flow_create_and_publish(api, client):
    api.post(f"/{WABA}/flows").respond(200, json={"id": "f-1", "success": True})
    api.post("/f-1/publish").respond(200, json={"success": True})
    f = client.flows.create(
        name="survey",
        categories=["SURVEY"],
        flow_json={"version": "5.0", "screens": []},
        publish=True,
    )
    assert f.id == "f-1"
    body = json.loads(api.calls[0].request.content)
    assert body["publish"] is True
    client.flows.publish("f-1")


def test_flow_assets_and_preview(api, client):
    api.post("/f-1/assets").respond(200, json={"success": True, "validation_errors": []})
    api.get("/f-1").respond(200, json={"preview": {"preview_url": "https://biz/preview"}})
    client.flows.update_json("f-1", {"version": "5.0"})
    prev = client.flows.preview("f-1")
    assert prev["preview"]["preview_url"].startswith("https://biz")


def test_flow_migrate(api, client):
    api.post(f"/{WABA}/migrate_flows").respond(
        200,
        json={
            "migrated_flows": [{"source_name": "s", "migrated_id": "f-2"}],
        },
    )
    r = client.flows.migrate(source_waba_id="src")
    assert r.migrated_flows[0].migrated_id == "f-2"


# --- marketing / waba ------------------------------------------------------------


def test_marketing_message(api, client):
    api.post(f"/{PNID}/marketing_messages").respond(200, json={"messages": [{"id": "w"}]})
    client.marketing.send_template(
        "1555", {"name": "promo", "language": {"code": "en"}}, product_policy="STRICT"
    )
    body = sent_json(api)
    assert body["type"] == "template"
    assert body["product_policy"] == "STRICT"


def test_waba_get_and_analytics(api, client):
    import httpx

    api.get(f"/{WABA}").side_effect = [
        httpx.Response(200, json={"id": WABA, "name": "Acct"}),
        httpx.Response(200, json={"analytics": {"data_points": []}}),
    ]
    w = client.waba.get()
    assert w.name == "Acct"
    client.waba.analytics(start=1, end=2, granularity="DAY")
    from urllib.parse import unquote

    url = unquote(str(sent_request(api).url))
    assert "analytics.start(1).end(2).granularity(DAY)" in url


def test_subscribed_apps(api, client):
    api.post(f"/{WABA}/subscribed_apps").respond(200, json={"success": True})
    client.waba.subscribe_app(override_callback_uri="https://me/hook", verify_token="vt")
    assert sent_json(api)["override_callback_uri"] == "https://me/hook"


def test_schedule_create(api, client):
    api.post(f"/{WABA}/schedules").respond(200, json={"id": "s-1"})
    client.waba.create_schedule(hsm_id="h1", delivery_time=1700000000, name="blast")
    assert sent_json(api)["hsm_id"] == "h1"
