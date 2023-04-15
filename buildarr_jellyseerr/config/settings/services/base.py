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
Jellyseerr plugin Arr service base configuration.
"""


from __future__ import annotations

import operator

from logging import getLogger
from typing import List, Optional

from buildarr.config import RemoteMapEntry
from buildarr.types import NonEmptyStr, Port
from pydantic import AnyHttpUrl

from ...types import JellyseerrConfigBase

logger = getLogger(__name__)


class ArrBase(JellyseerrConfigBase):
    # Base class for an Arr application link in Jellyseerr.

    is_default_server: bool = False
    """
    Set this server as a default server for this application type.

    Up to two default servers can be set at a time: one for non-4K content, one for 4K content.
    """

    is_4k_server: bool = False
    """
    Use this server for managing 4K content.
    """

    hostname: NonEmptyStr
    """
    The hostname that Jellyseerr will use to connect to the server.
    """

    port: Port  # Default is set in individual classes.
    """
    The communication port that the server listens on.
    """

    use_ssl: bool = False
    """
    Connect to the server using HTTPS.
    """

    url_base: Optional[str] = None
    """
    The URL base configured on the server, if it has one configured.
    """

    external_url: Optional[AnyHttpUrl] = None
    """
    An optional external URL to the server, used to add clickable links
    to the servers on media detail pages.

    If not defined, uses the internal URL to the instance.
    """

    enable_scan: bool = False
    """
    Scan the server for existing media/request status.

    It is recommended that this setting is enabled, so that users cannot submit requests
    for media which has already been requested or is already available.
    """

    enable_automatic_search: bool = True
    """
    Automatically search for media upon approval of a request.
    """

    _base_remote_map: List[RemoteMapEntry] = [
        ("is_default_server", "isDefault", {}),
        ("is_4k_server", "is4k", {}),
        ("hostname", "hostname", {}),
        ("port", "port", {}),
        ("use_ssl", "useSsl", {}),
        (
            "url_base",
            "baseUrl",
            {"decoder": lambda v: v or None, "encoder": lambda v: v or ""},
        ),
        ("external_url", "externalUrl", {"optional": True, "set_if": lambda v: bool(v)}),
        ("enable_scan", "syncEnabled", {}),
        (
            "enable_automatic_search",
            "preventSearch",
            {"decoder": operator.not_, "encoder": operator.not_},
        ),
    ]

    class Config(JellyseerrConfigBase.Config):
        # Ensure in-place assignments of attributes are always validated,
        # since this class performs such modifications in certain cases.
        validate_assignment = True
