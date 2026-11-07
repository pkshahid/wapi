"""Fluent builders for outbound message payloads.

Builders only *construct* the JSON structure Meta expects — they never touch
the network. Pass them (or an equivalent dict) to ``client.messages.*``::

    client.messages.send_interactive(to, Buttons()
        .body("Are you sure?")
        .add("Yes", id="yes")
        .add("No", id="no"))

    client.messages.send_template(to, Template("order_conf", "en_US")
        .body_params("Ana", "order-1234"))
"""

from __future__ import annotations

from typing import Any

from .http import clean_body

__all__ = [
    "Button",
    "Buttons",
    "CallPermissionRequest",
    "CatalogMessage",
    "Contact",
    "CtaUrl",
    "FlowAction",
    "FlowMessage",
    "Interactive",
    "ListMessage",
    "LocationRequest",
    "Media",
    "Param",
    "Payload",
    "Product",
    "ProductList",
    "ProductSection",
    "Row",
    "Section",
    "Template",
    "Text",
]


class Payload:
    """Anything that serializes to a dict via :meth:`to_dict`."""

    def to_dict(self) -> dict[str, Any]:  # pragma: no cover - interface
        raise NotImplementedError


def as_dict(value: Any) -> dict[str, Any]:
    """Accept a ``Payload`` or plain dict."""
    if isinstance(value, Payload):
        return value.to_dict()
    return dict(value)


class Text(Payload):
    """``type: text`` payload."""

    def __init__(self, body: str, *, preview_url: bool = False) -> None:
        self.body = body
        self.preview_url = preview_url

    def to_dict(self) -> dict[str, Any]:
        return {"body": self.body, "preview_url": self.preview_url}


class Media(Payload):
    """An ``id``- or ``link``-based media object (image/audio/video/document/sticker)."""

    def __init__(
        self,
        *,
        media_id: str | None = None,
        link: str | None = None,
        caption: str | None = None,
        filename: str | None = None,
    ) -> None:
        if not media_id and not link:
            raise ValueError("Media requires media_id or link")
        self.media_id = media_id
        self.link = link
        self.caption = caption
        self.filename = filename

    def to_dict(self) -> dict[str, Any]:
        return clean_body(
            {
                "id": self.media_id,
                "link": self.link,
                "caption": self.caption,
                "filename": self.filename,
            }
        )


class Contact(Payload):
    """One entry of a ``contacts[]`` payload."""

    def __init__(self, name: dict[str, Any] | None = None, **fields: Any) -> None:
        self.fields = fields
        if name:
            self.fields["name"] = name

    def to_dict(self) -> dict[str, Any]:
        return clean_body(self.fields)

    @staticmethod
    def name(
        formatted: str,
        *,
        first: str | None = None,
        last: str | None = None,
        middle: str | None = None,
        prefix: str | None = None,
        suffix: str | None = None,
    ) -> dict[str, Any]:
        return clean_body(
            {
                "formatted_name": formatted,
                "first_name": first,
                "last_name": last,
                "middle_name": middle,
                "prefix": prefix,
                "suffix": suffix,
            }
        )

    @staticmethod
    def phone(number: str, *, wa_id: str | None = None, type: str | None = None) -> dict[str, Any]:
        return clean_body({"phone": number, "wa_id": wa_id, "type": type})


# --- interactive -----------------------------------------------------------


class Interactive(Payload):
    """Base for ``type: interactive`` payloads."""

    def __init__(self, type: str) -> None:
        self.type = type
        self._header: dict[str, Any] | None = None
        self._body: str | None = None
        self._footer: str | None = None
        self._action: dict[str, Any] = {}

    def header_text(self, text: str, *, sub_text: str | None = None) -> Interactive:
        self._header = clean_body({"type": "text", "text": text, "sub_text": sub_text})
        return self

    def header_media(
        self, kind: str, *, media_id: str | None = None, link: str | None = None
    ) -> Interactive:
        if kind not in ("image", "video", "document"):
            raise ValueError("header media kind must be image, video, or document")
        self._header = {"type": kind, kind: Media(media_id=media_id, link=link).to_dict()}
        return self

    def body(self, text: str) -> Interactive:
        self._body = text
        return self

    def footer(self, text: str) -> Interactive:
        self._footer = text
        return self

    def to_dict(self) -> dict[str, Any]:
        return clean_body(
            {
                "type": self.type,
                "header": self._header,
                "body": {"text": self._body} if self._body else None,
                "footer": {"text": self._footer} if self._footer else None,
                "action": self._action or None,
            }
        )


