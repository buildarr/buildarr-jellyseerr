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
Jellyseerr plugin Jellyfin settings configuration.
"""


from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from buildarr.config import RemoteMapEntry
from buildarr.types import NonEmptyStr
from pydantic import AnyHttpUrl, Field
from typing_extensions import Self

from ...api import api_get, api_post
from ...secrets import JellyseerrSecrets
from ..types import JellyseerrConfigBase


class JellyseerrJellyfinSettings(JellyseerrConfigBase):
    """
    Jellyseerr Jellyfin settings.
    """

    external_url: Optional[AnyHttpUrl] = Field(None, alias="external_hostname")

    libraries: Set[NonEmptyStr] = set()

    # These need to be changed in the Jellyseerr configuration file (`settings.json`).
    # base_url: AnyHttpUrl = Field("http://my.jellyfin.host", alias="hostname")
    # admin_username: NonEmptyStr = Field("admin", alias="admin_user")
    # admin_password: SecretStr = Field("password", min_length=1, alias="admin_pass")

    @classmethod
    def _get_remote_map(
        cls,
        libraries: Optional[List[Dict[str, Any]]] = None,
    ) -> List[RemoteMapEntry]:
        if not libraries:
            libraries = []
        return [
            (
                "external_url",
                "externalHostname",
                {"decoder": lambda v: v or None, "encoder": lambda v: str(v) or ""},
            ),
            (
                "libraries",
                "libraries",
                {
                    "decoder": lambda v: set(li["name"] for li in v if li["enabled"]),
                    # Encode the libraries set into a set of library IDs.
                    # This gets used in a separate request when updating the settings.
                    "encoder": lambda v: set(li["id"] for li in libraries if li["name"] in v),
                },
            ),
            # ("base_url", "hostname", {}),
            # ("admin_user", "adminUser", {}),
            # ("admin_password", "adminPass", {}),
        ]

    @classmethod
    def from_remote(cls, secrets: JellyseerrSecrets) -> Self:
        return cls(
            **cls.get_local_attrs(
                cls._get_remote_map(),
                api_get(secrets, "/api/v1/settings/jellyfin"),
            ),
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
            self._get_remote_map(api_get(secrets, "/api/v1/settings/jellyfin")["libraries"]),
            check_unmanaged=check_unmanaged,
        )
        if "libraries" in remote_attrs:
            api_get(
                secrets,
                f"/api/v1/settings/jellyfin/library?enable={','.join(remote_attrs['libraries'])}",
            )
            del remote_attrs["libraries"]
        if changed:
            api_post(secrets, "/api/v1/settings/jellyfin", remote_attrs)
            return True
        return False
