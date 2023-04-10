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
Jellyseerr plugin app sync profile configuration.
"""


from __future__ import annotations

import logging

from contextlib import contextmanager
from http import HTTPStatus
from typing import Any, Dict, Generator, List, Mapping, Optional, Set, Union, cast

import sonarr

from buildarr.config import RemoteMapEntry
from buildarr.state import state
from buildarr.types import InstanceName, NonEmptyStr
from pydantic import Field, validator
from typing_extensions import Self

from ....api import api_delete, api_get, api_post, api_put
from ....secrets import JellyseerrSecrets
from ....types import ArrApiKey
from ...types import JellyseerrConfigBase
from .base import ArrBase

logger = logging.getLogger(__name__)


class Sonarr(ArrBase):
    """
    The following configuration attributes are available for an app sync profile.
    """

    instance_name: Optional[InstanceName] = Field(None, plugin="sonarr")
    """
    The name of the Sonarr instance within Buildarr, if linking this Sonarr instance
    with another Buildarr-defined Sonarr instance.
    """

    api_key: Optional[ArrApiKey] = None

    root_folder: NonEmptyStr

    quality_profile: Union[NonEmptyStr, int]

    language_profile: Union[NonEmptyStr, int]

    tags: Set[Union[NonEmptyStr, int]] = set()

    anime_root_folder: Optional[Union[NonEmptyStr, int]] = None

    anime_quality_profile: Optional[Union[NonEmptyStr, int]] = None

    anime_language_profile: Optional[Union[NonEmptyStr, int]] = None

    anime_tags: Set[Union[NonEmptyStr, int]] = set()

    enable_season_folders: bool = Field(False, alias="season_folders")

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

    def _render(
            self,
            api_key: str,
            root_folders: Set[str],
            quality_profile_ids: Mapping[str, int],
            language_profile_ids: Mapping[str, int],
            tag_ids: Mapping[str, int],
            required: bool = True,
        ) -> Self:
        rendered = self.copy(deep=True)
        rendered.api_key = api_key  # type: ignore[assignment]
        if required and rendered.root_folder not in root_folders:
            raise ValueError(
                f"Invalid root folder '{rendered.root_folder}' "
                f"(expected one of: {', '.join(repr(rf) for rf in root_folders)})",
            )
        rendered.quality_profile = self._render_get_resource(  # type: ignore[assignment]
            resource_description="quality profile",
            resource_ids=quality_profile_ids,
            resource_ref=rendered.quality_profile,
            required=required,
        )
        rendered.language_profile = self._render_get_resource(  # type: ignore[assignment]
            resource_description="language profile",
            resource_ids=language_profile_ids,
            resource_ref=rendered.language_profile,
            required=required,
        )
        rendered.tags = set(
            self._render_get_resource(  # type: ignore[misc]
                resource_description="tag",
                resource_ids=tag_ids,
                resource_ref=tag,
                required=required,
            )
            for tag in rendered.tags
        )
        if rendered.anime_quality_profile:
            rendered.anime_quality_profile = (
                    self._render_get_resource(  # type: ignore[assignment]
                    resource_description="quality profile",
                    resource_ids=quality_profile_ids,
                    resource_ref=rendered.anime_quality_profile,
                    required=required,
                )
            )
        if rendered.anime_language_profile:
            rendered.anime_language_profile = (
                self._render_get_resource(  # type: ignore[assignment]
                    resource_description="language profile",
                    resource_ids=language_profile_ids,
                    resource_ref=rendered.anime_language_profile,
                    required=required,
                )
            )
        rendered.anime_tags = set(
            self._render_get_resource(  # type: ignore[misc]
                resource_description="tag",
                resource_ids=tag_ids,
                resource_ref=tag,
                required=required,
            )
            for tag in rendered.anime_tags
        )
        return rendered

    def _render_get_resource(
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

    def _delete_remote(self, tree: str, secrets: JellyseerrSecrets, service_id: int) -> None:
        logger.info("%s: (...) -> (deleted)", tree)
        api_delete(secrets, f"/api/v1/settings/sonarr/{service_id}")


class SonarrSettings(JellyseerrConfigBase):
    """
    App sync profiles are used to set application syncing configuration
    with respect to an indexer.

    Configure the sync profile in Buildarr:

    ```yaml
    jellyseerr:
      settings:
        sonarr:
          delete_unmanaged: false
          definitions:
            "Standard":
              enable_automatic_search: true
              enable_interactive_search: true
              enable_rss: true
              minimum_seeders: 1
    ```

    When the [`sync_profile`](
    ../indexers/indexers.md#buildarr_prowlarr.config.settings
    .indexers.indexers.Indexer.sync_profile
    )
    attribute on the indexer is set to the name of the
    sync profile, the applications connected to the indexer will respect
    the settings defined in the sync profile for that indexer.

    For more information, refer to the guide for
    [sync profiles](https://wiki.servarr.com/prowlarr/settings#sync-profiles)
    on WikiArr.
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
                api_profile["name"]: api_profile["id"]
                for api_profile in api_metadata["profiles"]
            }
            language_profile_ids: Dict[str, int] = {
                api_profile["name"]: api_profile["id"]
                for api_profile in api_metadata["languageProfiles"]
            }
            tag_ids: Dict[str, int] = {
                api_profile["label"]: api_profile["id"]
                for api_profile in api_metadata["tags"]
            }
            rendered_service = service._render(
                api_key=api_key,
                root_folders=root_folders,
                quality_profile_ids=quality_profile_ids,
                language_profile_ids=language_profile_ids,
                tag_ids=tag_ids,
            )
            if service_name not in remote.definitions:
                rendered_service._create_remote(
                    tree=profile_tree,
                    secrets=secrets,
                    quality_profile_ids=quality_profile_ids,
                    language_profile_ids=language_profile_ids,
                    tag_ids=tag_ids,
                    service_name=service_name,
                )
                changed = True
            elif rendered_service._update_remote(
                tree=profile_tree,
                secrets=secrets,
                remote=remote.definitions[service_name]._render(  # type: ignore[arg-type]
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
        # Traverse the remote definitions, and see if there are any remote definitions
        # that do not exist in the local configuration.
        # If `delete_unmanaged` is enabled, delete it from the remote.
        # If `delete_unmanaged` is disabled, just add a log entry acknowledging
        # the existence of the unmanaged definition.
        for service_name, service in remote.definitions.items():
            if service_name not in self.definitions:
                profile_tree = f"{tree}.definitions[{repr(service_name)}]"
                if self.delete_unmanaged:
                    service._delete_remote(
                        tree=profile_tree,
                        secrets=secrets,
                        service_id=service_ids[service_name],
                    )
                    changed = True
                else:
                    logger.debug("%s: (...) (unmanaged)", profile_tree)
        # Return whether or not the remote instance was changed.
        return changed


@contextmanager
def sonarr_api_client(*, host_url: str, api_key: str) -> Generator[sonarr.ApiClient, None, None]:
    """
    Create a Sonarr API client object, and make it available within a context.

    Args:
        host_url (str): Host URL for the Sonarr instance.
        api_key (str): API key to use to access the Sonarr instance.

    Yields:
        Sonarr API client object
    """

    configuration = sonarr.Configuration(host=host_url)

    root_logger = logging.getLogger()
    configuration.logger_format = cast(
        str,
        cast(logging.Formatter, root_logger.handlers[0].formatter)._fmt,
    )
    configuration.debug = logging.getLevelName(root_logger.level) == "DEBUG"
    configuration.api_key["X-Api-Key"] = api_key

    with sonarr.ApiClient(configuration) as api_client:
        yield api_client