class Button:
    """One reply button for :class:`Buttons` (max 3)."""

    def __init__(self, title: str, id: str) -> None:
        if len(title) > 20:
            raise ValueError("button title must be ≤ 20 characters")
        self.title = title
        self.id = id


class Buttons(Interactive):
    """``interactive.type = 'button'`` — up to 3 reply buttons."""

    def __init__(self) -> None:
        super().__init__("button")
        self._buttons: list[Button] = []

    def add(self, title: str, id: str) -> Buttons:
        if len(self._buttons) >= 3:
            raise ValueError("reply buttons support at most 3 buttons")
        self._buttons.append(Button(title, id))
        return self

    def to_dict(self) -> dict[str, Any]:
        self._action = {
            "buttons": [
                {"type": "reply", "reply": {"id": b.id, "title": b.title}} for b in self._buttons
            ]
        }
        return super().to_dict()


class Row:
    """One row in a :class:`Section` of a list message."""

    def __init__(self, title: str, id: str, *, description: str | None = None) -> None:
        if len(title) > 24:
            raise ValueError("row title must be ≤ 24 characters")
        self.data = clean_body({"id": id, "title": title, "description": description})


class Section:
    """A section of rows (list) or products (product_list)."""

    def __init__(self, title: str | None = None) -> None:
        if title is not None and len(title) > 24:
            raise ValueError("section title must be ≤ 24 characters")
        self.title = title
        self.rows: list[dict[str, Any]] = []
        self.product_items: list[dict[str, Any]] = []

    def row(self, title: str, id: str, *, description: str | None = None) -> Section:
        if len(self.rows) >= 10:
            raise ValueError("a section supports at most 10 rows")
        self.rows.append(Row(title, id, description=description).data)
        return self

    def product(self, retailer_id: str) -> Section:
        self.product_items.append({"product_retailer_id": retailer_id})
        return self

    def to_dict(self) -> dict[str, Any]:
        return clean_body(
            {
                "title": self.title,
                "rows": self.rows or None,
                "product_items": self.product_items or None,
            }
        )


class ListMessage(Interactive):
    """``interactive.type = 'list'`` — a menu of up to 10 sections."""

    def __init__(self, button_text: str) -> None:
        super().__init__("list")
        self._button_text = button_text
        self._sections: list[Section] = []

    def section(self, title: str | None = None) -> Section:
        if len(self._sections) >= 10:
            raise ValueError("list messages support at most 10 sections")
        sec = Section(title)
        self._sections.append(sec)
        return sec

    def to_dict(self) -> dict[str, Any]:
        if not self._sections:
            raise ValueError("a list message needs at least one section")
        self._action = {
            "button": self._button_text,
            "sections": [s.to_dict() for s in self._sections],
        }
        return super().to_dict()


class CtaUrl(Interactive):
    """``interactive.type = 'cta_url'`` — single call-to-action URL button."""

    def __init__(self, display_text: str, url: str) -> None:
        super().__init__("cta_url")
        self._display_text = display_text
        self._url = url

    def to_dict(self) -> dict[str, Any]:
        self._action = {
            "name": "cta_url",
            "parameters": {"display_text": self._display_text, "url": self._url},
        }
        return super().to_dict()


class FlowAction:
    """``flow.parameters.flow_action_payload`` for flow messages."""

    @staticmethod
    def navigate(screen: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"screen": screen, "data": data or {}}


