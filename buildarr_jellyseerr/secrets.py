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
Jellyseerr plugin secrets file model.
"""


from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Dict, Optional, cast

from buildarr.secrets import SecretsPlugin
from buildarr.types import NonEmptyStr, Port
from pydantic import validator

from .api import api_get
from .exceptions import JellyseerrAPIError, JellyseerrSecretsUnauthorizedError
from .types import JellyseerrApiKey, JellyseerrProtocol

if TYPE_CHECKING:
    from typing_extensions import Self

    from .config import JellyseerrConfig

    class _JellyseerrSecrets(SecretsPlugin[JellyseerrConfig]):
        pass

else:

    class _JellyseerrSecrets(SecretsPlugin):
        pass


class JellyseerrSecrets(_JellyseerrSecrets):
    hostname: NonEmptyStr
    port: Port
    protocol: JellyseerrProtocol
    url_base: Optional[str]
    api_key: JellyseerrApiKey
    version: NonEmptyStr

    @property
    def host_url(self) -> str:
        return self._get_host_url(
            protocol=self.protocol,
            hostname=self.hostname,
            port=self.port,
            url_base=self.url_base,
        )

    @validator("url_base")
    def validate_url_base(cls, value: Optional[str]) -> Optional[str]:
        return f"/{value.strip('/')}" if value and value.strip("/") else None

    @classmethod
    def _get_host_url(
        cls,
        protocol: str,
        hostname: str,
        port: int,
        url_base: Optional[str],
    ) -> str:
        return f"{protocol}://{hostname}:{port}{url_base or ''}"

    @classmethod
    def get(cls, config: JellyseerrConfig) -> Self:
        return cls.get_from_url(
            hostname=config.hostname,
            port=config.port,
            protocol=config.protocol,
            url_base=config.url_base,
            api_key=config.api_key.get_secret_value() if config.api_key else None,
        )

    @classmethod
    def get_from_url(
        cls,
        hostname: str,
        port: int,
        protocol: str,
        url_base: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> Self:
        url_base = cls.validate_url_base(url_base)
        host_url = cls._get_host_url(
            protocol=protocol,
            hostname=hostname,
            port=port,
            url_base=url_base,
        )
        if not api_key:
            raise JellyseerrSecretsUnauthorizedError(
                (
                    "API key not found in the Buildarr configuration "
                    f"for the Jellyseerr instance at '{host_url}'. "
                    "Please check that the API key is set correctly, "
                    "and that it is set to the value as shown in "
                    "'Settings -> General -> API Key' on the Jellyseerr instance."
                ),
            )
        try:
            status = cast(Dict[str, Any], api_get(host_url, "/api/v1/status", api_key=api_key))
        except JellyseerrAPIError as err:
            if err.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
                raise JellyseerrSecretsUnauthorizedError(
                    (
                        f"Incorrect API key for the Jellyseerr instance at '{host_url}'. "
                        "Please check that the API key is set correctly in the Buildarr "
                        "configuration, and that it is set to the value as shown in "
                        "'Settings -> General -> API Key' on the Jellyseerr instance."
                    ),
                ) from None
            else:
                raise
        try:
            version = cast(NonEmptyStr, status["version"])
        except KeyError:
            raise JellyseerrSecretsUnauthorizedError(
                f"Unable to find Jellyseerr version in status metadata: {status}",
            ) from None
        except TypeError as err:
            raise JellyseerrSecretsUnauthorizedError(
                f"Unable to parse Jellyseerr status metadata: {err} (metadata object: {status})",
            ) from None
        return cls(
            hostname=cast(NonEmptyStr, hostname),
            port=cast(Port, port),
            protocol=cast(JellyseerrProtocol, protocol),
            url_base=url_base,
            api_key=cast(JellyseerrApiKey, api_key),
            version=version,
        )

    def test(self) -> bool:
        # We already perform API requests as part of instantiating the secrets object.
        # If the object exists, then the connection test is already successful.
        return True
