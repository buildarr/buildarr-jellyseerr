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
Jellyseerr plugin type hints.
"""


from __future__ import annotations

from typing import Literal

from pydantic import SecretStr

JellyseerrProtocol = Literal["http", "https"]


class JellyseerrApiKey(SecretStr):
    """
    Constrained secret string type for a Jellyseerr API key.
    """

    regex = "^[A-Za-z0-9]+=$"


class ArrApiKey(SecretStr):
    """
    Constrained secret string type for an Arr stack application API key.
    """

    min_length = 32
    max_length = 32