class FlowMessage(Interactive):
    """``interactive.type = 'flow'`` — launch a WhatsApp Flow."""

    def __init__(
        self,
        cta: str,
        *,
        flow_id: str | None = None,
        flow_name: str | None = None,
        flow_token: str | None = None,
        draft: bool = False,
        data_exchange: bool = False,
        screen: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__("flow")
        if not flow_id and not flow_name:
            raise ValueError("FlowMessage requires flow_id or flow_name")
        self._cta = cta
        self._flow_id = flow_id
        self._flow_name = flow_name
        self._flow_token = flow_token
        self._draft = draft
        self._exchange = data_exchange
        self._screen = screen
        self._data = data

    def to_dict(self) -> dict[str, Any]:
        params = clean_body(
            {
                "flow_id": self._flow_id,
                "flow_name": self._flow_name,
                "flow_token": self._flow_token,
                "flow_cta": self._cta,
                "flow_action": "data_exchange" if self._exchange else "navigate",
                "mode": "draft" if self._draft else None,
            }
        )
        if self._screen:
            params["flow_action_payload"] = FlowAction.navigate(self._screen, self._data)
        self._action = {"name": "flow", "parameters": params}
        return super().to_dict()


class Product(Interactive):
    """``interactive.type = 'product'`` — single product message (SPM).

    Note: ``header`` is not allowed on product messages.
    """

    def __init__(self, catalog_id: str, product_retailer_id: str) -> None:
        super().__init__("product")
        self._catalog_id = catalog_id
        self._rid = product_retailer_id

    def to_dict(self) -> dict[str, Any]:
        self._action = {
            "catalog_id": self._catalog_id,
            "product_retailer_id": self._rid,
        }
        return super().to_dict()


class ProductSection:
    def __init__(self, title: str | None = None) -> None:
        self._sec = Section(title)

    def add(self, retailer_id: str) -> ProductSection:
        self._sec.product(retailer_id)
        return self

    def to_dict(self) -> dict[str, Any]:
        return self._sec.to_dict()


class ProductList(Interactive):
    """``interactive.type = 'product_list'`` — multi-product message (MPM)."""

    def __init__(self, catalog_id: str, *, header_text: str) -> None:
        super().__init__("product_list")
        self._catalog_id = catalog_id
        self.header_text(header_text)
        self._sections: list[ProductSection] = []

    def section(self, title: str | None = None) -> ProductSection:
        sec = ProductSection(title)
        self._sections.append(sec)
        return sec

    def to_dict(self) -> dict[str, Any]:
        if not self._sections:
            raise ValueError("a product list needs at least one section")
        self._action = {
            "catalog_id": self._catalog_id,
            "sections": [s.to_dict() for s in self._sections],
        }
        return super().to_dict()


class CatalogMessage(Interactive):
    """``interactive.type = 'catalog_message'`` — open the full catalog."""

    def __init__(self, *, thumbnail_product_retailer_id: str | None = None) -> None:
        super().__init__("catalog_message")
        self._thumb = thumbnail_product_retailer_id

    def to_dict(self) -> dict[str, Any]:
        params = clean_body({"thumbnail_product_retailer_id": self._thumb})
        self._action = {"name": "catalog_message", "parameters": params}
        return super().to_dict()


class LocationRequest(Interactive):
    """``interactive.type = 'location_request_message'`` — ask for a location."""

    def __init__(self) -> None:
        super().__init__("location_request_message")

    def to_dict(self) -> dict[str, Any]:
        self._action = {"name": "send_location"}
        return super().to_dict()


class CallPermissionRequest(Interactive):
    """``interactive.type = 'call_permission_request'``."""

    def __init__(self) -> None:
        super().__init__("call_permission_request")

    def to_dict(self) -> dict[str, Any]:
        self._action = {"name": "call_permission_request"}
        return super().to_dict()


# --- template send ---------------------------------------------------------


class Param:
    """A template component ``parameters[]`` entry."""

    @staticmethod
    def text(value: str, *, parameter_name: str | None = None) -> dict[str, Any]:
        return clean_body({"type": "text", "text": value, "parameter_name": parameter_name})

    @staticmethod
    def currency(code: str, amount_1000: float | int) -> dict[str, Any]:
        return {
            "type": "currency",
            "currency": {
                "fallback_value": f"{code} {amount_1000 / 1000:.2f}",
                "code": code,
                "amount_1000": int(amount_1000),
            },
        }

    @staticmethod
    def date_time(fallback: str, *, timestamp: int | None = None) -> dict[str, Any]:
        dt: dict[str, Any] = {"fallback_value": fallback}
        if timestamp is not None:
            dt["timestamp"] = timestamp
        return {"type": "date_time", "date_time": dt}

    @staticmethod
    def image(*, media_id: str | None = None, link: str | None = None) -> dict[str, Any]:
        return {"type": "image", "image": Media(media_id=media_id, link=link).to_dict()}

    @staticmethod
    def document(
        *, media_id: str | None = None, link: str | None = None, filename: str | None = None
    ) -> dict[str, Any]:
        return {
            "type": "document",
            "document": Media(media_id=media_id, link=link, filename=filename).to_dict(),
        }

    @staticmethod
    def video(*, media_id: str | None = None, link: str | None = None) -> dict[str, Any]:
        return {"type": "video", "video": Media(media_id=media_id, link=link).to_dict()}

    @staticmethod
    def payload(value: str) -> dict[str, Any]:
        """Quick-reply/URL button parameter."""
        return {"type": "payload", "payload": value}

    @staticmethod
    def text_button(value: str) -> dict[str, Any]:
        return {"type": "text", "text": value}

    @staticmethod
    def coupon(code: str) -> dict[str, Any]:
        return {"type": "coupon_code", "coupon_code": code}

    @staticmethod
    def limited_time_offer(expiration_time_ms: int) -> dict[str, Any]:
        return {
            "type": "limited_time_offer",
            "limited_time_offer": {"expiration_time_ms": expiration_time_ms},
        }

    @staticmethod
    def location(
        latitude: float, longitude: float, *, name: str | None = None, address: str | None = None
    ) -> dict[str, Any]:
        return {
            "type": "location",
            "location": clean_body(
                {"latitude": latitude, "longitude": longitude, "name": name, "address": address}
            ),
        }

    @staticmethod
    def action(**fields: Any) -> dict[str, Any]:
        """Button action parameters (e.g. flow_token for FLOW buttons)."""
        return {"type": "action", "action": clean_body(fields)}


class Template(Payload):
    """``type: template`` send payload.

    ::

        Template("hello_world", "en_US")
        Template("order", "en_US").body_params("Ana", "1234")
        Template("otp", "en_US").button_params("url", Param.text("xyz"))
    """

    def __init__(
        self,
        name: str,
        language: str,
        *,
        components: list[dict[str, Any]] | None = None,
    ) -> None:
        self.name = name
        self.language = language
        self._components: list[dict[str, Any]] = list(components or [])

    def header_params(self, *params: dict[str, Any]) -> Template:
        self._components.append({"type": "header", "parameters": list(params)})
        return self

    def body_params(self, *values: Any, **named: str) -> Template:
        """Positional values → ``{{1}}``, ``{{2}}``; named kwargs → ``{{name}}``."""
        params: list[dict[str, Any]] = [
            p if isinstance(p, dict) else Param.text(str(p)) for p in values
        ]
        params.extend(Param.text(str(v), parameter_name=k) for k, v in named.items())
        self._components.append({"type": "body", "parameters": params})
        return self

    def button_params(self, sub_type: str, index: int, *params: dict[str, Any]) -> Template:
        """``sub_type``: 'quick_reply' | 'url' | 'flow' | 'copy_code' etc."""
        self._components.append(
            {
                "type": "button",
                "sub_type": sub_type,
                "index": str(index),
                "parameters": list(params),
            }
        )
        return self

    def component(self, type_: str, parameters: list[dict[str, Any]], **extra: Any) -> Template:
        self._components.append(clean_body({"type": type_, "parameters": parameters, **extra}))
        return self

    def carousel(self, cards: list[dict[str, Any]]) -> Template:
        self._components.append({"type": "carousel", "cards": cards})
        return self

    def to_dict(self) -> dict[str, Any]:
        return clean_body(
            {
                "name": self.name,
                "language": {"code": self.language},
                "components": self._components or None,
            }
        )
