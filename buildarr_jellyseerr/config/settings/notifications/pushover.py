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
Jellyseerr plugin Pushover notifications settings configuration.
"""


from __future__ import annotations

from typing import List, Optional, Set

from buildarr.config import RemoteMapEntry
from pydantic import SecretStr

from .notification_types import NotificationTypesSettingsBase


class PushoverApiKey(SecretStr):
    to_lower = True
    min_length = 30
    max_length = 30
    regex = r"^[A-Za-z0-9]{30}$"


class PushoverSettings(NotificationTypesSettingsBase):
    """
    Send notifications to one or more devices via Pushover.
    """

    api_key: Optional[PushoverApiKey] = None
    """
    API key registered for Jellyseerr in Pushover.

    **Required if Pushover notifications are enabled.**
    """

    user_key: Optional[PushoverApiKey] = None
    """
    User key to authenticate with on Pushover.

    **Required if Pushover notifications are enabled.**
    """

    _type: str = "pushover"
    _required_if_enabled: Set[str] = {"api_key", "user_key"}

    @classmethod
    def _get_remote_map(cls) -> List[RemoteMapEntry]:
        return [
            (
                "api_key",
                "accessToken",
                {
                    "decoder": lambda v: v or None,
                    "encoder": lambda v: v.get_secret_value() if v else "",
                },
            ),
            (
                "user_key",
                "userToken",
                {
                    "decoder": lambda v: v or None,
                    "encoder": lambda v: v.get_secret_value() if v else "",
                },
            ),
        ]
