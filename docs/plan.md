# `whatsapp-business-cloud` — WhatsApp Business Platform Python Client: Build Plan

A complete, well-organized, easy-to-use Python package covering the entire
WhatsApp Business Platform. `docs/api-reference.md` is the endpoint spec; this
document is the architecture and delivery plan.

---

## 1. Design goals

1. **Complete** — every endpoint in `api-reference.md` (~100 operations),
   including calls, groups, flows, marketing messages, and WABA/partner admin.
2. **Ergonomic** — `client.messages.send_text(to, body)` not raw dicts; fluent
   builders for interactive/template payloads.
3. **Typed** — Pydantic v2 models for every request body, response, and
   webhook event. Full `mypy --strict` coverage.
4. **Sync + Async** — one codebase, `Client` and `AsyncClient` sharing resource
   classes over `httpx`.
5. **Framework-agnostic webhooks** — signature verification + typed event
   parsing that plugs into Flask/FastAPI/Django or plain functions.
6. **Zero-surprise defaults** — sane retries on rate limits, cursor pagination
   iterators, clear exception hierarchy mapped to Meta error codes.

## 2. Tech choices

| Concern | Choice | Why |
|---|---|---|
| HTTP | `httpx` | Sync+async, HTTP/2, multipart, streaming downloads |
| Models | `pydantic` v2 | Validation, `model_dump(exclude_none=True)`, JSON Schema for docs |
| Packaging | `pyproject.toml` + `hatchling` | Modern, simple |
| Lint/format | `ruff` | Fast, one tool |
| Types | `mypy --strict` | Public API fully typed |
| Tests | `pytest` + `respx` | respx mocks httpx transport — no network needed |
| Docs | `mkdocs-material` + mkdocstrings | Auto API docs from docstrings |
| CI | GitHub Actions | lint, typecheck, test matrix (3.10–3.13), build |
| Versioning | SemVer; `API_VERSION` default `"v25.0"` pinned, user-overridable |

No framework dependencies. Optional extras:
`whatsapp-business-cloud[fastapi]` (webhook router), `whatsapp-business-cloud[flask]` later if wanted.

## 3. Package layout

```
whatsapp-business-cloud/
├── __init__.py            # Client, AsyncClient, __version__
├── client.py              # Client / AsyncClient config + resource wiring
├── http.py                # transport: request, retry/backoff, rate-limit, download
├── exceptions.py          # WhatsAppError hierarchy + code mapping
├── pagination.py          # CursorPaginator / async iterator
├── _utils.py              # file handling, E.164 validation, mime sniffing
│
├── types/                 # Pydantic models, grouped by domain
│   ├── base.py            # Response[T] envelope, Paging
│   ├── messages.py        # inbound/outbound message models
│   ├── interactive.py     # buttons, lists, products, flows, cta_url, call_permission
│   ├── templates.py       # components, categories, statuses
│   ├── contacts.py        # contact-card objects
│   ├── media.py           # media info objects
│   ├── phone_numbers.py   # registration, settings, verification
│   ├── profiles.py        # business profile, compliance
│   ├── calls.py           # SDP session, call actions, permissions
│   ├── groups.py          # group, participants, join_requests
│   ├── flows.py           # flow metadata, assets, validation errors
│   ├── waba.py            # WABA node, analytics, schedules
│   └── webhooks.py        # WebhookPayload, Change, Value unions
│
├── builders.py            # fluent payload builders:
│                          #   TextMessage("hi").preview_url()
│                          #   Buttons().add("Yes","y").body(..).footer(..)
│                          #   ListMessage(), TemplateMessage(), FlowMessage()
│
├── resources/             # one class per API resource, thin + predictable
│   ├── base.py            # ResourceBase (binds transport + path ids)
│   ├── messages.py        # send_*, mark_read, send_typing
│   ├── marketing.py       # marketing_messages
│   ├── media.py           # upload, info, download, delete, resumable upload
│   ├── templates.py       # list/get/create/edit/delete/migrate
│   ├── phone_numbers.py   # CRUD + register/deregister/verify/settings/OBA
│   ├── profile.py         # business profile, commerce, compliance,
│                          #   automation, encryption, QR, block_users
│   ├── calls.py           # calls + call_permissions
│   ├── groups.py          # groups + participants + invites + join_requests
│   ├── flows.py           # flows CRUD, assets, publish/deprecate, migrate
│   ├── waba.py            # WABA node, analytics, activities, schedules,
│                          #   assigned_users, subscribed_apps, solutions
│   ├── business.py        # portfolio, client/owned WABAs, credits,
│                          #   preverified numbers, MM-lite onboarding
│   ├── app.py             # app solutions, connected businesses
│   └── users.py           # assigned WABAs
│
└── webhooks/
    ├── signature.py       # verify X-Hub-Signature-256 (app secret)
    ├── parser.py          # raw dict → typed WebhookEvent unions
    ├── events.py          # MessageReceived, StatusUpdate, TemplateUpdate…
    └── fastapi.py         # optional router (extra)
```

