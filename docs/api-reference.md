# WhatsApp Business Platform — Complete API Reference

Catalog of every endpoint, method, and option exposed by the WhatsApp Business
Platform (Cloud API + Business Management API + Flows API), verified against
Meta's official API reference (November 2026, Graph API v21+).

This document is the build spec for the `whatsapp-business-cloud` package: every resource class in
the plan maps to a section here.

---

## 1. Fundamentals

| Item | Value |
|---|---|
| Base URL | `https://graph.facebook.com/{VERSION}` |
| Current versions | `v21.0` – `v25.0` (version is part of the path, configurable in the client) |
| Auth | `Authorization: Bearer <ACCESS_TOKEN>` (system-user or user token) |
| Content types | `application/json` (most calls), `multipart/form-data` (media/asset uploads) |
| Pagination | Cursor-based: `limit`, `after`, `before`; response `paging.cursors` / `paging.next` |
| Field selection | `?fields=a,b,c` on almost every GET |

### Required permissions

| Scope | Needed for |
|---|---|
| `whatsapp_business_messaging` | Sending messages, media upload/download, calls, groups, marketing messages |
| `whatsapp_business_management` | Templates, phone numbers, registration, profiles, QR codes, flows, webhooks, WABA admin |
| `business_management` | Business portfolio / partner-level endpoints |
| `catalog_management` | Product/catalog messages (plus commerce settings) |

### Core IDs

| ID | Used in |
|---|---|
| `{Phone-Number-ID}` | Send messages, media, calls, groups, profile, registration, settings |
| `{WABA-ID}` | Templates, phone number management, subscribed apps, flows, analytics |
| `{Business-ID}` | Portfolio-level endpoints (owned/client WABAs, phone numbers, credits) |
| `{Application-ID}` | App-level partner endpoints |
| `{Media-ID}` / `{Media-URL}` | Media retrieval/download/deletion |
| `{FLOW-ID}` | Flows management |
| `{TEMPLATE_ID}` | Single-template get/edit |
| `{group_id}` | Group node operations |

---

## 2. Messages — `whatsapp-business-phone-number`

The central endpoint. One `POST` handles every outbound message type, plus
read receipts and typing indicators.

### `POST /{Phone-Number-ID}/messages`

Base fields (all message types):

| Field | Type | Required | Notes |
|---|---|---|---|
| `messaging_product` | `"whatsapp"` | ✓ | Always |
| `recipient_type` | `"individual"` \| `"group"` | ✓ | `group` for group chats |
| `to` | string | ✓ | E.164 phone number, WhatsApp user ID, or group ID |
| `type` | string | ✓ | See message types below |
| `context` | object | | `{ "message_id": "<wamid>" }` — quote/reply |
| `biz_opaque_callback_data` | string | | ≤512 chars, echoed back in status webhooks |
| `status` | `"read"` | | For read receipts (see below) |

#### Message types (`type` field)

| `type` | Payload key | Options |
|---|---|---|
| `text` | `text` | `body` (≤4096), `preview_url` (bool) for link previews |
| `image` | `image` | `id` or `link`, `caption` |
| `audio` | `audio` | `id` or `link` |
| `video` | `video` | `id` or `link`, `caption` |
| `document` | `document` | `id` or `link`, `caption`, `filename` |
| `sticker` | `sticker` | `id` or `link` (WebP 512×512, ≤100KB static / 500KB animated) |
| `location` | `location` | `latitude`, `longitude`, `name`, `address` |
| `contacts` | `contacts` | Array of contact objects: `name` (`formatted_name`, `first_name`…), `phones` (`phone`, `wa_id`, `type`), `emails`, `urls`, `addresses`, `birthday`, `org` |
| `reaction` | `reaction` | `message_id`, `emoji` (empty string removes reaction) |
| `template` | `template` | `name`, `language.code`, `components[]` (see §4) |
| `interactive` | `interactive` | `type`, `header`, `body`, `footer`, `action` (see below) |
| `address` | `address` (interactive, India) | Address-form interactive message |
| `location_request` | via `interactive.action.name: "send_location"` | Requests user's location |

