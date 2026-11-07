# Configuration

`Client` / `AsyncClient` constructor options:

| Option | Default | Notes |
|---|---|---|
| `access_token` | — | Required. System-user or user access token |
| `phone_number_id` | `None` | Default sender number; override per call |
| `waba_id` | `None` | Default WABA; override per call |
| `app_id` | `None` | Needed for resumable uploads |
| `api_version` | `"v25.0"` | Graph API version segment |
| `base_url` | `https://graph.facebook.com` | Override for proxies/testing |
| `timeout` | `30.0` | Seconds (httpx) |
| `max_retries` | `3` | Automatic retries on rate limits & 5xx |
| `user_agent` | `whatsapp-cloud-python/…` | Sent on every request |
| `http_client` | `None` | Bring your own `httpx.Client` / `AsyncClient` |

## Retries

```python
client = Client(token, max_retries=0)   # disable
client.retry.base_delay = 1.0           # tune via RetryPolicy
```

Retries apply to `RateLimitError`, HTTP 5xx, and Meta transient codes
(1, 2, 120), honoring the `Retry-After` header when present.

## Raw escape hatch

Any Graph API call not yet covered:

```python
client.raw_request("GET", f"{waba_id}", params={"fields": "analytics"})
client.raw_request("POST", f"{pnid}/messages", json={...})
```
