# Calls, Groups & Flows

## Calling (VoIP)

```python
perm = client.calls.check_permissions(user_wa_id="1555")
if perm.status == "granted":
    call = client.calls.connect("1555", sdp=local_sdp_offer)
    call.call_id

client.calls.accept("call-id", sdp=local_sdp_answer)
client.calls.pre_accept("call-id", sdp=sdp)
client.calls.reject("call-id")
client.calls.terminate("call-id")
client.calls.media_update("call-id", sdp=new_offer)
```

Call-related webhooks arrive on the `calls` field (`CallEvent`).

## Groups

```python
g = client.groups.create(subject="VIP", join_approval_mode="auto_approve")
client.groups.get(g.id); client.groups.update(g.id, subject="New")
client.messages.send_text(to=g.id, body="hi group", recipient_type="group")

client.groups.add_participants(g.id, ["1555"])          # max 8/call
client.groups.remove_participants(g.id, ["1555"])
client.groups.create_invite_link(g.id); client.groups.revoke_invite_link(g.id)
list(client.groups.list_join_requests(g.id))
client.groups.approve_join_requests(g.id, ["jr1"])
client.groups.reject_join_requests(g.id, ["jr2"])
client.groups.delete(g.id)
```

## Flows

```python
f = client.flows.create(name="survey", categories=["SURVEY"],
                        flow_json={"version": "5.0", "screens": [...]}, publish=True)
client.flows.get(f.id, fields=["status", "validation_errors", "health_status"])
client.flows.update_json(f.id, {"version": "5.0", "screens": [...]})
client.flows.update(f.id, endpoint_uri="https://me/flow-endpoint")
client.flows.preview(f.id)              # shareable web preview URL
client.flows.publish(f.id); client.flows.deprecate(f.id)
client.flows.delete(f.id)               # DRAFT only
client.flows.migrate(source_waba_id="src", source_flow_names=["s1"])
```

Send a flow to users with `FlowMessage` — see [Messages](messages.md).
