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
Jellyseerr plugin settings configuration.
"""


from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import Self

from ..types import JellyseerrConfigBase
from .general import JellyseerrGeneralSettings
from .jellyfin import JellyseerrJellyfinSettings
from .services import JellyseerrServicesSettings
from .users import JellyseerrUsersSettings

# from .apps import JellyseerrAppsSettings
# from .download_clients import JellyseerrDownloadClientsSettings
# from .indexers import JellyseerrIndexersSettings
# from .notifications import JellyseerrNotificationsSettings
# from .tags import JellyseerrTagsSettings
# from .ui import JellyseerrUISettings

if TYPE_CHECKING:
    from ...secrets import JellyseerrSecrets


class JellyseerrSettings(JellyseerrConfigBase):
    """
    Jellyseerr settings, used to configure a remote Jellyseerr instance.
    """

    # indexers: JellyseerrIndexersSettings = JellyseerrIndexersSettings()
    # apps: JellyseerrAppsSettings = JellyseerrAppsSettings()
    # download_clients: JellyseerrDownloadClientsSettings = JellyseerrDownloadClientsSettings()
    # notifications: JellyseerrNotificationsSettings = JellyseerrNotificationsSettings()
    # tags: JellyseerrTagsSettings = JellyseerrTagsSettings()
    general: JellyseerrGeneralSettings = JellyseerrGeneralSettings()
    jellyfin: JellyseerrJellyfinSettings = JellyseerrJellyfinSettings()
    users: JellyseerrUsersSettings = JellyseerrUsersSettings()
    services: JellyseerrServicesSettings = JellyseerrServicesSettings()

    def update_remote(
        self,
        tree: str,
        secrets: JellyseerrSecrets,
        remote: Self,
        check_unmanaged: bool = False,
    ) -> bool:
        # Overload base function to guarantee execution order of section updates.
        # 1. Tags must be created before everything else, and destroyed after they
        #    are no longer referenced elsewhere.
        return any(
            [
                # self.tags.update_remote(
                #     f"{tree}.tags",
                #     secrets,
                #     remote.tags,
                #     check_unmanaged=check_unmanaged,
                # ),
                # self.apps.update_remote(
                #     f"{tree}.apps",
                #     secrets,
                #     remote.apps,
                #     check_unmanaged=check_unmanaged,
                # ),
                # self.indexers.update_remote(
                #     f"{tree}.indexers",
                #     secrets,
                #     remote.indexers,
                #     check_unmanaged=check_unmanaged,
                # ),
                # self.download_clients.update_remote(
                #     f"{tree}.download_clients",
                #     secrets,
                #     remote.download_clients,
                #     check_unmanaged=check_unmanaged,
                # ),
                self.jellyfin.update_remote(
                    f"{tree}.jellyfin",
                    secrets,
                    remote.jellyfin,
                    check_unmanaged=check_unmanaged,
                ),
                self.general.update_remote(
                    f"{tree}.general",
                    secrets,
                    remote.general,
                    check_unmanaged=check_unmanaged,
                ),
                self.users.update_remote(
                    f"{tree}.users",
                    secrets,
                    remote.users,
                    check_unmanaged=check_unmanaged,
                ),
                self.services.update_remote(
                    f"{tree}.services",
                    secrets,
                    remote.services,
                    check_unmanaged=check_unmanaged,
                ),
                # TODO: destroy indexers
                # TODO: destroy tags
            ],
        )
