"""Quickstart for whatsapp_business_cloud — set env vars and run against a real WABA.

    export WA_TOKEN=EAAB...
    export WA_PHONE_NUMBER_ID=106540352242922
    export WA_WABA_ID=102290129340398
    export WA_RECIPIENT=15551234567
    python examples/quickstart.py
"""

from __future__ import annotations

import os

from whatsapp_business_cloud import Client
from whatsapp_business_cloud.builders import Buttons, Template

client = Client(
    access_token=os.environ["WA_TOKEN"],
    phone_number_id=os.environ["WA_PHONE_NUMBER_ID"],
    waba_id=os.environ["WA_WABA_ID"],
)
to = os.environ["WA_RECIPIENT"]

# Send a text message.
resp = client.messages.send_text(to=to, body="Hello from whatsapp_business_cloud!")
print("sent:", resp.message_id)

# Send reply buttons.
client.messages.send_interactive(
    to=to,
    interactive=Buttons().body("Was that helpful?").add("Yes", "y").add("No", "n"),
)

# Send a template (outside the 24h window).
client.messages.send_template(
    to=to, template=Template("hello_world", "en_US")
)

# List phone numbers and templates.
print("numbers:", [n.display_phone_number for n in client.phone_numbers.list()])
print("templates:", [t.name for t in client.templates.list(status="APPROVED")])

client.close()
