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
    """
    The following configuration attributes are available for an app sync profile.
    """

    is_default_server: bool = False

    is_4k_server: bool = False

    hostname: NonEmptyStr

    port: Port = 8989  # type: ignore[assignment]

    use_ssl: bool = False

    url_base: Optional[str] = None

    external_url: Optional[AnyHttpUrl] = None

    enable_scan: bool = False

    enable_automatic_search: bool = True

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
