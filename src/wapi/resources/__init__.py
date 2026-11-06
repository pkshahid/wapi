"""API resource classes — one per endpoint group."""

from .calls import AsyncCalls, Calls
from .flows import AsyncFlows, Flows
from .groups import AsyncGroups, Groups
from .marketing import AsyncMarketing, Marketing
from .media import AsyncMedia, Media
from .messages import AsyncMessages, Messages
from .phone_numbers import AsyncPhoneNumbers, PhoneNumbers
from .profile import (
    AsyncAutomation,
    AsyncBlockedUsers,
    AsyncCommerce,
    AsyncCompliance,
    AsyncEncryption,
    AsyncProfile,
    AsyncQRCodes,
    Automation,
    BlockedUsers,
    Commerce,
    Compliance,
    Encryption,
    Profile,
    QRCodes,
)
from .templates import AsyncTemplates, Templates
from .waba import AsyncWabaResource, WabaResource

__all__ = [
    "AsyncAutomation",
    "AsyncBlockedUsers",
    "AsyncCalls",
    "AsyncCommerce",
    "AsyncCompliance",
    "AsyncEncryption",
    "AsyncFlows",
    "AsyncGroups",
    "AsyncMarketing",
    "AsyncMedia",
    "AsyncMessages",
    "AsyncPhoneNumbers",
    "AsyncProfile",
    "AsyncQRCodes",
    "AsyncTemplates",
    "AsyncWabaResource",
    "Automation",
    "BlockedUsers",
    "Calls",
    "Commerce",
    "Compliance",
    "Encryption",
    "Flows",
    "Groups",
    "Marketing",
    "Media",
    "Messages",
    "PhoneNumbers",
    "Profile",
    "QRCodes",
    "Templates",
    "WabaResource",
]
