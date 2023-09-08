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
from typing import TYPE_CHECKING, cast
from urllib.parse import urlparse

from buildarr.secrets import SecretsPlugin
from buildarr.types import NonEmptyStr, Port

from .api import api_get
from .exceptions import JellyseerrAPIError
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
    api_key: JellyseerrApiKey

    @property
    def host_url(self) -> str:
        return f"{self.protocol}://{self.hostname}:{self.port}"

    @classmethod
    def from_url(cls, base_url: str, api_key: str) -> Self:
        url_obj = urlparse(base_url)
        hostname_port = url_obj.netloc.rsplit(":", 1)
        hostname = hostname_port[0]
        protocol = url_obj.scheme
        port = (
            int(hostname_port[1])
            if len(hostname_port) > 1
            else (443 if protocol == "https" else 80)
        )
        return cls(
            **{  # type: ignore[arg-type]
                "hostname": hostname,
                "port": port,
                "protocol": protocol,
                "api_key": api_key,
            },
        )

    @classmethod
    def get(cls, config: JellyseerrConfig) -> Self:
        return cls(
            hostname=config.hostname,
            port=config.port,
            protocol=config.protocol,
            api_key=cast(JellyseerrApiKey, config.api_key),
        )

    def test(self) -> bool:
        try:
            api_get(self, "/api/v1/settings/main")
            return True
        except JellyseerrAPIError as err:
            if err.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
                return False
            else:
                raise
