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
Jellyseerr notifiations with adjustable types settings configuration base class.
"""


from __future__ import annotations

import functools
import operator

from typing import List, Set

from buildarr.config import RemoteMapEntry
from buildarr.types import BaseEnum

from .base import NotificationsSettingsBase


class NotificationType(BaseEnum):
    # none = 0
    media_pending = 2
    media_approved = 4
    media_available = 8
    media_failed = 16
    test_notification = 32
    media_declined = 64
    media_auto_approved = 128
    issue_created = 256
    issue_comment = 512
    issue_resolved = 1024
    issue_reopened = 2048
    media_auto_requested = 4096


class NotificationTypesSettingsBase(NotificationsSettingsBase):
    # Base class for notification services with configurable notification types.

    notification_types: Set[NotificationType] = set()
    """
    The notification types to send to the service.

    By default no notifications are sent, even if enabled, so remember to set
    the types of events you'd like to get notified for.

    Values:

    * `media-pending`
    * `media-approved`
    * `media-available`
    * `media-failed`
    * `test-notification`
    * `media-declined`
    * `media-auto-approved`
    * `issue-created`
    * `issue-comment`
    * `issue-resolved`
    * `issue-reopened`
    * `media-auto-requested`
    """

    @classmethod
    def _get_base_remote_map(cls) -> List[RemoteMapEntry]:
        return [
            *super()._get_base_remote_map(),
            (
                "notification_types",
                "types",
                {
                    "decoder": lambda v: (
                        set(
                            notification_type
                            for notification_type in NotificationType
                            if v & notification_type.value
                        )
                        if v
                        else set()
                    ),
                    "encoder": lambda v: functools.reduce(
                        operator.ior,
                        (notification_type.value for notification_type in v),
                        0,
                    ),
                },
            ),
        ]
