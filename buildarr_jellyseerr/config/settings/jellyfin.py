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

from http import HTTPStatus
from logging import getLogger
from typing import Any, Dict, List, Optional, Set, Union, cast

import requests

from buildarr.config import RemoteMapEntry
from buildarr.types import NonEmptyStr
from pydantic import AnyHttpUrl, EmailStr, SecretStr
from typing_extensions import Self

from ...api import api_get, api_post
from ...exceptions import JellyseerrAPIError
from ...secrets import JellyseerrSecrets
from ..types import JellyseerrConfigBase

logger = getLogger(__name__)


class JellyseerrJellyfinSettings(JellyseerrConfigBase):
    server_url: Optional[str] = None
    """
    Server URL that Jellyseerr will use to communicate with Jellyfin.
    """

    username: Optional[str] = None
    """
    Username of the Jellyfin administrator user that Jellyseerr will use.
    """

    password: Optional[SecretStr] = None
    """
    Jellyfin administrator user password.
    """

    email_address: Optional[EmailStr] = None
    """
    Email address associated with the Jellyfin administrator user.
    """

    external_url: Optional[AnyHttpUrl] = None
    """
    The externally-accessible URL for the Jellyfin server.

    This is used to create usable URLs to Jellyfin libraries in the Jellyseerr UI.
    """

    libraries: Set[NonEmptyStr] = set()
    """
    The Jellyfin libraries that Jellyseerr will use to scan for available titles.
    """

    def _is_initialized(self, host_url: str) -> bool:
        return api_get(host_url, "/api/v1/settings/public")["initialized"]

    def _initialize(self, tree: str, host_url: str) -> None:
        # Check if we have all the information we need to initialise it.
        logger.info("Checking if required attributes are defined")
        missing_attrs: List[str] = []
        for attr_name in ("server_url", "username", "password", "email_address", "libraries"):
            attr_value: Optional[Union[str, SecretStr, Set[str]]] = getattr(self, attr_name)
            if isinstance(attr_value, SecretStr):
                attr_value = attr_value.get_secret_value()
            if not attr_value or (isinstance(attr_value, str) and not attr_value.strip()):
                logger.debug("  - %s.%s: NOT DEFINED", tree, attr_name)
                missing_attrs.append(attr_name)
            else:
                logger.debug("  - %s.%s: defined", tree, attr_name)
        if missing_attrs:
            raise ValueError(
                "Unable to initialise Jellyseerr instance, required attributes are missing. "
                "Either manually initialise Jellyseerr yourself, "
                "or set the following attributes so Buildarr can automatically initialise it: "
                f"{', '.join(repr(f'{tree}.{an}') for an in missing_attrs)}. ",
            )
        logger.info("Finished checking if required attributes are defined")
        # Start a session, to store the cookie used during initialisation.
        with requests.Session() as session:
            # Configure the Jellyfin instance on Jellyseerr.
            logger.info("Authenticating Jellyseerr with Jellyfin")
            try:
                api_post(
                    host_url,
                    "/api/v1/auth/jellyfin",
                    {
                        "username": self.username,
                        "password": cast(SecretStr, self.password).get_secret_value(),
                        "hostname": self.server_url,
                        "email": self.email_address,
                    },
                    session=session,
                    expected_status_code=HTTPStatus.OK,
                )
            except JellyseerrAPIError as err:
                error_message = str(err)
                if err.status_code == HTTPStatus.INTERNAL_SERVER_ERROR and all(
                    word in error_message for word in ("Jellyfin", "configured")
                ):
                    raise RuntimeError(
                        "Jellyseerr already has been configured with a Jellyfin instance "
                        "but session data has been lost, please recreate Jellyseerr and "
                        "re-initialise it",
                    ) from None
                else:
                    raise
            logger.info("Finished authenticating Jellyseerr with Jellyfin")
            # Ensure the Jellyfin libraries are synced, and fetch the library metadata.
            logger.info("Syncing Jellyfin libraries to Jellyseerr")
            api_libraries = api_get(
                host_url,
                "/api/v1/settings/jellyfin/library?sync=true",
                session=session,
            )
            logger.info("Finished syncing Jellyfin libraries to Jellyseerr")
            # Enable the selected libraries in the configuration.
            logger.info(
                "Enabling Jellyfin libraries in Jellyseerr: %s",
                ", ".join(repr(library_name) for library_name in self.libraries),
            )
            library_ids: Dict[str, str] = {li["name"]: li["id"] for li in api_libraries}
            enabled_library_ids: List[str] = []
            for library_name in self.libraries:
                if library_name in library_ids:
                    enabled_library_ids.append(library_ids[library_name])
                else:
                    raise ValueError(
                        f"Enabled library '{library_name}' not found in Jellyfin "
                        "(available libraries: "
                        f"{', '.join(repr(ln) for ln in library_ids.keys())}"
                        ")",
                    )
            api_get(
                host_url,
                f"/api/v1/settings/jellyfin/library?enable={','.join(enabled_library_ids)}",
                session=session,
            )
            logger.info("Finished enabling Jellyfin libraries in Jellyseerr")
            # Finalise the initialisation of the Jellyseerr instance.
            logger.info("Finalising initialisation")
            api_post(
                host_url,
                "/api/v1/settings/initialize",
                session=session,
                expected_status_code=HTTPStatus.OK,
            )
            logger.info("Finished finalising initialisation")

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
            # /api/v1/settings/jellyfin/libraries is not used here because
            # despite it being a GET endpoint, it is actually meant to be used
            # only to enable or disable libraries.
            self._get_remote_map(api_get(secrets, "/api/v1/settings/jellyfin")["libraries"]),
            check_unmanaged=check_unmanaged,
            set_unchanged=True,
        )
        if changed:
            api_get(
                secrets,
                f"/api/v1/settings/jellyfin/library?enable={','.join(remote_attrs['libraries'])}",
            )
            del remote_attrs["libraries"]
            api_post(
                secrets,
                "/api/v1/settings/jellyfin",
                remote_attrs,
                expected_status_code=HTTPStatus.OK,
            )
            return True
        return False
