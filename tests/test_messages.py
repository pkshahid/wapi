from __future__ import annotations

import pytest

from conftest import PNID, sent_json
from whatsapp_cloud.builders import (
    Buttons,
    CatalogMessage,
    Contact,
    CtaUrl,
    FlowMessage,
    ListMessage,
    LocationRequest,
    Param,
    Product,
    ProductList,
    Template,
)


@pytest.fixture
def route(api):
    api.post(f"/{PNID}/messages").respond(
        200,
        json={
            "messaging_product": "whatsapp",
            "contacts": [{"input": "1555", "wa_id": "1555"}],
            "messages": [{"id": "wamid.abc"}],
        },
    )
    return api


def test_send_text(route, client):
    resp = client.messages.send_text(to="1555", body="hi", preview_url=True, reply_to="wamid.old")
    assert resp.message_id == "wamid.abc"
    body = sent_json(route)
    assert body["type"] == "text"
    assert body["text"] == {"body": "hi", "preview_url": True}
    assert body["context"] == {"message_id": "wamid.old"}
    assert body["messaging_product"] == "whatsapp"


def test_send_image_by_id(route, client):
    client.messages.send_image(to="1555", media_id="m1", caption="look")
    body = sent_json(route)
    assert body["image"] == {"id": "m1", "caption": "look"}
    assert "link" not in body["image"]


def test_send_document_by_link(route, client):
    client.messages.send_document(to="1555", link="https://x/y.pdf", filename="y.pdf")
    body = sent_json(route)
    assert body["document"] == {"link": "https://x/y.pdf", "filename": "y.pdf"}


def test_send_media_requires_id_or_link(client):
    with pytest.raises(ValueError):
        client.messages.send_image(to="1555")


def test_send_location(route, client):
    client.messages.send_location(to="1555", latitude=1.5, longitude=2.5, name="HQ")
    assert sent_json(route)["location"]["name"] == "HQ"


def test_send_contacts(route, client):
    c = Contact(name=Contact.name("Ana B", first="Ana"), phones=[Contact.phone("1555")])
    client.messages.send_contacts(to="1555", contacts=[c])
    body = sent_json(route)
    assert body["type"] == "contacts"
    assert body["contacts"][0]["name"]["formatted_name"] == "Ana B"


def test_send_reaction(route, client):
    client.messages.send_reaction(to="1555", message_id="wamid.1", emoji="👍")
    assert sent_json(route)["reaction"] == {"message_id": "wamid.1", "emoji": "👍"}


def test_send_buttons(route, client):
    b = Buttons().body("Sure?").add("Yes", "y").add("No", "n").footer("pick")
    client.messages.send_interactive(to="1555", interactive=b)
    inter = sent_json(route)["interactive"]
    assert inter["type"] == "button"
    assert inter["body"] == {"text": "Sure?"}
    assert len(inter["action"]["buttons"]) == 2
    assert inter["action"]["buttons"][0]["reply"] == {"id": "y", "title": "Yes"}


def test_buttons_max_3():
    with pytest.raises(ValueError):
        Buttons().add("a", "1").add("b", "2").add("c", "3").add("d", "4")


def test_send_list_message(route, client):
    msg = ListMessage("Menu").body("Choose")
    msg.section("Food").row("Pizza", "p1", description="slice").row("Pasta", "p2")
    client.messages.send_interactive(to="1555", interactive=msg)
    inter = sent_json(route)["interactive"]
    assert inter["type"] == "list"
    assert inter["action"]["button"] == "Menu"
    assert inter["action"]["sections"][0]["rows"][0]["title"] == "Pizza"


def test_send_cta_url(route, client):
    client.messages.send_interactive(
        to="1555", interactive=CtaUrl("Shop", "https://shop.x").body("go")
    )
    inter = sent_json(route)["interactive"]
    assert inter["action"]["parameters"]["url"] == "https://shop.x"


def test_send_flow_message(route, client):
    flow = FlowMessage("Book", flow_id="f1", screen="ENTRY", data={"a": 1}).body("book now")
    client.messages.send_interactive(to="1555", interactive=flow)
    inter = sent_json(route)["interactive"]
    params = inter["action"]["parameters"]
    assert params["flow_id"] == "f1"
    assert params["flow_action"] == "navigate"
    assert params["flow_action_payload"] == {"screen": "ENTRY", "data": {"a": 1}}


