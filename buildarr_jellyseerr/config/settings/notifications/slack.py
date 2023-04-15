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
Jellyseerr plugin Slack notifications settings configuration.
"""


from __future__ import annotations

from typing import List, Optional, Set

from buildarr.config import RemoteMapEntry
from pydantic import AnyHttpUrl

from .notification_types import NotificationTypesSettingsBase


class SlackSettings(NotificationTypesSettingsBase):
    """
    Send notifications to a Slack channel.
    """

    webhook_url: Optional[AnyHttpUrl] = None
    """
    Slack server webhook URL.
    """

    _type: str = "slack"
    _required_if_enabled: Set[str] = {"webhook_url"}

    @classmethod
    def _get_remote_map(cls) -> List[RemoteMapEntry]:
        return [
            (
                "webhook_url",
                "webhookUrl",
                {"decoder": lambda v: v or None, "encoder": lambda v: str(v) if v else ""},
            ),
        ]