#### Interactive message `action` options

| `interactive.type` | `action` fields |
|---|---|
| `button` (reply buttons) | `buttons[]` — max 3, each `{type:"reply", reply:{id,title(≤20)}}` |
| `list` | `button` (label), `sections[]` — max 10, rows per section max 10, each row `{id,title(≤24),description}` |
| `cta_url` | `name:"cta_url"`, `parameters:{display_text,url}` |
| `catalog_message` | `name:"catalog_message"`, `parameters:{thumbnail_product_retailer_id?}` |
| `product` (SPM) | `catalog_id`, `product_retailer_id` |
| `product_list` (MPM) | `catalog_id`, `sections[]` with `product_items[]` (`product_retailer_id`), max 30 items |
| `flow` | `name:"flow"`, `parameters:{flow_token?, flow_id` or `flow_name`, flow_cta, flow_action:"navigate"\|"data_exchange", flow_action_payload:{screen, data}}`, `mode:"draft"` for draft flows |
| `call_permission_request` | Call permission request interactive |
| `order_details` | India payments order message |
| `order_status` | Order status update |
| `wa_pay` / `payment_settings` | Brazil/ROW payments |
| `voice_call` | Voice call CTA button |
| `location_request_message` | `name:"send_location"` body |

Headers for interactive: `type: text|image|video|document` + matching payload;
`sub_text` optional. `body.text`, `footer.text` optional/required by type.

#### Read receipts & typing indicator

Same endpoint, sentinel payload:

```json
{ "messaging_product":"whatsapp", "status":"read",
  "message_id":"<wamid>",
  "typing_indicator": { "type":"text" } }
```

`typing_indicator` is optional; include to show "typing…" in the user's app.

#### Media upload constraints

| Type | Formats | Max |
|---|---|---|
| Image | JPEG, PNG | 5 MB |
| Video | MP4, 3GPP (H.264/AAC only) | 16 MB |
| Audio | AAC, MP4, MPEG, AMR, OGG (Opus only) | 16 MB |
| Document | Any MIME | 100 MB |
| Sticker | WebP 512×512 | 100 KB / 500 KB animated |

### `POST /{Phone-Number-ID}/marketing_messages` — Marketing Messages (MM Lite) API

Lightweight marketing sends with Meta-side optimizations. Body:
`messaging_product`, `recipient_type:"individual"`, `to`, `type:"template"`,
`template{...}` (same schema as messages), plus optional
`product_policy: "CLOUD_API_FALLBACK"|"STRICT"` and
`message_activity_sharing: bool`.

---

## 3. Media

| Method | Path | Purpose | Notes |
|---|---|---|---|
| `POST` | `/{Phone-Number-ID}/media` | Upload media | `multipart/form-data`: `file`, `messaging_product:"whatsapp"`, `type` (MIME). Returns `{id}`. ID valid ~30 days |
| `GET` | `/{Media-ID}` | Get media info/URL | Returns `url`, `mime_type`, `sha256`, `file_size`. Query `phone_number_id` required when token covers multiple numbers |
| `GET` | `/{Media-URL}` | Download bytes | GET the returned URL **with** `Authorization` header (and `User-Agent` on some setups) |
| `DELETE` | `/{Media-ID}` | Delete media | Query `phone_number_id` when ambiguous |

### Resumable Upload API (Graph API file upload)

Required for **template header media** and **profile pictures** — produces an
asset *handle* (`h:…`) instead of a media ID:

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/{App-ID}/uploads?file_name=…&file_length=…&file_type=…` | Create upload session → returns `upload_id` (a `h:` handle) |
| `POST` | `/{Upload-ID}` (header `OAuth <token>`, `file_offset`) | Upload binary, returns handle for use in `profile_picture_handle` / template `example.header_handle` |

---

