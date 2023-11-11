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

from http import HTTPStatus
from typing import List, Optional, Set

from buildarr.config import RemoteMapEntry
from buildarr.types import LowerCaseNonEmptyStr, LowerCaseStr, NonEmptyStr, UpperCaseStr
from pydantic import AnyHttpUrl
from typing_extensions import Self

from ...api import api_get, api_post
from ...secrets import JellyseerrSecrets
from ..types import JellyseerrConfigBase


class JellyseerrGeneralSettings(JellyseerrConfigBase):
    """
    These settings adjust the general behaviour for how Jellyseerr
    is accessed, and discovers content.

    ```yaml
    jellyseerr:
      settings:
        general:
          application_title: "Jellyseerr"
          application_url: null
          enable_proxy_support: false
          enable_csrf_protection: false
          enable_image_caching: false
          display_language: "en"
          discover_region: null
          discover_languages: []
          hide_available_media: false
          allow_partial_series_requests: true
    ```
    """

    application_title: NonEmptyStr = "Jellyseerr"  # type: ignore[assignment]
    """
    Name of the Jellyseerr instance, as shown in the browser title.
    """

    application_url: Optional[AnyHttpUrl] = None
    """
    Application URL to use when generating links to Jellyseerr.

    If set to `null`, use the URL the browser is currently using to access Jellyseerr.
    """

    enable_proxy_support: bool = False
    """
    Allow Jellyseerr to correctly register client IP addresses behind a proxy.

    When this attribute is changed, a restart of Jellyseerr is required.
    """

    enable_csrf_protection: bool = False
    """
    Set external API access to read-only (requires HTTPS).

    When this attribute is changed, a restart of Jellyseerr is required.
    """

    enable_image_caching: bool = False
    """
    Cache externally sourced images.

    Take care when enabling this option, as this requires a significant amount of disk space.
    """

    display_language: LowerCaseNonEmptyStr = "en"  # type: ignore[assignment]
    """
    The display language of the Jellyseerr UI.

    Use the [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
    two-character language code when defining this attribute.
    """

    discover_region: Optional[UpperCaseStr] = None
    """
    Filter content by regional availability.

    If set to `null`, discovers content for all regions.

    Use the [ISO 3166-1](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)
    two-character country code when defining this attribute.
    """

    discover_languages: Set[LowerCaseStr] = set()
    """
    Filter content by original language.

    If empty, discovers all languages.

    Use [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
    two-character language codes when defining this attribute.
    """

    hide_available_media: bool = False
    """
    Hide content that is already available in the media library in the UI.
    """

    allow_partial_series_requests: bool = True
    """
    Allow making media requests for only part of a series.
    """

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
            "display_language",
            "locale",
            {"decoder": lambda v: v or "en"},  # Sometimes can be an empty string.
        ),
        (
            "discover_languages",
            "originalLanguage",
            {
                "decoder": lambda v: set(ln.strip() for ln in v.split("|")) if v else set(),
                "encoder": lambda v: "|".join(sorted(v)) if v else "",
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
            set_unchanged=True,
        )
        if changed:
            api_post(
                secrets,
                "/api/v1/settings/main",
                remote_attrs,
                expected_status_code=HTTPStatus.OK,
            )
            return True
        return False
