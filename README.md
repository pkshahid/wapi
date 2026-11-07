# whatsapp-business-cloud

A complete, typed Python client for the **WhatsApp Business Platform** (Cloud API +
Business Management API + Flows API).

```python
from whatsapp_business_cloud import Client
from whatsapp_business_cloud.builders import Buttons, Template

client = Client(
    access_token="EAAB...",
    phone_number_id="106540352242922",
    waba_id="102290129340398",
)

# messages
client.messages.send_text(to="15551234567", body="Hello!")
client.messages.send_interactive(to="15551234567", interactive=Buttons()
    .body("Pick one").add("Yes", "y").add("No", "n"))
client.messages.send_template(to="15551234567", template=Template("order_conf", "en_US")
    .body_params("Ana", "1234"))

# media
media = client.media.upload("./invoice.pdf")
client.messages.send_document(to="15551234567", media_id=media.id, filename="invoice.pdf")

# everything else
client.templates.list(status="APPROVED")
client.groups.create(subject="VIP")
client.calls.connect(to="1555...", sdp=offer)
client.flows.publish(flow_id)

# webhooks
from whatsapp_business_cloud.webhooks import parse, verify_signature
events = parse(request.body())

# async
from whatsapp_business_cloud import AsyncClient
async with AsyncClient("EAAB...", phone_number_id="...") as c:
    await c.messages.send_text(to="1555...", body="hi")
```

See `docs/api-reference.md` for the endpoint spec and `docs/plan.md` for the design.

## Install

```bash
pip install -e .          # from this repo
pip install "whatsapp-business-cloud[fastapi]"  # with the webhook router extra
```

## Develop

```bash
uv venv .venv && uv pip install --python .venv/bin/python -e ".[dev,fastapi]"
.venv/bin/pytest          # tests
.venv/bin/ruff check src  # lint
.venv/bin/mypy src        # typecheck
```