## 4. Message Templates — `whatsapp-business-account`

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/{WABA-ID}/message_templates` | List templates. Query: `fields`, `limit`, `after`, `before`; filters via `fields` (`name`, `category`, `status`, `language`, `quality_score`, `components`, `id`, `rejected_reason`) |
| `POST` | `/{WABA-ID}/message_templates` | Create template |
| `GET` | `/{TEMPLATE_ID}` | Get one template (`fields`) |
| `POST` | `/{TEMPLATE_ID}` | Edit template |
| `DELETE` | `/{WABA-ID}/message_templates` | Delete by `name` (all languages), `name`+`hsm_id` (one language), or `hsm_ids` JSON array (≤100) |
| `POST` | `/{WABA-ID}/migrate_message_templates` | Migrate templates between WABAs (source/destination WABA + template names) |

**Create/edit body:** `name`* (lowercase, `_`), `language`* (e.g. `en_US`),
`category`* (`UTILITY`\|`MARKETING`\|`AUTHENTICATION`), `components[]`,
`parameter_format` (`named`\|`positional`), `allow_category_change`,
`cta_url_link_tracking_opted_out`, `message_send_ttl_seconds`,
`sub_category`, `display_format`, `library_template_name` +
`library_template_body_inputs`/`library_template_button_inputs` (clone from
library), `is_primary_device_delivery_only`, `send_type` (MM Lite).

**Components:** `HEADER` (`format: TEXT|IMAGE|VIDEO|DOCUMENT|LOCATION|PRODUCT`,
`example.header_text` / `example.header_handle`), `BODY` (`text` with
`{{1}}`/`{{name}}` params, `example.body_text`/`body_text_named_params`),
`FOOTER`, `BUTTONS` (`QUICK_REPLY`, `URL`, `PHONE_NUMBER`, `OTP`,
`COPY_CODE`, `CATALOG`, `MPM`, `SPM`, `FLOW`, `VOICE_CALL`, `APP`),
`CAROUSEL` (media card carousels), `LIMITED_TIME_OFFER`.

**Statuses:** `APPROVED`, `PENDING`/`IN_APPEAL`, `REJECTED`, `PAUSED`,
`DISABLED`, `PENDING_DELETION`, `DELETED`, `LIMIT_EXCEEDED`. Quality scores
`GREEN`/`YELLOW`/`RED`/`UNKNOWN` via `quality_score` field.

Rate limit: max 100 template creates per WABA per hour.

---

## 5. Phone Numbers

| Method | Path | Purpose | Body/params |
|---|---|---|---|
| `GET` | `/{WABA-ID}/phone_numbers` | List numbers on WABA | `fields`, `filtering` (e.g. `[{"field":"account_mode","operator":"EQUAL","value":"SANDBOX"}]`), `sort` (`creation_time.asc|desc`, `last_onboarded_time.asc|desc`), paging |
| `POST` | `/{WABA-ID}/phone_numbers` | Add number to WABA | `cc`*, `phone_number`* (E.164 no `+`), `verified_name`*, `migrate_phone_number`, `preverified_id` |
| `GET` | `/{Phone-Number-ID}` | Number details | `fields`: `id`, `verified_name`, `display_phone_number`, `quality_rating`, `code_verification_status`, `platform_type`, `throughput`, `webhook_configuration`, `last_onboarded_time`, `is_official_business_account`, `account_mode`, `messaging_limit_tier`, `status`, `certificate`, `name_status`, `new_name_status`, `search_visibility`, `health_status` |
| `POST` | `/{Phone-Number-ID}` | Update number config | `webhook_configuration`, `webhook_url`, `pin`, `new_display_name`, `username`, `search_visibility`, `connection_status`, `whatsapp_business_api_data` |
| `POST` | `/{Phone-Number-ID}/register` | Register (after verification) | `messaging_product`, `pin`* (6-digit 2FA), `data_localization_region`, `backup` |
| `POST` | `/{Phone-Number-ID}/deregister` | Deregister | — |
| `POST` | `/{Phone-Number-ID}/request_code` | Send verification code | `code_method: SMS\|VOICE`*, `language` |
| `POST` | `/{Phone-Number-ID}/verify_code` | Verify code | `code`* |
| `GET` | `/{Phone-Number-ID}/settings` | Get settings | `include_sip_credentials` |
| `POST` | `/{Phone-Number-ID}/settings` | Update settings | One of: `calling{...}`, `user_identity_change{...}`, `payload_encryption{...}`, `storage_configuration{...}` |
| `GET` | `/{Phone-Number-ID}/official_business_account` | OBA status | `fields` |
| `POST` | `/{Phone-Number-ID}/official_business_account` | Update OBA | — |

---

## 6. Business Profile, Commerce, Automation, QR

| Method | Path | Purpose | Body/params |
|---|---|---|---|
| `GET` | `/{Phone-Number-ID}/whatsapp_business_profile` | Get profile | `fields`: `about`, `address`, `description`, `email`, `profile_picture_url`, `websites`, `vertical` |
| `POST` | `/{Phone-Number-ID}/whatsapp_business_profile` | Update profile | `messaging_product`*, `about`, `address`, `description`, `email`, `websites[]`, `vertical`, `profile_picture_handle` (from Resumable Upload) |
| `GET` | `/{WhatsApp-Business-Profile-ID}` | Profile node (alt) | `fields` |
| `POST` | `/{WhatsApp-Business-Profile-ID}` | Update profile node | same fields |
| `GET` | `/{Phone-Number-ID}/whatsapp_commerce_settings` | Get commerce settings | returns `is_cart_enabled`, `is_catalog_visible`, `id` |
| `POST` | `/{Phone-Number-ID}/whatsapp_commerce_settings` | Set commerce | query `is_cart_enabled`, `is_catalog_visible` |
| `GET` | `/{Phone-Number-ID}/business_compliance_info` | India compliance info | `fields` |
| `POST` | `/{Phone-Number-ID}/business_compliance_info` | Update compliance | `entity_name`*, `entity_type`*, `grievance_officer_details`*, `customer_care_details`*, `is_registered`, `entity_type_custom` |
| `POST` | `/{Phone-Number-ID}/conversational_automation` | Welcome message config | `enable_welcome_message`, `prompts[]` (ice breakers), `commands[]` (`command_name`, `command_description`) |
| `GET` | `/{Phone-Number-ID}/message_qrdls` | List QR codes | `fields`, `code`, `limit` ≤25, paging |
| `POST` | `/{Phone-Number-ID}/message_qrdls` | Create/update QR | `prefilled_message` (≤140 chars), `generate_qr_image: PNG\|SVG`; update via `code` |
| `GET` | `/{Phone-Number-ID}/message_qrdls/{QR-Code-ID}` | Get QR code | `fields` |
| `DELETE` | `/{Phone-Number-ID}/message_qrdls/{QR-Code-ID}` | Delete QR code | — |
| `GET` | `/{Phone-Number-ID}/whatsapp_business_encryption` | Get Flows pubkey | `fields` |
| `POST` | `/{Phone-Number-ID}/whatsapp_business_encryption` | Set pubkey | `business_public_key`* (PEM; for Flows end-to-end encryption) |
| `GET` | `/{Phone-Number-ID}/block_users` | List blocked users | — |
| `POST` | `/{Phone-Number-ID}/block_users` | Block users | `block_users:[{user}]`, `messaging_product` |
| `DELETE` | `/{Phone-Number-ID}/block_users` | Unblock | same body |

---

## 7. Calling API (VoIP)

| Method | Path | Purpose | Body/params |
|---|---|---|---|
| `GET` | `/{Phone-Number-ID}/call_permissions` | Check permission to call a user | `user_wa_id`* → `permission.status` (`granted`/`pending`/`denied`/`expired`), `actions[]` (`start_call`, `send_call_permission_request` + rate `limits`) |
| `POST` | `/{Phone-Number-ID}/calls` | Manage calls | `messaging_product`, `action`* |

Call actions (body `action` field): `connect` (initiate; `to` + `session:{sdp_type:"offer", sdp}`),
`pre_accept`, `accept` (`session` answer), `reject`, `terminate`
(`call_id` body variant), `media_update`. Optional
`biz_opaque_callback_data`. Call settings via `POST /{Phone-Number-ID}/settings`
`calling` object (enable calling, call icon visibility, SIP credentials,
callback permission restrictions). Webhooks field: `calls` (SDP events,
connect/terminate, permission updates).

---

## 8. Groups

| Method | Path | Purpose | Body/params |
|---|---|---|---|
| `GET` | `/{Phone-Number-ID}/groups` | List groups | `limit` ≤1024, paging |
| `POST` | `/{Phone-Number-ID}/groups` | Create group | `subject`* ≤128, `description` ≤2048, `join_approval_mode: approval_required\|auto_approve` |
| `GET` | `/{group_id}` | Group info | `fields` (`subject`, `description`, `creation_timestamp`, `invite_link`, `join_approval_mode`, `is_locked`, `participants`…) |
| `POST` | `/{group_id}` | Update group | `subject`, `description`; profile pic via `profile_picture_file` or multipart `file` (JPEG ≤5MB square) |
| `DELETE` | `/{group_id}` | Delete/leave group | — |
| `POST` | `/{group_id}/participants` | Add members | `participants[]` (phone/WA-ID, max 8/request) |
| `DELETE` | `/{group_id}/participants` | Remove members | same |
| `POST` | `/{group_id}/invite_link` | Create invite link | — |
| `DELETE` | `/{group_id}/invite_link` | Revoke invite link | — |
| `GET` | `/{group_id}/join_requests` | List join requests | — |
| `POST` | `/{group_id}/join_requests` | Approve | `join_requests[]` IDs |
| `DELETE` | `/{group_id}/join_requests` | Reject | `join_requests[]` IDs |

Group messages are sent via `POST /{Phone-Number-ID}/messages` with
`recipient_type:"group"` and `to:<group_id>`.

---

## 9. Flows API (management)

Flows live under the WABA; sent via interactive `flow` messages or FLOW button
templates.

| Method | Path | Purpose | Params |
|---|---|---|---|
| `POST` | `/{WABA-ID}/flows` | Create flow | `name`*, `categories[]`* (`SIGN_UP`, `SIGN_IN`, `APPOINTMENT_BOOKING`, `LEAD_GENERATION`, `CONTACT_US`, `CUSTOMER_SUPPORT`, `SURVEY`, `OTHER`), `flow_json`, `publish`, `clone_flow_id`, `endpoint_uri` |
| `GET` | `/{WABA-ID}/flows` | List flows | paging |
| `GET` | `/{FLOW-ID}` | Flow details | `fields`: `id`, `name`, `categories`, `preview`, `status` (`DRAFT`\|`PUBLISHED`\|`DEPRECATED`\|`BLOCKED`\|`THROTTLED`), `validation_errors`, `json_version`, `data_api_version`, `endpoint_uri`, `whatsapp_business_account`, `application`, `health_status`, `metrics` |
| `POST` | `/{FLOW-ID}` | Update metadata | `name`, `categories`, `endpoint_uri`, `application_id` |
| `DELETE` | `/{FLOW-ID}` | Delete (DRAFT only) | — |
| `POST` | `/{FLOW-ID}/assets` | Update flow JSON | `multipart`: `name:"flow.json"`, `asset_type:"FLOW_JSON"`, `file` (≤10MB) |
| `GET` | `/{FLOW-ID}/assets` | List assets | — |
| `GET` | `/{FLOW-ID}?fields=preview.invalidate(<bool>)` | Web preview URL | `interactive`, `flow_token` URL params |
| `POST` | `/{FLOW-ID}/publish` | Publish | — |
| `POST` | `/{FLOW-ID}/deprecate` | Deprecate | — |
| `POST` | `/{WABA-ID}/migrate_flows` | Copy flows across WABAs | query `source_waba_id`*, `source_flow_names[]` (≤100) |
| `GET` | `/{Message-History-ID}/events` | Message history events | `delivery_status`, `fields`, paging |

---

## 10. WhatsApp Business Account node

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/{WABA-ID}` | WABA details; `fields` incl. `name`, `currency`, `timezone_id`, `message_template_namespace`, `on_behalf_of_business_info`, `primary_business_location`, `is_enabled_for_insights`, **`analytics`** (conversation costs/volume), **`template_analytics`**, `health_status`, `account_review_status`, `business_capabilities`, `pricing_configuration` |
| `POST` | `/{WABA-ID}` | Update WABA (`name`, `timezone_id`) |
| `GET` | `/{WABA-ID}/activities` | Account activity log |
| `GET` | `/{WABA-ID}/solutions` | Multi-partner solutions attached |
| `GET` | `/{WABA-ID}/schedules` + `POST` | Scheduled template campaigns (`hsm_id`, `audience_id`, `waba_cs_id`, `delivery_time`, `name`, `description`) |
| `GET`/`POST`/`DELETE` | `/{WABA-ID}/assigned_users` | Manage WABA user access (`user`, `tasks[]` permission tasks; GET requires `business` param) |
| `GET`/`POST`/`DELETE` | `/{WABA-ID}/subscribed_apps` | Webhook app subscription; POST body `override_callback_uri`, `verify_token` |
| `GET` | `/{Migration-Intent-ID}` | WABA migration intent status |

