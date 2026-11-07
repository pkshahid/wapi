# Async Client

`AsyncClient` exposes the same resources — every method is awaitable.

```python
import asyncio
from whatsapp_cloud import AsyncClient
from whatsapp_cloud.builders import Buttons

async def main():
    async with AsyncClient("EAAB...", phone_number_id="...", waba_id="...") as c:
        resp = await c.messages.send_text(to="1555...", body="hi")
        media = await c.media.upload("pic.png")
        async for t in c.templates.list(status="APPROVED"):   # async pagination
            print(t.name)
        await c.messages.mark_read("wamid.x", typing=True)

asyncio.run(main())
```

Differences vs sync: list methods return `AsyncCursorIterator` — iterate
with `async for`.
