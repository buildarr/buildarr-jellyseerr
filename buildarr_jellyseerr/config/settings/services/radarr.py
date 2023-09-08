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
Jellyseerr plugin Radarr service configuration.
"""


from __future__ import annotations

import logging

from http import HTTPStatus
from typing import Any, Dict, List, Mapping, Optional, Set, Union

from buildarr.config import RemoteMapEntry
from buildarr.state import state
from buildarr.types import BaseEnum, InstanceName, NonEmptyStr, Port
from pydantic import Field, validator
from typing_extensions import Self

from ....api import api_delete, api_get, api_post, api_put
from ....secrets import JellyseerrSecrets
from ....types import ArrApiKey
from ...types import JellyseerrConfigBase
from .base import ArrBase

logger = logging.getLogger(__name__)


class MinimumAvailability(BaseEnum):
    accounced = "announced"
    in_cinemas = "inCinemas"
    released = "released"


class Radarr(ArrBase):
    # Radarr application link for Jellyseerr.

    instance_name: Optional[InstanceName] = Field(None, plugin="radarr")
    """
    The name of the Radarr instance within Buildarr, if linking this Radarr instance
    with another Buildarr-defined Radarr instance.
    """

    port: Port = 7878  # type: ignore[assignment]
    """
    The communication port that the Radarr server listens on.
    """

    api_key: Optional[ArrApiKey] = None
    """
    API key for the Radarr server.

    When not linking to a Buildarr-defined instance using `instance_name`,
    this attribute is required.
    """

    root_folder: NonEmptyStr
    """
    Target root folder to use for movies in Radarr.
    """

    quality_profile: Union[NonEmptyStr, int]
    """
    Quality profile to use for movies in Radarr.
    """

    minimum_availability: MinimumAvailability = MinimumAvailability.released
    """
    The point of release at which requested movies are added to Radarr.

    Values:

    * `announced`
    * `in-cinemas`
    * `released`
    """

    tags: Set[Union[NonEmptyStr, int]] = set()
    """
    Tags to assign to movies in Radarr.
    """

    @validator("api_key")
    def required_if_instance_name_not_defined(cls, value: Any, values: Mapping[str, Any]) -> Any:
        try:
            if not values["instance_name"] and not value:
                raise ValueError("required when 'instance_name' is not defined")
        except KeyError:
            pass
        return value

    @classmethod
    def _get_remote_map(
        cls,
        quality_profile_ids: Optional[Mapping[str, int]] = None,
        tag_ids: Optional[Mapping[str, int]] = None,
    ) -> List[RemoteMapEntry]:
        if not quality_profile_ids:
            quality_profile_ids = {}
        if not tag_ids:
            tag_ids = {}
        return [
            *cls._base_remote_map,
            ("api_key", "apiKey", {}),
            ("root_folder", "activeDirectory", {}),
            # `quality_profile` supplies both `activeProfileId` and `ActiveProfileName`
            # on the remote.
            (
                "quality_profile",
                "activeProfileId",
                {
                    # No decoder here: The quality profile ID will get resolved
                    # later *if* a Buildarr instance-to-instance link is used.
                    "encoder": lambda v: (
                        quality_profile_ids[v] if quality_profile_ids and isinstance(v, str) else v
                    ),
                },
            ),
            ("quality_profile", "activeProfileName", {}),
            ("tags", "tags", {"encoder": lambda v: sorted(tag_ids[tag] for tag in v)}),
            ("minimum_availability", "minimumAvailability", {"optional": True}),
        ]

    @classmethod
    def _from_remote(cls, remote_attrs: Mapping[str, Any]) -> Self:
        return cls(
            **cls.get_local_attrs(remote_map=cls._get_remote_map(), remote_attrs=remote_attrs),
        )

    def _get_api_key(self) -> str:
        if self.instance_name and not self.api_key:
            return state.secrets.radarr[  # type: ignore[attr-defined]
                self.instance_name
            ].api_key.get_secret_value()
        else:
            return self.api_key.get_secret_value()  # type: ignore[union-attr]

    def _get_api_metadata(self, secrets: JellyseerrSecrets, api_key: str) -> Dict[str, Any]:
        return api_post(
            secrets,
            "/api/v1/settings/radarr/test",
            {
                "hostname": self.hostname,
                "port": self.port,
                "useSsl": self.use_ssl,
                "apiKey": api_key,
                **({"urlBase": self.url_base} if self.url_base else {}),
            },
            expected_status_code=HTTPStatus.OK,
        )

    def _resolve(
        self,
        api_key: str,
        root_folders: Set[str],
        quality_profile_ids: Mapping[str, int],
        tag_ids: Mapping[str, int],
        required: bool = True,
    ) -> Self:
        resolved = self.copy(deep=True)
        resolved.api_key = api_key  # type: ignore[assignment]
        if required and resolved.root_folder not in root_folders:
            raise ValueError(
                f"Invalid root folder '{resolved.root_folder}' "
                f"(expected one of: {', '.join(repr(rf) for rf in root_folders)})",
            )
        resolved.quality_profile = self._resolve_get_resource(  # type: ignore[assignment]
            resource_description="quality profile",
            resource_ids=quality_profile_ids,
            resource_ref=resolved.quality_profile,
            required=required,
        )
        resolved.tags = set(
            self._resolve_get_resource(  # type: ignore[misc]
                resource_description="tag",
                resource_ids=tag_ids,
                resource_ref=tag,
                required=required,
            )
            for tag in resolved.tags
        )
        return resolved

    def _resolve_get_resource(
        self,
        resource_description: str,
        resource_ids: Mapping[str, int],
        resource_ref: Union[str, int],
        required: bool,
    ) -> Union[str, int]:
        if isinstance(resource_ref, int):
            for resource_name, resource_id in resource_ids.items():
                if resource_id == resource_ref:
                    return resource_name
            if required:
                raise ValueError(
                    f"Invalid {resource_description} ID {resource_ref} "
                    "(expected one of: "
                    f"{', '.join(f'{rn!r} ({rid})' for rn, rid in resource_ids.items())}"
                    ")",
                )
            else:
                return resource_ref
        if not required or resource_ref in resource_ids:
            return resource_ref
        raise ValueError(
            f"Invalid {resource_description} name '{resource_ref}' "
            f"(expected one of: "
            f"{', '.join(f'{rn!r} ({rid})' for rn, rid in resource_ids.items())}"
            ")",
        )

    def _create_remote(
        self,
        tree: str,
        secrets: JellyseerrSecrets,
        quality_profile_ids: Mapping[str, int],
        tag_ids: Mapping[str, int],
        service_name: str,
    ) -> None:
        remote_attrs = {
            "name": service_name,
            **self.get_create_remote_attrs(
                tree=tree,
                remote_map=self._get_remote_map(quality_profile_ids, tag_ids),
            ),
        }
        api_post(secrets, "/api/v1/settings/radarr", {"name": service_name, **remote_attrs})

    def _update_remote(
        self,
        tree: str,
        secrets: JellyseerrSecrets,
        remote: Self,
        quality_profile_ids: Mapping[str, int],
        tag_ids: Mapping[str, int],
        service_id: int,
        service_name: str,
    ) -> bool:
        changed, remote_attrs = self.get_update_remote_attrs(
            tree=tree,
            remote=remote,
            remote_map=self._get_remote_map(quality_profile_ids, tag_ids),
            set_unchanged=True,
        )
        if changed:
            api_put(
                secrets,
                f"/api/v1/settings/radarr/{service_id}",
                {"name": service_name, **remote_attrs},
            )
            return True
        return False

    def _delete_remote(self, secrets: JellyseerrSecrets, service_id: int) -> None:
        api_delete(secrets, f"/api/v1/settings/radarr/{service_id}")


class RadarrSettings(JellyseerrConfigBase):
    """
    Jellyseerr relies on Radarr for tracking, downloading and managing local copies
    of movies.

    When a request is made for a movie, Jellyseerr will add it to Radarr.

    !!! note

        At the time of release, a Radarr plugin is not yet available for Buildarr.

        Until one is released, an API key must be specified when adding a Radarr instance
        to Jellyseerr.

    A common usage pattern is having multiple Radarr instances, one for non-4K movies
    and another for 4K movies:

    ```yaml
    jellyseerr:
      settings:
        sonarr:
          delete_unmanaged: false
          definitions:
            "Radarr (HD)":
              is_default_server: true
              is_4k_server: false
              hostname: "localhost"
              port: 7878
              use_ssl: false
              api_key: "..."
              root_folder: "/data/media/movies/hd"
              quality_profile: "HD Movies"
              minimum_availability: "released"
              tags: []
              enable_scan: false
              enable_automatic_search: true
            "Radarr (4K)":
              is_default_server: true
              is_4k_server: true
              hostname: "localhost"
              port: 7879
              use_ssl: false
              api_key: "..."
              root_folder: "/data/media/movies/4k"
              quality_profile: "4K Movies"
              minimum_availability: "released"
              tags: []
              enable_scan: false
              enable_automatic_search: true
    ```

    For more information on configuring Radarr instances in Jellyseerr, refer to
    [this guide](https://docs.overseerr.dev/using-overseerr/settings#radarr-sonarr-settings)
    in the Overseerr documentation.
    """

    delete_unmanaged: bool = False
    """
    Automatically delete Radarr instance links not configured in Buildarr.

    If unsure, leave set to the default value of `false`.
    """

    definitions: Dict[str, Radarr] = {}
    """
    Radarr service definitions are defined here.
    """

    @validator("definitions")
    def only_one_default_non4k_instance(cls, value: Dict[str, Radarr]) -> Dict[str, Radarr]:
        default_instances: List[str] = []
        for instance_name, instance in value.items():
            if instance.is_default_server and not instance.is_4k_server:
                default_instances.append(instance_name)
        if len(default_instances) > 1:
            raise ValueError(
                "more than one instance set as the non-4K default: "
                f"{', '.join(repr(instance_name) for instance_name in default_instances)}",
            )
        return value

    @validator("definitions")
    def only_one_default_4k_instance(cls, value: Dict[str, Radarr]) -> Dict[str, Radarr]:
        default_4k_instances: List[str] = []
        for instance_name, instance in value.items():
            if instance.is_default_server and instance.is_4k_server:
                default_4k_instances.append(instance_name)
        if len(default_4k_instances) > 1:
            raise ValueError(
                "more than one instance set as the 4K default: "
                f"{', '.join(repr(instance_name) for instance_name in default_4k_instances)}",
            )
        return value

    @classmethod
    def from_remote(cls, secrets: JellyseerrSecrets) -> Self:
        return cls(
            definitions={
                api_service["name"]: Radarr._from_remote(api_service)
                for api_service in api_get(secrets, "/api/v1/settings/radarr")
            },
        )

    def update_remote(
        self,
        tree: str,
        secrets: JellyseerrSecrets,
        remote: Self,
        check_unmanaged: bool = False,
    ) -> bool:
        # Track whether or not any changes have been made on the remote instance.
        changed = False
        # Pull API objects and metadata required during the update operation.
        service_ids = {
            api_service["name"]: api_service["id"]
            for api_service in api_get(secrets, "/api/v1/settings/radarr")
        }
        # Compare local definitions to their remote equivalent.
        # If a local definition does not exist on the remote, create it.
        # If it does exist on the remote, attempt an an in-place modification,
        # and set the `changed` flag if modifications were made.
        for service_name, service in self.definitions.items():
            profile_tree = f"{tree}.definitions[{service_name!r}]"
            api_key = service._get_api_key()
            api_metadata = service._get_api_metadata(secrets, api_key)
            root_folders: Set[str] = set(
                api_rootfolder["path"] for api_rootfolder in api_metadata["rootFolders"]
            )
            quality_profile_ids: Dict[str, int] = {
                api_profile["name"]: api_profile["id"] for api_profile in api_metadata["profiles"]
            }
            tag_ids: Dict[str, int] = {
                api_profile["label"]: api_profile["id"] for api_profile in api_metadata["tags"]
            }
            resolved_service = service._resolve(
                api_key=api_key,
                root_folders=root_folders,
                quality_profile_ids=quality_profile_ids,
                tag_ids=tag_ids,
            )
            if service_name not in remote.definitions:
                resolved_service._create_remote(
                    tree=profile_tree,
                    secrets=secrets,
                    quality_profile_ids=quality_profile_ids,
                    tag_ids=tag_ids,
                    service_name=service_name,
                )
                changed = True
            elif resolved_service._update_remote(
                tree=profile_tree,
                secrets=secrets,
                remote=remote.definitions[service_name]._resolve(  # type: ignore[arg-type]
                    api_key=api_key,
                    root_folders=root_folders,
                    quality_profile_ids=quality_profile_ids,
                    tag_ids=tag_ids,
                    required=False,
                ),
                quality_profile_ids=quality_profile_ids,
                tag_ids=tag_ids,
                service_id=service_ids[service_name],
                service_name=service_name,
            ):
                changed = True
        # Return whether or not the remote instance was changed.
        return changed

    def delete_remote(
        self,
        tree: str,
        secrets: JellyseerrSecrets,
        remote: Self,
    ) -> bool:
        # Track whether or not any changes have been made on the remote instance.
        changed = False
        # Pull API objects and metadata required during the update operation.
        service_ids = {
            api_service["name"]: api_service["id"]
            for api_service in api_get(secrets, "/api/v1/settings/radarr")
        }
        # Traverse the remote definitions, and see if there are any remote definitions
        # that do not exist in the local configuration.
        # If `delete_unmanaged` is enabled, delete it from the remote.
        # If `delete_unmanaged` is disabled, just add a log entry acknowledging
        # the existence of the unmanaged definition.
        for service_name, service in remote.definitions.items():
            if service_name not in self.definitions:
                profile_tree = f"{tree}.definitions[{service_name!r}]"
                if self.delete_unmanaged:
                    logger.info("%s: (...) -> (deleted)", profile_tree)
                    service._delete_remote(secrets=secrets, service_id=service_ids[service_name])
                    changed = True
                else:
                    logger.debug("%s: (...) (unmanaged)", profile_tree)
        # Return whether or not the remote instance was changed.
        return changed

    def _resolve_(self, secrets: JellyseerrSecrets) -> None:
        resolved_definitions: Dict[str, Radarr] = {}
        for service_name, service in self.definitions.items():
            api_key = service._get_api_key()
            api_metadata = service._get_api_metadata(secrets, api_key)
            root_folders: Set[str] = set(
                api_rootfolder["path"] for api_rootfolder in api_metadata["rootFolders"]
            )
            quality_profile_ids: Dict[str, int] = {
                api_profile["name"]: api_profile["id"] for api_profile in api_metadata["profiles"]
            }
            tag_ids: Dict[str, int] = {
                api_profile["label"]: api_profile["id"] for api_profile in api_metadata["tags"]
            }
            resolved_definitions[service_name] = service._resolve(
                api_key=api_key,
                root_folders=root_folders,
                quality_profile_ids=quality_profile_ids,
                tag_ids=tag_ids,
            )
        self.definitions = resolved_definitions