**Analytics fields** on `GET /{WABA-ID}`: `analytics.start`, `.end`,
`.granularity` (`HALF_HOUR`|`DAY`|`MONTH`), `.phone_numbers[]`; and
`template_analytics` (per-template sent/delivered/read/clicked).

---

## 11. Business portfolio & partner endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/{Business-ID}` | Business portfolio details |
| `GET` | `/{Business-ID}/whatsapp_business_accounts` | All WABAs (`business_type: ENTERPRISE\|SMB`, `find`, paging) |
| `POST` | `/{Business-ID}/whatsapp_business_accounts` | Create WABA |
| `GET` | `/{Business-ID}/client_whatsapp_business_accounts` | Client WABAs (`business_type: STANDARD\|PREMIUM\|ENTERPRISE`) |
| `GET` | `/{Business-ID}/owned_whatsapp_business_accounts` | Owned WABAs (`first`/`last` paging, `find`) |
| `POST` | `/{Business-ID}/add_phone_numbers` | Add phone number to business |
| `GET` | `/{Business-ID}/preverified_numbers` | List pre-verified numbers (`phone_number`, `code_verification_status` filters) |
| `POST` | `/{Business-ID}/share_preverified_numbers` | Share pre-verified number with another business |
| `GET` | `/{Business-ID}/extendedcredits` | Credit lines (`order_by_is_owned_credential`) |
| `POST` | `/{Business-ID}/onboard_partners_to_mm_lite` | Onboard partner to MM Lite (`solution_id`) |
| `GET` | `/{User-ID}/assigned_whatsapp_business_accounts` | WABAs a user can access |
| `GET` | `/{Application-ID}/connected_client_businesses` | App's connected client businesses |
| `GET` | `/{Application-ID}/whatsapp_business_solutions` | App's multi-partner solutions (`role` filter) |
| `POST` | `/{Application-ID}/whatsapp_business_solution` | Create solution |
| `GET` | `/{Solution-ID}` + `/access_token` (requires `business_id`), `POST /accept`, `/reject`, `/send_deactivation_request`, `/accept_deactivation_request`, `/reject_deactivation_request` | Multi-partner solution lifecycle |
| `GET`/`POST`/`DELETE` | `/{Pre-Verified-Phone-Number-ID}` (+ `/request_code`, `/verify_code`, `/partners`) | Pre-verified number lifecycle |
| `GET` | `/{WhatsApp-Account-Number-ID}` | Messaging-account number details |
| `GET` | `/{WABA-Bot-ID}` | Meta Business Bot details |

