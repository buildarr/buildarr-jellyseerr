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
Jellyseerr plugin email notifications settings configuration base class.
"""


from __future__ import annotations

from http import HTTPStatus
from typing import List, Set

from buildarr.config import RemoteMapEntry
from pydantic import SecretStr
from typing_extensions import Self

from ....api import api_get, api_post
from ....secrets import JellyseerrSecrets
from ...types import JellyseerrConfigBase


class NotificationsSettingsBase(JellyseerrConfigBase):
    """
    To enable push notifications to a service, simply set `enable: true` in the settings,
    as shown below.

    ```yaml
    jellyseerr:
      settings:
        notifications:
          webpush:
            enable: true
    ```
    """

    enable: bool = False
    """
    Enable sending notifications to a service.

    If enabled, some configuration attributes for the service will be required.
    """

    _type: str
    _required_if_enabled: Set[str] = set()

    @classmethod
    def _get_base_remote_map(cls) -> List[RemoteMapEntry]:
        return [("enable", "enabled", {})]

    @classmethod
    def _get_remote_map(cls) -> List[RemoteMapEntry]:
        raise NotImplementedError()

    @classmethod
    def from_remote(cls, secrets: JellyseerrSecrets) -> Self:
        remote_attrs = api_get(secrets, f"/api/v1/settings/notifications/{cls._type}")
        try:
            options_local_attrs = cls.get_local_attrs(
                cls._get_remote_map(),
                remote_attrs["options"],
            )
        except NotImplementedError:
            options_local_attrs = {}
        return cls(
            **cls.get_local_attrs(cls._get_base_remote_map(), remote_attrs),
            **options_local_attrs,
        )

    def update_remote(
        self,
        tree: str,
        secrets: JellyseerrSecrets,
        remote: Self,
        check_unmanaged: bool = False,
    ) -> bool:
        # Run update checks for the base class attributes.
        base_changed, base_attrs = self.get_update_remote_attrs(
            tree,
            remote,
            self._get_base_remote_map(),
            check_unmanaged=check_unmanaged,
            set_unchanged=True,
        )
        # Run update checks for the implementing class attributes,
        # if additional attributes were defined.
        try:
            remote_map = self._get_remote_map()
            options_changed, options_attrs = self.get_update_remote_attrs(
                tree,
                remote,
                remote_map,
                check_unmanaged=check_unmanaged,
                set_unchanged=True,
            )
        except NotImplementedError:
            remote_map = []
            options_changed = False
            options_attrs = {}
        # Check if attributes in the service that are required when enabled, have been defined.
        if self._required_if_enabled and base_attrs["enabled"]:
            local_remote_name = {entry[0]: entry[1] for entry in remote_map}
            undefined_attrs: List[str] = []
            for attr_name in self._required_if_enabled:
                value = options_attrs[local_remote_name[attr_name]]
                if isinstance(value, SecretStr):
                    value = value.get_secret_value().strip()
                elif isinstance(value, str):
                    value = value.strip()
                if not value:
                    undefined_attrs.append(attr_name)
            if undefined_attrs:
                raise ValueError(
                    f"Attributes for notification type '{self._type}' "
                    "must not be empty when 'enable' is True: "
                    f"{', '.join(repr(attr_name) for attr_name in undefined_attrs)}",
                )
        # If changes were found, update the remote instance.
        if base_changed or options_changed:
            api_attrs = api_get(secrets, f"/api/v1/settings/notifications/{self._type}")
            api_post(
                secrets,
                f"/api/v1/settings/notifications/{self._type}",
                {
                    **api_attrs,
                    **base_attrs,
                    "options": {**api_attrs["options"], **options_attrs},
                },
                expected_status_code=HTTPStatus.OK,
            )
            return True
        return False
