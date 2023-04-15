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
Jellyseerr plugin Telegram notifications settings configuration.
"""


from __future__ import annotations

from typing import List, Optional, Set

from buildarr.config import RemoteMapEntry
from pydantic import SecretStr

from .notification_types import NotificationTypesSettingsBase


class TelegramSettings(NotificationTypesSettingsBase):
    """
    Send notifications to a group chat in Telegram.

    If `username` is set, also allows Jellyseerr users to setup their own chats
    with the Jellyseerr Telegram bot to receive notifications.
    """

    access_token: Optional[SecretStr] = None
    """
    Access token provided for the Telegram bot by BotFather at the end of the creation process.

    **Required if Telegram notifications are enabled.**
    """

    username: Optional[str] = None
    """
    The username of the Telegram bot.

    If this value is configured, Jellyseerr users will be able to click a link to start a chat
    with your bot and configure their own personal notifications.
    """

    chat_id: Optional[str] = None
    """
    Chat ID of the group chat to send messages to.

    **Required if Telegram notifications are enabled.**
    """

    send_silently: bool = False
    """
    When set to `true`, sends messages without notification sounds.
    """

    _type: str = "telegram"
    _required_if_enabled: Set[str] = {"access_token", "chat_id"}

    @classmethod
    def _get_remote_map(cls) -> List[RemoteMapEntry]:
        return [
            (
                "access_token",
                "botAPI",
                {
                    "decoder": lambda v: v or None,
                    "encoder": lambda v: v.get_secret_value() if v else "",
                },
            ),
            (
                "username",
                "botUsername",
                {"optional": True, "decoder": lambda v: v or None, "encoder": lambda v: v or ""},
            ),
            (
                "chat_id",
                "chatId",
                {"decoder": lambda v: v or None, "encoder": lambda v: v or ""},
            ),
            ("send_silently", "sendSilently", {}),
        ]