---

## 12. Webhooks

| Side | Detail |
|---|---|
| Verification | `GET <callback>` with `hub.mode`, `hub.verify_token`, `hub.challenge` → echo `hub.challenge` |
| Events | `POST <callback>` JSON `{object:"whatsapp_business_account", entry:[{id, changes:[{field, value}]}]}` |
| Signature | `X-Hub-Signature-256`: `sha256=` HMAC of raw body with **app secret** |
| Subscription | App dashboard or `POST /{WABA-ID}/subscribed_apps` (with optional `override_callback_uri`, `verify_token`) |

### Webhook `field` values (change types)

`messages` (inbound messages + statuses), `message_template_status_update`,
`message_template_quality_update`, `message_template_components_update`,
`template_category_update`, `account_update`, `account_alerts`,
`account_review_update`, `business_capability_update`,
`phone_number_name_update`, `phone_number_quality_update`, `history`,
`messaging_handovers`, `partner_solutions`, `payment_configuration_update`,
`security`, `smb_app_state_sync`, `smb_message_echoes`, `standby`,
`user_preferences`, `group_text_messages`, `calls`, `flows`.

### `messages` value payloads

- Inbound `messages[]` types: `text`, `image`, `audio`, `video`, `document`,
  `sticker`, `location`, `contacts`, `reaction`, `interactive`
  (`button_reply`, `list_reply`, `nfm_reply` for Flows, `product_inquiry`,
  `order`, `address`), `button`, `order`, `system`, `referral`,
  `unknown`/unsupported, `group_*`, `call_*`.
