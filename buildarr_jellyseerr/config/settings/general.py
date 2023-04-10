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
Jellyseerr plugin general settings configuration.
"""


from __future__ import annotations

from typing import List, Optional, Set

from buildarr.config import RemoteMapEntry
from buildarr.types import NonEmptyStr
from pydantic import AnyHttpUrl, Field
from typing_extensions import Self

from ...api import api_get, api_post
from ...secrets import JellyseerrSecrets
from ...types import LowerCaseNonEmptyStr, LowerCaseStr, UpperCaseStr
from ..types import JellyseerrConfigBase


class JellyseerrGeneralSettings(JellyseerrConfigBase):
    """
    Jellyseerr general settings.
    """

    application_title: NonEmptyStr = "Jellyseerr"  # type: ignore[assignment]

    application_url: Optional[AnyHttpUrl] = None

    enable_proxy_support: bool = False
    """
    Restart required.
    """

    enable_csrf_protection: bool = False
    """
    Restart required.
    """

    enable_image_caching: bool = False

    display_language: LowerCaseNonEmptyStr = Field(  # type: ignore[assignment]
        "en",
        alias="locale",
    )
    """
    case-insensitive NonEmptyStr, get values from API schema. Two-character English code.
    """

    discover_region: Optional[UpperCaseStr] = Field(None, alias="region")
    """
    None is same as "All Regions". Get values from API schema
    Two-character country code
    """

    discover_languages: Set[LowerCaseStr] = Field(set(), alias="original_languages")
    """
    Empty is same as "All Languages". Two character lower-case language code.
    Set[case-insensitive NonEmptyStr], get values from API schema
    """

    hide_available_media: bool = False

    allow_partial_series_requests: bool = True

    _remote_map: List[RemoteMapEntry] = [
        ("application_title", "applicationTitle", {}),
        (
            "application_url",
            "applicationUrl",
            {"decoder": lambda v: v or None, "encoder": lambda v: v or ""},
        ),
        ("enable_proxy_support", "trustProxy", {}),
        ("enable_csrf_protection", "csrfProtection", {}),
        ("enable_image_caching", "cacheImages", {}),
        (
            "discover_languages",
            "locale",
            {
                "decoder": lambda v: set(ln.strip() for ln in v.split(",")) if v else set(),
                "encoder": lambda v: ",".join(sorted(v)) if v else "",
            },
        ),
        ("discover_region", "region", {}),
        ("hide_available_media", "hideAvailable", {}),
        ("allow_partial_series_requests", "partialRequestsEnabled", {}),
    ]

    @classmethod
    def from_remote(cls, secrets: JellyseerrSecrets) -> Self:
        return cls(
            **cls.get_local_attrs(cls._remote_map, api_get(secrets, "/api/v1/settings/main")),
        )

    def update_remote(
        self,
        tree: str,
        secrets: JellyseerrSecrets,
        remote: Self,
        check_unmanaged: bool = False,
    ) -> bool:
        changed, remote_attrs = self.get_update_remote_attrs(
            tree,
            remote,
            self._remote_map,
            check_unmanaged=check_unmanaged,
        )
        if changed:
            api_post(secrets, "/api/v1/settings/main", remote_attrs)
            return True
        return False
