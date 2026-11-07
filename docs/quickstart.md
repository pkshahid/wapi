# Installation & Quickstart

## Install

```bash
pip install whatsapp-business-cloud            # core
pip install "whatsapp-business-cloud[fastapi]" # + webhook FastAPI router
```

From source:

```bash
git clone https://github.com/whatsapp-business-cloud-py/whatsapp-business-cloud && cd whatsapp-business-cloud
pip install -e ".[dev,fastapi]"
```

## Credentials

You need three IDs from the Meta app dashboard (or WhatsApp Manager):

| Value | Where |
|---|---|
| `access_token` | System user token with `whatsapp_business_messaging` + `whatsapp_business_management` |
| `phone_number_id` | API Setup page → *From* number |
| `waba_id` | API Setup page → WhatsApp Business Account ID |

```python
from whatsapp_business_cloud import Client

client = Client(
    access_token="EAAB...",
    phone_number_id="106540352242922",
    waba_id="102290129340398",
)
```

`phone_number_id` / `waba_id` are optional per-call — pass them to any
resource method to override.

## First message

```python
resp = client.messages.send_text(to="15551234567", body="Hello from whatsapp_business_cloud!")
print(resp.message_id)          # -> "wamid.XXX"
```

## With a context manager

```python
with Client("EAAB...", phone_number_id="...") as client:
    client.messages.send_text(to="1555...", body="hi")
```

## Next steps

- [Sending Messages](guides/messages.md) — all message types & builders
- [Webhooks](guides/webhooks.md) — receive and verify inbound events
- [Errors & Retries](guides/errors.md) — exception hierarchy and retry policy