- `statuses[]`: `sent`, `delivered`, `read`, `failed` (with `errors[]` code +
  `error_data.details`), `warning`; includes `conversation{id, origin.type}`
  and `pricing{pricing_model, category, billable}`.
- `contacts[]` (sender `wa_id`, `profile.name`), `metadata`
  (`display_phone_number`, `phone_number_id`), `errors[]`, `identity`
  (user identity change hash).
- `echoes` (SMB/coexistence), `history` (chat sync), `smb_app_state_sync`.

---

## 13. Supporting APIs & mechanics

- **OAuth / Embedded Signup**: `GET /oauth/access_token` (code → user token);
  `GET /{App-ID}/subscriptions` to manage webhook field subscriptions.
- **Coexistence (Business app + API)**: `POST /{Phone-Number-ID}/smb_app_data`
  (chat history sync payload from embedded signup).
- **User identity change**: check `settings` → `user_identity_change`;
  webhook `identity` field carries the identity hash; verify before trusting
  profile data.
- **Error model**: `{error:{message,type,code,error_subcode,fbtrace_id,
  error_data{details},error_user_title,error_user_msg}}`. Common families:
  131xxx (send/template errors), 132xxx (params), 133xxx (registration/phone),
  4xx OAuth, rate limits (`#4`/80007/131056 pair-rate).
- **Throughput**: ~80 msg/s per phone number (1,000/s high-throughput tier);
  template pacing + per-user marketing template limits apply.
- **24-hour customer service window**: free-form messages only inside the
  window opened by the last inbound user message; outside → template required.

---

## 14. Endpoint coverage summary (build checklist)

| Resource module | Endpoints |
|---|---|
| `messages` | 1 POST, ~15 payload types |
| `marketing_messages` | 1 |
| `media` | 4 (+2 resumable upload) |
| `templates` | 6 |
| `phone_numbers` | 11 (WABA list/add + node get/update + register/deregister/request_code/verify_code/settings/OBA) |
| `profile` | 4 (+ profile node 2) |
| `commerce` / `compliance` / `automation` / `encryption` / `block` | 2+2+1+2+3 |
| `calling` | 2 (+ settings) |
| `groups` | 12 |
| `qr_codes` | 4 |
| `flows` | 11 |
| `waba` (account, analytics, activities, schedules, users, subscribed_apps, solutions, migration) | 12 |
| `business` (portfolio, client/owned WABAs, phone numbers, credits, preverified, MM-lite) | 9 |
| `app`/`solutions`/`user`/`account_number`/`bot` | 10 |
| **Total** | **~100 operations** |
