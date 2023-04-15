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
Jellyseerr plugin Pushbullet notifications settings configuration.
"""


from __future__ import annotations

from typing import List, Optional, Set

from buildarr.config import RemoteMapEntry
from pydantic import SecretStr

from .notification_types import NotificationTypesSettingsBase


class PushbulletSettings(NotificationTypesSettingsBase):
    """
    Send notifications to one or more devices via Pushbullet.
    """

    access_token: Optional[SecretStr] = None
    """
    The generated application token for Jellyseerr in Pushbullet.

    **Required if Pushbullet notifications are enabled.**
    """

    channel_tag: Optional[str] = None
    """
    Optional [channel tag](https://pushbullet.com/my-channel) for pushing notifications
    to any devices subscribed to it.
    """

    _type: str = "pushbullet"
    _required_if_enabled: Set[str] = {"access_token"}

    @classmethod
    def _get_remote_map(cls) -> List[RemoteMapEntry]:
        return [
            (
                "access_token",
                "accessToken",
                {
                    "decoder": lambda v: v or None,
                    "encoder": lambda v: v.get_secret_value() if v else "",
                },
            ),
            (
                "channel_tag",
                "channelTag",
                {"optional": True, "decoder": lambda v: v or None, "encoder": lambda v: v or ""},
            ),
        ]
