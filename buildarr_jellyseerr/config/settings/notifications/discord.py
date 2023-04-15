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
Jellyseerr plugin Discord notifications settings configuration.
"""


from __future__ import annotations

from typing import List, Optional, Set

from buildarr.config import RemoteMapEntry
from pydantic import AnyHttpUrl

from .notification_types import NotificationTypesSettingsBase


class DiscordSettings(NotificationTypesSettingsBase):
    """
    Send notifications to a Discord server using a webhook URL.
    """

    webhook_url: Optional[AnyHttpUrl] = None
    """
    Discord server webhook URL.

    **Required if Discord notifications are enabled.**
    """

    username: Optional[str] = None
    """
    The username to post as.

    If unset, blank or set to `None`, use the default username set to the webhook URL.
    """

    avatar_url: Optional[AnyHttpUrl] = None
    """
    A URL to an custom avatar to use when posting.

    If unset, blank or set to `None`, use the default avatar for the user.
    """

    enable_mentions: bool = True
    """
    Allow the user to mention when posting.
    """

    _type: str = "discord"
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
                "username",
                "botUsername",
                {"optional": True, "decoder": lambda v: v or None, "encoder": lambda v: v or ""},
            ),
            (
                "avatar_url",
                "botAvatarUrl",
                {
                    "optional": True,
                    "decoder": lambda v: v or None,
                    "encoder": lambda v: str(v) if v else "",
                },
            ),
            ("enable_mentions", "enableMentions", {"optional": True}),
        ]
