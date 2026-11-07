# Templates

```python
# iterate (auto-paginated)
for t in client.templates.list(status="APPROVED", category="UTILITY"):
    print(t.id, t.name, t.quality_score)

t = client.templates.get("template_id", fields=["name", "status", "components"])

# create
client.templates.create(
    name="order_conf", language="en_US", category="UTILITY",
    components=[
        {"type": "HEADER", "format": "TEXT", "text": "Order {{1}}",
         "example": {"header_text": ["#123"]}},
        {"type": "BODY", "text": "Hi {{name}}, total {{total}}",
         "example": {"body_text_named_params": [
             {"param_name": "name", "example": "Ana"},
             {"param_name": "total", "example": "$10"}]},
        {"type": "FOOTER", "text": "Thanks"},
        {"type": "BUTTONS", "buttons": [
            {"type": "QUICK_REPLY", "text": "Track"},
            {"type": "URL", "text": "View", "url": "https://x/{{1}}",
             "example": ["https://x/1"]}]},
    ],
    parameter_format="named",
)

# edit / delete / migrate
client.templates.edit("template_id", category="MARKETING", allow_category_change=True)
client.templates.delete(name="old")                      # all languages
client.templates.delete(name="old", hsm_id="123")        # one language
client.templates.delete(hsm_ids=["1", "2"])              # bulk
client.templates.migrate(source_waba_id="src", template_names=["otp"])
```

Media header examples need a resumable-upload handle — see
[Media](media.md#resumable-uploads).
