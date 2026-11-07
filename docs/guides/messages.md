# Sending Messages

All outbound messages go through `client.messages` →
`POST /{phone-number-id}/messages`.

## Common options

Every `send_*` accepts:

| Option | Purpose |
|---|---|
| `recipient_type` | `"individual"` (default) or `"group"` (`to` = group id) |
| `reply_to` | Quote a message by `wamid` |
| `biz_opaque_callback_data` | ≤512 chars echoed back in status webhooks |
| `phone_number_id` | Override the client's default number |

## Text & media

```python
client.messages.send_text(to, "Hello", preview_url=True)
client.messages.send_image(to, media_id="8006...", caption="look")
client.messages.send_image(to, link="https://…/a.png")
client.messages.send_document(to, link="https://…/f.pdf", filename="f.pdf")
client.messages.send_audio(to, media_id="…")
client.messages.send_video(to, link="https://…/v.mp4", caption="clip")
client.messages.send_sticker(to, media_id="…")
client.messages.send_location(to, latitude=1.5, longitude=2.5, name="HQ")
client.messages.send_contacts(to, contacts=[Contact(name=Contact.name("Ana"), phones=[Contact.phone("1555")])])
client.messages.send_reaction(to, message_id="wamid.x", emoji="👍")
```

## Interactive builders

```python
from wapi.builders import Buttons, ListMessage, CtaUrl, FlowMessage, Product, ProductList, CatalogMessage, LocationRequest, CallPermissionRequest

# reply buttons (max 3)
Buttons().body("Sure?").add("Yes", "y").add("No", "n")

# list menu
msg = ListMessage("Menu").body("Choose"); msg.section("Food").row("Pizza", "p1")
client.messages.send_interactive(to, msg)

# CTA URL
CtaUrl("Shop", "https://shop.example").body("Go")

# WhatsApp Flow
FlowMessage("Book", flow_id="f1", screen="ENTRY", data={"a": 1}).body("Book now")
FlowMessage("T", flow_name="draft_flow", draft=True)          # draft testing

# products
Product("catalog_id", "retailer_sku")
ProductList("catalog_id", header_text="Picks")
CatalogMessage()

# utility
LocationRequest()               # ask user for their location
CallPermissionRequest()         # request permission to call
```

Pass the builder to `send_interactive`:

```python
client.messages.send_interactive(to, Buttons().body("?").add("OK", "ok"))
```

## Templates

```python
from wapi.builders import Template, Param

client.messages.send_template(to, Template("order_conf", "en_US").body_params("Ana", "1234"))
client.messages.send_template(to,
    Template("shipped", "en_US")
        .header_params(Param.image(link="https://…"))
        .body_params(first_name="Bo")
        .button_params("quick_reply", 0, Param.payload("track-1")),
)
```

## Receipts & typing

```python
client.messages.mark_read("wamid.in")            # blue ticks
client.messages.mark_read("wamid.in", typing=True)  # + typing indicator
```

## Marketing messages (MM Lite)

```python
client.marketing.send_template(to, Template("promo", "en_US"),
    product_policy="STRICT", message_activity_sharing=True)
```
