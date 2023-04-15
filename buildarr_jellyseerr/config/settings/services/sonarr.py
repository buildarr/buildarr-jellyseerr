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
Jellyseerr plugin Sonarr service configuration.
"""


from __future__ import annotations

import logging

from http import HTTPStatus
from typing import Any, Dict, List, Mapping, Optional, Set, Union

from buildarr.config import RemoteMapEntry
from buildarr.state import state
from buildarr.types import InstanceName, NonEmptyStr, Port
from pydantic import Field, validator
from typing_extensions import Self

from ....api import api_delete, api_get, api_post, api_put
from ....secrets import JellyseerrSecrets
from ....types import ArrApiKey
from ...types import JellyseerrConfigBase
from .base import ArrBase

logger = logging.getLogger(__name__)


class Sonarr(ArrBase):
    # Sonarr application link for Jellyseerr.

    instance_name: Optional[InstanceName] = Field(None, plugin="sonarr")
    """
    The name of the Sonarr instance within Buildarr, if linking this Sonarr instance
    with another Buildarr-defined Sonarr instance.
    """

    port: Port = 8989  # type: ignore[assignment]
    """
    The communication port that the Sonarr server listens on.
    """

    api_key: Optional[ArrApiKey] = None
    """
    API key for the Sonarr server.

    When not linking to a Buildarr-defined instance using `instance_name`,
    this attribute is required.
    """

    root_folder: NonEmptyStr
    """
    Target root folder to use for series in Sonarr.
    """

    quality_profile: Union[NonEmptyStr, int]
    """
    Quality profile to use for series in Sonarr.
    """

    language_profile: Union[NonEmptyStr, int]
    """
    Quality profile to use for series in Sonarr.
    """

    tags: Set[Union[NonEmptyStr, int]] = set()
    """
    Tags to assign to series in Sonarr.
    """

    anime_root_folder: Optional[Union[NonEmptyStr, int]] = None
    """
    Target root folder to use for series classified as anime in Sonarr.
    """

    anime_quality_profile: Optional[Union[NonEmptyStr, int]] = None
    """
    Quality profile to use for series classified as anime in Sonarr.
    """

    anime_language_profile: Optional[Union[NonEmptyStr, int]] = None
    """
    Language profile to use for series classified as anime in Sonarr.
    """

    anime_tags: Set[Union[NonEmptyStr, int]] = set()
    """
    Tags to assign to series classified as anime in Sonarr.
    """

    enable_season_folders: bool = False
    """
    Sort series into subfolders for each season.
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
        language_profile_ids: Optional[Mapping[str, int]] = None,
        tag_ids: Optional[Mapping[str, int]] = None,
    ) -> List[RemoteMapEntry]:
        if not quality_profile_ids:
            quality_profile_ids = {}
        if not language_profile_ids:
            language_profile_ids = {}
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
            (
                "language_profile",
                "activeLanguageProfileId",
                {
                    # No decoder here: The language profile ID will get resolved
                    # later *if* a Buildarr instance-to-instance link is used.
                    "encoder": lambda v: language_profile_ids[v],
                },
            ),
            ("tags", "tags", {"encoder": lambda v: sorted(tag_ids[tag] for tag in v)}),
            (
                "anime_root_folder",
                "activeAnimeDirectory",
                {
                    "decoder": lambda v: v or None,
                    "encoder": lambda v: v or "",
                },
            ),
            # `anime_quality_profile` supplies both `activeAnimeProfileId`
            # and `ActiveAnimeProfileName` on the remote.
            (
                "anime_quality_profile",
                "activeAnimeProfileId",
                {
                    # No decoder here: The quality profile ID will get resolved
                    # later *if* a Buildarr instance-to-instance link is used.
                    "optional": True,
                    "set_if": bool,
                    "encoder": lambda v: quality_profile_ids[v],
                },
            ),
            (
                "anime_quality_profile",
                "activeAnimeProfileName",
                {"optional": True, "set_if": bool},
            ),
            (
                "anime_language_profile",
                "activeAnimeLanguageProfileId",
                {
                    # No decoder here: The language profile ID will get resolved
                    # later *if* a Buildarr instance-to-instance link is used.
                    "optional": True,
                    "set_if": bool,
                    "encoder": lambda v: language_profile_ids[v],
                },
            ),
            ("anime_tags", "animeTags", {"encoder": lambda v: sorted(tag_ids[tag] for tag in v)}),
            ("enable_season_folders", "enableSeasonFolders", {}),
        ]

    @classmethod
    def _from_remote(cls, remote_attrs: Mapping[str, Any]) -> Self:
        return cls(
            **cls.get_local_attrs(remote_map=cls._get_remote_map(), remote_attrs=remote_attrs),
        )

    def _get_api_key(self) -> str:
        if self.instance_name and not self.api_key:
            return state.secrets.sonarr[  # type: ignore[attr-defined]
                self.instance_name
            ].api_key.get_secret_value()
        else:
            return self.api_key.get_secret_value()  # type: ignore[union-attr]

    def _get_api_metadata(self, secrets: JellyseerrSecrets, api_key: str) -> Dict[str, Any]:
        return api_post(
            secrets,
            "/api/v1/settings/sonarr/test",
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
        language_profile_ids: Mapping[str, int],
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
        resolved.language_profile = self._resolve_get_resource(  # type: ignore[assignment]
            resource_description="language profile",
            resource_ids=language_profile_ids,
            resource_ref=resolved.language_profile,
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
        if resolved.anime_quality_profile:
            resolved.anime_quality_profile = self._resolve_get_resource(  # type: ignore[assignment]
                resource_description="quality profile",
                resource_ids=quality_profile_ids,
                resource_ref=resolved.anime_quality_profile,
                required=required,
            )
        else:
            resolved.anime_quality_profile = None
        if resolved.anime_language_profile:
            resolved.anime_language_profile = (
                self._resolve_get_resource(  # type: ignore[assignment]
                    resource_description="language profile",
                    resource_ids=language_profile_ids,
                    resource_ref=resolved.anime_language_profile,
                    required=required,
                )
            )
        else:
            resolved.anime_language_profile = None
        resolved.anime_tags = set(
            self._resolve_get_resource(  # type: ignore[misc]
                resource_description="tag",
                resource_ids=tag_ids,
                resource_ref=tag,
                required=required,
            )
            for tag in resolved.anime_tags
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
                    f"{', '.join(f'{repr(rn)} ({rid})' for rn, rid in resource_ids.items())}"
                    ")",
                )
            else:
                return resource_ref
        if not required or resource_ref in resource_ids:
            return resource_ref
        raise ValueError(
            f"Invalid {resource_description} name '{resource_ref}' "
            f"(expected one of: "
            f"{', '.join(f'{repr(rn)} ({rid})' for rn, rid in resource_ids.items())}"
            ")",
        )

    def _create_remote(
        self,
        tree: str,
        secrets: JellyseerrSecrets,
        quality_profile_ids: Mapping[str, int],
        language_profile_ids: Mapping[str, int],
        tag_ids: Mapping[str, int],
        service_name: str,
    ) -> None:
        remote_attrs = {
            "name": service_name,
            **self.get_create_remote_attrs(
                tree=tree,
                remote_map=self._get_remote_map(quality_profile_ids, language_profile_ids, tag_ids),
            ),
        }
        api_post(secrets, "/api/v1/settings/sonarr", {"name": service_name, **remote_attrs})

    def _update_remote(
        self,
        tree: str,
        secrets: JellyseerrSecrets,
        remote: Self,
        quality_profile_ids: Mapping[str, int],
        language_profile_ids: Mapping[str, int],
        tag_ids: Mapping[str, int],
        service_id: int,
        service_name: str,
    ) -> bool:
        changed, remote_attrs = self.get_update_remote_attrs(
            tree=tree,
            remote=remote,
            remote_map=self._get_remote_map(quality_profile_ids, language_profile_ids, tag_ids),
            set_unchanged=True,
        )
        if changed:
            api_put(
                secrets,
                f"/api/v1/settings/sonarr/{service_id}",
                {"name": service_name, **remote_attrs},
            )
            return True
        return False

    def _delete_remote(self, secrets: JellyseerrSecrets, service_id: int) -> None:
        api_delete(secrets, f"/api/v1/settings/sonarr/{service_id}")


class SonarrSettings(JellyseerrConfigBase):
    """
    Jellyseerr relies on Sonarr for tracking, downloading and managing local copies
    of series (TV shows).

    When a request is made for a series, Jellyseerr will add it to Sonarr.

    !!! note

        At the time of release, Sonarr V4 is
        [not fully supported](https://github.com/Fallenbagel/jellyseerr/issues/207)
        by Jellyseerr, as Sonarr V4 does not have language profiles.

        Buildarr does not support linking Jellyseerr instances with Sonarr V4 instances.

    In Buildarr, Jellyseerr can be linked to one or more Sonarr instances via instance links,
    using the `instance_name` attribute. Jellyseerr can also have non-Buildarr managed Sonarr
    instances added to it by explicitly defining the API key used to connect to it.

    A common usage pattern is having multiple Sonarr instances, one for non-4K series
    and another for 4K series:

    ```yaml
    sonarr:
      settings:
        language_profiles:
          definitions:
            "English":
              languages:
                - "English"
      instances:
        sonarr-hd:
          host: "localhost"
          port: 8989
          protocol: "http"
          api_key: "..."
          settings:
            media_management:
              root_folders:
                - "/data/media/shows/hd"
            profiles:
              quality_profiles:
                definitions:
                  "HD Series":
                    ...
        sonarr-4k:
          host: "localhost"
          port: 8990
          protocol: "http"
          api_key: "..."
          settings:
            media_management:
              root_folders:
                - "/data/media/shows/4k"
            profiles:
              quality_profiles:
                definitions:
                  "4K Series":
                    ...

    jellyseerr:
      settings:
        sonarr:
          delete_unmanaged: false
          definitions:
            "Sonarr (HD)":
              is_default_server: true
              is_4k_server: false
              instance_name: "sonarr-hd"
              hostname: "localhost"
              port: 8989
              use_ssl: false
              root_folder: "/data/media/shows/hd"
              quality_profile: "HD Series"
              language_profile: "English"
              tags: []
              enable_season_folders: true
              enable_scan: false
              enable_automatic_search: true
            "Sonarr (4K)":
              is_default_server: true
              is_4k_server: true
              instance_name: "sonarr-4k"
              hostname: "localhost"
              port: 8990
              use_ssl: false
              root_folder: "/data/media/shows/4k"
              quality_profile: "4K Series"
              language_profile: "English"
              tags: []
              enable_season_folders: true
              enable_scan: false
              enable_automatic_search: true
    ```

    For more information on configuring Sonarr instances in Jellyseerr, refer to
    [this guide](https://docs.overseerr.dev/using-overseerr/settings#radarr-sonarr-settings)
    in the Overseerr documentation.
    """

    delete_unmanaged: bool = False
    """
    Automatically delete Sonarr instance links not configured in Buildarr.

    If unsure, leave set to the default value of `false`.
    """

    definitions: Dict[str, Sonarr] = {}
    """
    Sonarr service definitions are defined here.
    """

    @validator("definitions")
    def only_one_default_non4k_instance(cls, value: Dict[str, Sonarr]) -> Dict[str, Sonarr]:
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
    def only_one_default_4k_instance(cls, value: Dict[str, Sonarr]) -> Dict[str, Sonarr]:
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
                api_service["name"]: Sonarr._from_remote(api_service)
                for api_service in api_get(secrets, "/api/v1/settings/sonarr")
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
            for api_service in api_get(secrets, "/api/v1/settings/sonarr")
        }
        # Compare local definitions to their remote equivalent.
        # If a local definition does not exist on the remote, create it.
        # If it does exist on the remote, attempt an an in-place modification,
        # and set the `changed` flag if modifications were made.
        for service_name, service in self.definitions.items():
            profile_tree = f"{tree}.definitions[{repr(service_name)}]"
            api_key = service._get_api_key()
            api_metadata = service._get_api_metadata(secrets, api_key)
            root_folders: Set[str] = set(
                api_rootfolder["path"] for api_rootfolder in api_metadata["rootFolders"]
            )
            quality_profile_ids: Dict[str, int] = {
                api_profile["name"]: api_profile["id"] for api_profile in api_metadata["profiles"]
            }
            language_profile_ids: Dict[str, int] = {
                api_profile["name"]: api_profile["id"]
                for api_profile in api_metadata["languageProfiles"]
            }
            tag_ids: Dict[str, int] = {
                api_profile["label"]: api_profile["id"] for api_profile in api_metadata["tags"]
            }
            resolved_service = service._resolve(
                api_key=api_key,
                root_folders=root_folders,
                quality_profile_ids=quality_profile_ids,
                language_profile_ids=language_profile_ids,
                tag_ids=tag_ids,
            )
            if service_name not in remote.definitions:
                resolved_service._create_remote(
                    tree=profile_tree,
                    secrets=secrets,
                    quality_profile_ids=quality_profile_ids,
                    language_profile_ids=language_profile_ids,
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
                    language_profile_ids=language_profile_ids,
                    tag_ids=tag_ids,
                    required=False,
                ),
                quality_profile_ids=quality_profile_ids,
                language_profile_ids=language_profile_ids,
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
            for api_service in api_get(secrets, "/api/v1/settings/sonarr")
        }
        # Traverse the remote definitions, and see if there are any remote definitions
        # that do not exist in the local configuration.
        # If `delete_unmanaged` is enabled, delete it from the remote.
        # If `delete_unmanaged` is disabled, just add a log entry acknowledging
        # the existence of the unmanaged definition.
        for service_name, service in remote.definitions.items():
            if service_name not in self.definitions:
                profile_tree = f"{tree}.definitions[{repr(service_name)}]"
                if self.delete_unmanaged:
                    logger.info("%s: (...) -> (deleted)", profile_tree)
                    service._delete_remote(secrets=secrets, service_id=service_ids[service_name])
                    changed = True
                else:
                    logger.debug("%s: (...) (unmanaged)", profile_tree)
        # Return whether or not the remote instance was changed.
        return changed

    def _resolve_(self, secrets: JellyseerrSecrets) -> None:
        resolved_definitions: Dict[str, Sonarr] = {}
        for service_name, service in self.definitions.items():
            api_key = service._get_api_key()
            api_metadata = service._get_api_metadata(secrets, api_key)
            root_folders: Set[str] = set(
                api_rootfolder["path"] for api_rootfolder in api_metadata["rootFolders"]
            )
            quality_profile_ids: Dict[str, int] = {
                api_profile["name"]: api_profile["id"] for api_profile in api_metadata["profiles"]
            }
            language_profile_ids: Dict[str, int] = {
                api_profile["name"]: api_profile["id"]
                for api_profile in api_metadata["languageProfiles"]
            }
            tag_ids: Dict[str, int] = {
                api_profile["label"]: api_profile["id"] for api_profile in api_metadata["tags"]
            }
            resolved_definitions[service_name] = service._resolve(
                api_key=api_key,
                root_folders=root_folders,
                quality_profile_ids=quality_profile_ids,
                language_profile_ids=language_profile_ids,
                tag_ids=tag_ids,
            )
        self.definitions = resolved_definitions