Layering: `http.py` knows nothing about WhatsApp; `resources/` build paths +
params; `types/` validate payloads; `builders/` are pure sugar that emit the
same dicts.

## 4. Public API sketch

```python
from whatsapp_business_cloud import Client
from whatsapp_business_cloud.builders import Buttons, ListMessage, TemplateMessage

client = Client(
    access_token="EAAB...",
    phone_number_id="106540352242922",
    waba_id="102290129340398",
    # api_version="v25.0", timeout=30, max_retries=3
)

# --- messages ---
client.messages.send_text(to="15551234567", body="Hello", preview_url=True)
client.messages.send_image(to=..., media_id="80061363...")
client.messages.send_image(to=..., link="https://…/a.png", caption="hi")
client.messages.send_interactive(to=..., interactive=Buttons().body("Pick").add("Yes","y1").add("No","n1"))
client.messages.send_template(to=..., template=TemplateMessage("order_conf", "en_US").body_params("Ana", "1234"))
client.messages.mark_read(message_id="wamid.X", typing=True)
client.messages.send_location / send_contacts / send_reaction / send_document …

# --- media ---
media = client.media.upload("./invoice.pdf")          # -> MediaInfo(id)
info  = client.media.get(media.id)                     # url, mime_type, sha256
path  = client.media.download(media.id, dest="./out")  # auth'd download
client.media.delete(media.id)
handle = client.media.resumable_upload("./banner.jpg") # h:... for templates

# --- templates ---
for t in client.templates.list(status="APPROVED"):      # auto-paginates
    ...
client.templates.create(name="otp", category="AUTHENTICATION", language="en_US", components=[...])
client.templates.edit(template_id, components=[...])
client.templates.delete(name="old")  # or hsm_id / hsm_ids

# --- phone numbers, profile, QR ---
client.phone_numbers.list()
client.phone_numbers.request_code(code_method="SMS")
client.phone_numbers.register(pin="123456")
client.profile.update(about="…", websites=["https://…"])
client.qr_codes.create("Talk to sales", generate_qr_image="PNG")

# --- calls / groups / flows ---
client.calls.connect(to=..., sdp_offer=offer)
client.calls.check_permissions(user_wa_id=...)
group = client.groups.create(subject="VIP", join_approval_mode="auto_approve")
client.groups.invite_link.create(group.id)
client.flows.publish(flow_id)

# --- webhooks ---
from whatsapp_business_cloud.webhooks import verify_signature, parse_event
verify_signature(raw_body, headers["X-Hub-Signature-256"], app_secret)
for event in parse_event(payload):
    match event:                               # typed union
        case TextMessageReceived(m): ...
        case StatusUpdate(s): ...

# --- async ---
async with AsyncClient(...) as c:
    await c.messages.send_text(...)
```

