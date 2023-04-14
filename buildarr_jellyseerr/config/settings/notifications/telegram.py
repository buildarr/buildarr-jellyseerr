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
    Jellyseerr Telegram notifications settings.
    """

    access_token: Optional[SecretStr] = None

    username: Optional[str] = None

    chat_id: Optional[str] = None

    send_silently: bool = False

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
