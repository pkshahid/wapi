# Errors & Retries

Every non-2xx response raises an `ApiError` subclass:

```python
from whatsapp_cloud import ApiError, RateLimitError, ValidationError, TemplateError

try:
    client.messages.send_text(to, "hi")
except RateLimitError as e:
    time.sleep(e.retry_after or 1)
except TemplateError as e:
    print(e.code, e.subcode, e.details)
except ApiError as e:
    print(e.status_code, e.error_type, e.fbtrace_id)
```

| Class | When |
|---|---|
| `AuthError` | 401 / code 190 — bad or expired token |
| `PermissionError_` | 403 — missing scope/capability |
| `NotFoundError` | 404 |
| `RateLimitError` | codes 4/17/32/341/368/613/80007/130429/131048/131056 — has `.retry_after` |
| `ValidationError` | 132xxx — bad params |
| `MessagingError` | 131xxx — send/delivery failures |
| `TemplateError` | template ops |
| `MediaError` | media ops |
| `RegistrationError` | 133xxx — number registration |
| `CallError` | 138xxx — calling API |
| `WebhookSignatureError` | invalid webhook signature |

Automatic retries (default 3, exponential backoff + jitter) apply to
rate limits, 5xx, and transient codes 1/2/120.
