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
Jellyseerr plugin configuration.
"""


from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from buildarr.config import ConfigPlugin
from buildarr.types import NonEmptyStr, Port
from typing_extensions import Self

from ..api import api_get
from ..types import JellyseerrApiKey, JellyseerrProtocol
from .settings import JellyseerrSettings

if TYPE_CHECKING:
    from ..secrets import JellyseerrSecrets

    class _JellyseerrInstanceConfig(ConfigPlugin[JellyseerrSecrets]):
        pass

else:

    class _JellyseerrInstanceConfig(ConfigPlugin):
        pass


class JellyseerrInstanceConfig(_JellyseerrInstanceConfig):
    """
    By default, Buildarr will look for a single instance at `http://jellyseerr:5055`.
    Most configurations are different, and to accommodate those, you can configure
    how Buildarr connects to individual Jellyseerr instances.

    Configuration of a single Jellyseerr instance:

    ```yaml
    jellyseerr:
      hostname: "jellyseerr.example.com"
      port: 5055
      protocol: "http"
      api_key: "..." # API key is required.
      settings:
        ...
    ```

    Configuration of multiple instances:

    ```yaml
    jellyseerr:
      # Configuration and settings common to all instances.
      port: 5055
      settings:
        ...
      instances:
        # Jellyseerr instance 1-specific configuration.
        jellyseerr1:
          hostname: "jellyseerr1.example.com"
          api_key: "..." # API key is required.
          settings:
            ...
        # Jellyseerr instance 2-specific configuration.
        jellyseerr2:
          hostname: "jellyseerr2.example.com"
          api_key: "..." # API key is required.
          settings:
            ...
    ```
    """

    hostname: NonEmptyStr = "jellyseerr"  # type: ignore[assignment]
    """
    Hostname of the Jellyseerr instance to connect to.

    When defining a single instance using the global `jellyseerr` configuration block,
    the default hostname is `jellyseerr`.

    When using multiple instance-specific configurations, the default hostname
    is the name given to the instance in the `instances` attribute.

    ```yaml
    jellyseerr:
      instances:
        jellyseerr1: # <--- This becomes the default hostname
          ...
    ```
    """

    port: Port = 5055  # type: ignore[assignment]
    """
    Port number of the Jellyseerr instance to connect to.
    """

    protocol: JellyseerrProtocol = "http"  # type: ignore[assignment]
    """
    Communication protocol to use to connect to Jellyseerr.

    Values:

    * `http`
    * `https`
    """

    api_key: Optional[JellyseerrApiKey] = None
    """
    API key to use to authenticate with the Jellyseerr instance.

    **This attribute is required.
    Buildarr is unable to automatically fetch the Jellyseerr API key.**
    """

    image: NonEmptyStr = "fallenbagel/jellyseerr"  # type: ignore[assignment]
    """
    The default Docker image URI when generating a Docker Compose file.
    """

    version: Optional[str] = None
    """
    The expected version of the Jellyseerr instance.
    If undefined or set to `None`, the version is auto-detected.

    This value is also used when generating a Docker Compose file.
    When undefined or set to `None`, the version tag will be set to `latest`.
    """

    settings: JellyseerrSettings = JellyseerrSettings()
    """
    Jellyseerr settings.
    Configuration options for Jellyseerr itself are set within this structure.
    """

    def is_initialized(self) -> bool:
        return self.settings.jellyfin._is_initialized(self.host_url)

    def initialize(self, tree: str) -> None:
        self.settings.jellyfin._initialize(f"{tree}.settings.jellyfin", self.host_url)

    @classmethod
    def from_remote(cls, secrets: JellyseerrSecrets) -> Self:
        return cls(
            hostname=secrets.hostname,
            port=secrets.port,
            protocol=secrets.protocol,
            api_key=secrets.api_key,
            version=api_get(secrets, "/api/v1/status")["version"],
            settings=JellyseerrSettings.from_remote(secrets),
        )

    def to_compose_service(self, compose_version: str, service_name: str) -> Dict[str, Any]:
        return {
            "image": f"{self.image}:{self.version or 'latest'}",
            "volumes": {service_name: "/app/config"},
        }

    def _resolve(self, secrets: JellyseerrSecrets) -> Self:
        resolved = self.copy(deep=True)
        resolved.settings.services.radarr._resolve_(secrets)
        resolved.settings.services.sonarr._resolve_(secrets)
        return resolved


class JellyseerrConfig(JellyseerrInstanceConfig):
    """
    Jellyseerr plugin global configuration class.
    """

    instances: Dict[str, JellyseerrInstanceConfig] = {}
    """
    Instance-specific Jellyseerr configuration.

    Can only be defined on the global `jellyseerr` configuration block.

    Globally specified configuration values apply to all instances.
    Configuration values specified on an instance-level take precedence at runtime.
    """
