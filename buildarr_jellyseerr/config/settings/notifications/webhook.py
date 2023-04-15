# Copyright (C) 2023 Callum Dickinson
#
# Buildarr is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# Buildarr is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Buildarr.
# If not, see <https://www.gnu.org/licenses/>.


"""
Jellyseerr plugin webhook notifications settings configuration.
"""


from __future__ import annotations

from typing import List, Optional, Set

from buildarr.config import RemoteMapEntry
from buildarr.types import NonEmptyStr
from pydantic import AnyHttpUrl, SecretStr

from .notification_types import NotificationTypesSettingsBase


class WebhookSettings(NotificationTypesSettingsBase):
    """
    Jellyseerr webhook notifications settings.
    """

    webhook_url: Optional[AnyHttpUrl] = None
    """
    Webhook endpoint URL.
    """

    authorization_header: Optional[SecretStr] = None

    payload_template: NonEmptyStr = "<JSON template>"  # type: ignore[assignment]

    _type: str = "webhook"
    _required_if_enabled: Set[str] = {"webhook_url"}

    @classmethod
    def _get_remote_map(cls) -> List[RemoteMapEntry]:
        return [
            (
                "webhook_url",
                "webhookUrl",
                {"decoder": lambda v: v or None, "encoder": lambda v: str(v) if v else ""},
            ),
            (
                "authorization_header",
                "authHeader",
                {
                    "optional": True,
                    "decoder": lambda v: v or None,
                    "encoder": lambda v: v.get_secret_value() if v else "",
                },
            ),
            ("payload_template", "jsonPayload", {}),
        ]
