# Phone Numbers & Profile

## Registration flow

```python
client.phone_numbers.add(cc="1", phone_number="5551234567", verified_name="Shop")
client.phone_numbers.request_code(code_method="SMS")     # or "VOICE"
client.phone_numbers.verify_code("123456")
client.phone_numbers.register(pin="123456")              # 6-digit 2FA pin
client.phone_numbers.deregister()
```

## Inspect & configure

```python
client.phone_numbers.list()
client.phone_numbers.get(fields=["quality_rating", "verified_name", "throughput"])
client.phone_numbers.update(webhook_url="https://me/hook", new_display_name="Shop")
client.phone_numbers.get_settings(include_sip_credentials=True)
client.phone_numbers.update_settings(calling={"status": "ENABLED"})
client.phone_numbers.get_official_status()
```

## Business profile

```python
client.profile.get()
client.profile.update(about="We help", websites=["https://x"], vertical="PROF_SERVICES",
                      email="hi@x.com", address="1 Main St")
```

## Commerce, compliance, automation, encryption

```python
client.commerce.update(is_cart_enabled=True, is_catalog_visible=True)
client.compliance.update(entity_name="Acme", entity_type="PRIVATE_LIMITED",
    grievance_officer_details={...}, customer_care_details={...})
client.automation.configure(enable_welcome_message=True, prompts=["Hi!"])
client.encryption.set_key(open("pub.pem").read())       # Flows E2E
```

## QR codes & blocked users

```python
client.qr_codes.create_or_update(prefilled_message="Hi", generate_qr_image="PNG")
list(client.qr_codes.list()); client.qr_codes.delete("QR-ID")

client.blocked.list(); client.blocked.block("1555"); client.blocked.unblock(["1555"])
```