Resource classes are thin: each method = one documented endpoint, returning a
typed model or a `CursorPaginator`. `client.raw_get()/raw_post()` escape hatches
for brand-new fields before the SDK catches up.

## 5. Error handling

```
WhatsAppError
├── ApiError (code, subcode, message, fbtrace_id, details)
│   ├── AuthError (401/190)
│   ├── PermissionError (403)
│   ├── NotFoundError (404)
│   ├── RateLimitError (4, 17, 80007, 131056, 131048, 613) → .retry_after
│   ├── ValidationError (100, 132xxx)
│   ├── TemplateError (131xxx family, paused/rejected)
│   ├── MediaError (131052 download, size limits)
│   ├── RegistrationError (133xxx)
│   └── CallError (138xxx)
├── WebhookSignatureError
└── ValidationError locally (pydantic) passthrough
```

Retry policy: exponential backoff + jitter on `RateLimitError` (honoring
`retry_after`) and 5xx; opt-out via `max_retries=0`.

## 6. Milestones

| # | Phase | Deliverable |
|---|---|---|
| 1 | Scaffold | pyproject, ruff/mypy config, CI skeleton, `http.py` transport + auth + retries, exception tree, `CursorPaginator` |
| 2 | Messages core | `types/messages.py`, `resources/messages.py` — all ~15 payload types + read/typing; `builders.py` for interactive/template |
| 3 | Media | upload/download/delete + resumable-upload handles |
| 4 | Templates | full CRUD + component models + migrate |
| 5 | Phone numbers & profile | registration flow, settings, OBA, profile/commerce/compliance, automation, encryption, QR, block_users |
| 6 | Webhooks | signature verify, typed event parser covering every `field`/message type in api-reference §12 |
| 7 | Extended resources | calls, groups, flows, marketing messages, schedules, WABA analytics/activities |
| 8 | Admin tier | business portfolio, app solutions, assigned users, subscribed apps, preverified numbers, migration |
| 9 | Polish | docs site, README + cookbook examples, error-code table, release to PyPI |

Each phase lands with: typed models, resource methods, unit tests (respx),
docstrings, and a runnable `examples/` script.

## 7. Testing strategy

- **Unit**: respx-mocked Graph API; assert URL, method, JSON body per method.
- **Payload fixtures**: real request/response samples from Meta docs under
  `tests/fixtures/` (messages, webhooks, template create, error envelopes).
- **Webhook**: canned webhook JSON per type; HMAC sign/verify round-trip.
- **Types**: `mypy --strict` in CI; `pyright` optional check.
- **Coverage**: ≥90% on `resources/` + `webhooks/`; builders 100%.
- **Live (manual)**: `tests/live/` gated behind env vars (`WA_TOKEN`,
  `WA_PHONE_NUMBER_ID`, `WA_TEST_RECIPIENT`) — never runs in CI.

## 8. Decisions

- **Name**: `whatsapp-business-cloud` (verify PyPI availability at publish time; fallback `wabapi`).
- **v1 scope — core first**: messages (+ marketing), media, templates, phone
  numbers, profile/QR/block/commerce/automation/encryption, calling, groups,
  flows, webhooks. Partner/admin tier (business portfolio, app solutions,
  pre-verified numbers, assigned users, credits, migration) ships in **v1.1**
  — the `resources/` layout already reserves `business.py`, `app.py`,
  `users.py` for it.
- **Webhooks**: signature verification + typed parser **plus** an optional
  FastAPI router under `whatsapp-business-cloud[fastapi]` that auto-verifies and dispatches.
- **Python**: 3.10+.
- **Excluded**: On-Premises API (deprecated by Meta), Embedded Signup frontend
  JS (documented, not implemented), Payments order APIs beyond sending the
  documented message payloads.

## 9. Adjusted milestones for v1

Phases 1–7 from §6 ship v1 (core). Phase 8 (admin tier) moves to v1.1;
phase 9 polish/release stays last.