def test_flow_draft_mode(route, client):
    client.messages.send_interactive(
        to="1555", interactive=FlowMessage("T", flow_name="myflow", draft=True).body("x")
    )
    params = sent_json(route)["interactive"]["action"]["parameters"]
    assert params["flow_name"] == "myflow"
    assert params["mode"] == "draft"


def test_send_product(route, client):
    client.messages.send_interactive(to="1555", interactive=Product("cat1", "sku1").body("buy"))
    inter = sent_json(route)["interactive"]
    assert inter["action"]["product_retailer_id"] == "sku1"


def test_send_product_list(route, client):
    pl = ProductList("cat1", header_text="Top picks").body("shop")
    pl.section("Shoes").add("s1").add("s2")
    client.messages.send_interactive(to="1555", interactive=pl)
    inter = sent_json(route)["interactive"]
    assert inter["header"]["text"] == "Top picks"
    assert inter["action"]["sections"][0]["product_items"] == [
        {"product_retailer_id": "s1"},
        {"product_retailer_id": "s2"},
    ]


def test_send_catalog(route, client):
    client.messages.send_interactive(to="1555", interactive=CatalogMessage().body("browse"))
    assert sent_json(route)["interactive"]["action"]["name"] == "catalog_message"


def test_location_request(route, client):
    client.messages.send_interactive(to="1555", interactive=LocationRequest().body("share loc"))
    assert sent_json(route)["interactive"]["action"] == {"name": "send_location"}


def test_send_template_positional(route, client):
    t = Template("order_conf", "en_US").body_params("Ana", "1234")
    client.messages.send_template(to="1555", template=t)
    tpl = sent_json(route)["template"]
    assert tpl["name"] == "order_conf"
    assert tpl["language"] == {"code": "en_US"}
    assert tpl["components"][0]["parameters"] == [
        {"type": "text", "text": "Ana"},
        {"type": "text", "text": "1234"},
    ]


def test_send_template_named_and_media(route, client):
    t = (
        Template("shipped", "en_US")
        .header_params(Param.image(link="https://x/img.png"))
        .body_params(first_name="Bo")
        .button_params("quick_reply", 0, Param.payload("track-1"))
    )
    client.messages.send_template(to="1555", template=t)
    comps = sent_json(route)["template"]["components"]
    assert comps[0]["type"] == "header"
    assert comps[0]["parameters"][0]["image"]["link"] == "https://x/img.png"
    assert comps[1]["parameters"][0]["parameter_name"] == "first_name"
    assert comps[2]["sub_type"] == "quick_reply"
    assert comps[2]["index"] == "0"


def test_mark_read_and_typing(api, client):
    api.post(f"/{PNID}/messages").respond(200, json={"success": True})
    client.messages.mark_read("wamid.1", typing=True)
    body = sent_json(api)
    assert body["status"] == "read"
    assert body["typing_indicator"] == {"type": "text"}


def test_mark_read_no_typing(api, client):
    api.post(f"/{PNID}/messages").respond(200, json={"success": True})
    client.messages.mark_read("wamid.1")
    assert "typing_indicator" not in sent_json(api)


def test_biz_opaque_callback_data(route, client):
    client.messages.send_text(to="1555", body="hi", biz_opaque_callback_data="track-123")
    assert sent_json(route)["biz_opaque_callback_data"] == "track-123"


def test_phone_number_id_override(route, client):
    api2 = route.post("/other-pnid/messages").respond(200, json={"messages": [{"id": "w"}]})
    client.messages.send_text(to="1555", body="hi", phone_number_id="other-pnid")
    assert api2.called


def test_send_raw(route, client):
    client.messages.send_raw({"to": "1555", "type": "text", "text": {"body": "raw"}})
    assert sent_json(route)["text"] == {"body": "raw"}


# --- async parity spot-checks ------------------------------------------------


pytestmark_anyio = True


@pytest.mark.anyio
async def test_async_send_text(api):
    from whatsapp_cloud import AsyncClient

    api.post(f"/{PNID}/messages").respond(200, json={"messages": [{"id": "wamid.a"}]})
    async with AsyncClient("tok", phone_number_id=PNID, max_retries=0) as c:
        resp = await c.messages.send_text(to="1555", body="hi")
        assert resp.message_id == "wamid.a"


@pytest.mark.anyio
async def test_async_mark_read(api):
    from whatsapp_cloud import AsyncClient

    api.post(f"/{PNID}/messages").respond(200, json={"success": True})
    async with AsyncClient("tok", phone_number_id=PNID, max_retries=0) as c:
        await c.messages.mark_read("wamid.1", typing=True)
        assert sent_json(api)["typing_indicator"] == {"type": "text"}
