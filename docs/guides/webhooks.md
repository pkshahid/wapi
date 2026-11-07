# Webhooks

## Verify + parse (framework-agnostic)

```python
from whatsapp_cloud.webhooks import verify_or_raise, parse, InboundMessages, StatusUpdates

verify_or_raise(raw_body, headers["X-Hub-Signature-256"], app_secret)
for event in parse(raw_body):
    match event:
        case InboundMessages() as m:
            for msg in m.messages:
                if msg.type == "text":
                    print(m.sender_phone, msg.text.body)
        case StatusUpdates() as s:
            for st in s.statuses:
                print(st.id, st.status, s.failed)
        case TemplateStatusUpdate() as t:
            print(t.message_template_name, t.event)
```

## FastAPI router

```python
from fastapi import FastAPI
from whatsapp_cloud.webhooks.fastapi import webhook_router
from whatsapp_cloud.webhooks import InboundMessages

app = FastAPI()

async def on_event(event):
    if isinstance(event, InboundMessages):
        for m in event.messages: print(m.type)

app.include_router(
    webhook_router(on_event, verify_token="tok", app_secret="sec", path="/webhook")
)
```

`GET /webhook` answers Meta's verification challenge automatically;
`POST` verifies the signature (when `app_secret` is set), parses, and
dispatches — sync or async handlers both work. `per_event=False` hands
the handler the whole list.

## Event types

| Event | Webhook field |
|---|---|
| `InboundMessages` | `messages` (messages[]) |
| `StatusUpdates` | `messages` (statuses[]) |
| `CallEvent` | `calls` |
| `TemplateStatusUpdate` / `Quality` / `Components` / `Category` | template lifecycle |
| `AccountUpdate` / `AccountAlert` / `AccountReviewUpdate` | account |
| `PhoneNumberNameUpdate` / `PhoneNumberQualityUpdate` | number |
| `SmbMessageEcho` / `SmbAppStateSync` / `History` | coexistence |
| `UserPreferences` / `MessagingHandover` / `Security` / `PaymentConfigurationUpdate` / `BusinessCapabilityUpdate` | misc |
| `UnknownEvent` | anything new — raw `value` |
