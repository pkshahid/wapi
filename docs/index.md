# whatsapp-cloud

A complete, typed Python client for the **WhatsApp Business Platform** —
Cloud API, Business Management API, Flows API, Calling API, and webhooks.

```python
from whatsapp_cloud import Client
from whatsapp_cloud.builders import Buttons, Template

client = Client(
    access_token="EAAB...",
    phone_number_id="106540352242922",
    waba_id="102290129340398",
)

client.messages.send_text(to="15551234567", body="Hello!")
client.messages.send_interactive(
    to="15551234567",
    interactive=Buttons().body("Pick one").add("Yes", "y").add("No", "n"),
)
client.messages.send_template(
    to="15551234567",
    template=Template("order_conf", "en_US").body_params("Ana", "1234"),
)
```

## Why whatsapp-cloud

- **Complete** — every endpoint on the platform: ~100 operations across
  messaging, media, templates, phone numbers, calling, groups, flows,
  marketing messages, and account admin.
- **Ergonomic** — `client.messages.send_text(to, body)` and fluent builders
  instead of hand-written JSON dicts.
- **Typed** — Pydantic models for every response and webhook event;
  `mypy --strict` clean.
- **Sync + Async** — `Client` and `AsyncClient` with the same API surface.
- **Webhooks** — signature verification, typed event parsing, and a ready
  FastAPI router.

## Coverage map

| Resource | Endpoints |
|---|---|
| `client.messages` | all ~15 message types, replies, read receipts, typing |
| `client.marketing` | Marketing Messages (MM Lite) API |
| `client.media` | upload / get URL / download / delete / resumable upload |
| `client.templates` | list, get, create, edit, delete, migrate |
| `client.phone_numbers` | list, add, register, deregister, verify, settings, OBA |
| `client.profile` | business profile get/update |
| `client.commerce` | cart & catalog visibility |
| `client.compliance` | India regulatory info |
| `client.automation` | welcome messages, ice breakers |
| `client.encryption` | Flows end-to-end public key |
| `client.qr_codes` | QR codes & message links |
| `client.blocked` | block / unblock users |
| `client.calls` | VoIP calls + permissions |
| `client.groups` | groups, participants, invites, join requests |
| `client.flows` | create, update JSON, publish, deprecate, migrate |
| `client.waba` | analytics, activities, schedules, subscribed apps |

See the [Endpoint Catalog](api-reference.md) for the full spec.

## Status

Alpha — core v1 covering all messaging + account APIs. The partner/admin
tier (business portfolio, app solutions, pre-verified numbers) is planned
for v1.1.
