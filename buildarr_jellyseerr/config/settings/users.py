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
Jellyseerr plugin global users settings configuration.
"""


from __future__ import annotations

import functools
import operator

from http import HTTPStatus
from typing import Dict, Iterable, List, Set

from buildarr.config import RemoteMapEntry
from buildarr.types import BaseEnum
from pydantic import Field, validator
from typing_extensions import Self

from ...api import api_get, api_post
from ...secrets import JellyseerrSecrets
from ..types import JellyseerrConfigBase


class Permission(BaseEnum):
    # none = 0
    admin = 2
    manage_settings = 4
    manage_users = 8
    manage_requests = 16
    request = 32
    vote = 64
    auto_approve = 128
    auto_approve_movie = 256
    auto_approve_series = 512
    request_4k = 1024
    request_4k_movie = 2048
    request_4k_series = 4096
    request_advanced = 8192
    request_view = 16384
    auto_approve_4k = 32768
    auto_approve_4k_movie = 65536
    auto_approve_4k_series = 131072
    request_movie = 262144
    request_series = 524288
    manage_issues = 1048576
    view_issues = 2097152
    create_issues = 4194304
    auto_request = 8388608
    auto_request_movie = 16777216
    auto_request_series = 33554432
    recent_view = 67108864
    watchlist_view = 134217728

    def is_permitted(self, permissions_encoded: int) -> bool:
        return bool(permissions_encoded & self.value)

    @classmethod
    def set_reduce(cls, permissions: Iterable[Permission]) -> Set[Permission]:
        return cls.set_decoder(cls.set_encoder(permissions))

    @classmethod
    def set_decoder(cls, permissions_encoded: int) -> Set[Permission]:
        # Handle the case where the user has no permissions, or is an admin.
        if not permissions_encoded:
            return set()
        if cls.admin.is_permitted(permissions_encoded):
            return {cls.admin}
        # Collect all allowed permissions into a set.
        permissions: Set[Permission] = set()
        # Add the group permission for managing users, if allowed.
        if cls.manage_users.is_permitted(permissions_encoded):
            permissions.add(cls.manage_users)
        # Add the group permission for managing issues, if allowed.
        # Alternatively, add the individual permissions within the group,
        # if allowed separately.
        if cls.manage_issues.is_permitted(permissions_encoded):
            permissions.add(cls.manage_issues)
        else:
            for permission in (cls.create_issues, cls.view_issues):
                if permission.is_permitted(permissions_encoded):
                    permissions.add(permission)
        # Add the group permission for managing requests, if allowed.
        # Alternatively, add the individual permissions within the group,
        # if allowed separately.
        if cls.manage_requests.is_permitted(permissions_encoded):
            permissions.add(cls.manage_requests)
        else:
            for permission in (
                cls.request_advanced,
                cls.request_view,
                cls.recent_view,
                cls.watchlist_view,
            ):
                if permission.is_permitted(permissions_encoded):
                    permissions.add(permission)
        # Add the group permission for making non-4K media requests, if allowed.
        # Alternatively, add the individual permissions within the group,
        # if allowed separately.
        if cls.request.is_permitted(permissions_encoded):
            permissions.add(cls.request)
        else:
            for permission in (cls.request_movie, cls.request_series):
                if permission.is_permitted(permissions_encoded):
                    permissions.add(permission)
        # Add the group permission for making 4K media requests, if allowed.
        # Alternatively, add the individual permissions within the group,
        # if allowed separately.
        if cls.request_4k:
            permissions.add(cls.request_4k)
        else:
            for permission in (cls.request_4k_movie, cls.request_4k_series):
                if permission.is_permitted(permissions_encoded):
                    permissions.add(permission)
        # Add the group permission for auto-requesting from the
        # Plex Watchlist, if allowed.
        # Check if other permissions these depend on are also allowed.
        # Alternatively, add the individual permissions within the group,
        # if allowed separately.
        if cls.auto_request.is_permitted(permissions_encoded):
            if cls.request not in permissions:
                cls._permission_error(cls.auto_request, cls.request)
            permissions.add(cls.auto_request)
        else:
            if cls.auto_request_movie.is_permitted(permissions_encoded):
                if cls.request not in permissions or cls.request_movie not in permissions:
                    cls._permission_error(cls.auto_request_movie, cls.request_movie)
                permissions.add(cls.auto_request_movie)
            if cls.auto_request_series.is_permitted(permissions_encoded):
                if cls.request not in permissions or cls.request_series not in permissions:
                    cls._permission_error(cls.auto_request_series, cls.request_series)
                permissions.add(cls.auto_request_series)
        # Add the group permission for auto-approving non-4K media requests, if allowed.
        # Check if other permissions these depend on are also allowed.
        # Alternatively, add the individual permissions within the group,
        # if allowed separately.
        if cls.auto_approve.is_permitted(permissions_encoded):
            if cls.request not in permissions:
                cls._permission_error(cls.auto_approve, cls.request)
            permissions.add(cls.auto_approve)
        else:
            if cls.auto_approve_movie.is_permitted(permissions_encoded):
                if cls.request not in permissions or cls.request_movie not in permissions:
                    cls._permission_error(cls.auto_approve_movie, cls.request_movie)
                permissions.add(cls.auto_approve_movie)
            if cls.auto_approve_series.is_permitted(permissions_encoded):
                if cls.request not in permissions or cls.request_series not in permissions:
                    cls._permission_error(cls.auto_approve_series, cls.request_series)
                permissions.add(cls.auto_approve_series)
        # Add the group permission for auto-approving 4K media requests, if allowed.
        # Check if other permissions these depend on are also allowed.
        # Alternatively, add the individual permissions within the group,
        # if allowed separately.
        if cls.auto_approve_4k.is_permitted(permissions_encoded):
            if cls.request_4k not in permissions:
                cls._permission_error(cls.auto_approve_4k, cls.request_4k)
            permissions.add(cls.auto_approve_4k)
        else:
            if cls.auto_approve_4k_movie.is_permitted(permissions_encoded):
                if cls.request_4k not in permissions or cls.request_4k_movie not in permissions:
                    cls._permission_error(cls.auto_approve_4k_movie, cls.request_4k_movie)
                permissions.add(cls.auto_approve_4k_movie)
            if cls.auto_approve_4k_series.is_permitted(permissions_encoded):
                if cls.request_4k not in permissions or cls.request_4k_series not in permissions:
                    cls._permission_error(cls.auto_approve_4k_series, cls.request_4k_series)
                permissions.add(cls.auto_approve_4k_series)
        # Return the final permission set.
        return permissions

    @classmethod
    def _permission_error(cls, permission: Permission, required_permission: Permission) -> None:
        raise ValueError(
            f"permission '{permission.to_name_str()}' "
            f"requires unset permission '{required_permission.to_name_str()}'",
        )

    @classmethod
    def set_encoder(cls, permissions: Iterable[Permission]) -> int:
        return functools.reduce(
            operator.ior,
            (permission.value for permission in permissions),
            0,
        )


class JellyseerrUsersSettings(JellyseerrConfigBase):
    """
    These settings change the behaviour for how Jellyseerr allows logins
    from Jellyfin/Plex users, user permissions, and request limits.

    ```yaml
    jellyseerr:
      settings:
        users:
          enable_local_signin: true
          enable_new_jellyfin_signin: true
          global_movie_request_limit: 0
          global_movie_request_days: 7
          global_series_request_limit: 0
          global_series_request_days: 7
          default_permissions:
            - "request"
            - "request-4k"
    ```
    """

    enable_local_signin: bool = True
    """
    Allow users to sign in using their email address and password, instead of Plex OAuth.
    """

    enable_new_jellyfin_signin: bool = True
    """
    Allow Jellyfin users to sign in without first being imported to Jellyseerr.
    """

    global_movie_request_limit: int = Field(0, ge=0, le=100)
    """
    The maximum number of movie requests within the selected number of days.

    0 is unlimited.
    """

    global_movie_request_days: int = Field(7, ge=1, le=100)
    """
    The timespan that applies to the global movie request limit, in days.
    """

    global_series_request_limit: int = Field(0, ge=0, le=100)
    """
    The maximum number of series (TV show) requests within the selected number of days.

    0 is unlimited.
    """

    global_series_request_days: int = Field(7, ge=1, le=100)
    """
    The timespan that applies to the global series request limit, in days.
    """

    default_permissions: Set[Permission] = {Permission.request, Permission.request_4k}
    """
    Permissions to grant to newly created users by default.

    Privileged permissions such as `admin`, `manage-users`, `manage-requests`,
    `auto-approve`, `auto-approve-4k`, and `manage-issues` generally should not be
    enabled by default.

    Instead, allow specific permissions under that category you wish to grant to new users.

    Values:

    * `admin` - Full administrator access. Bypasses all other permission checks.
    * `manage-users` - Grant permission to manage users.
      Users with this permission cannot modify users with or grant the `admin` privilege.
    * `manage-requests` - Grant permission to manage media requests.
      All requests made by a user with this permission will be automatically approved.
        * `request-advanced` - Grant permission to modify advanced media request options.
        * `request-view` - Grant permission to view media requests submitted by other users.
        * `recent-view` - Grant permission to view the list of recently added media.
        * `watchlist-view` - Grant permission to view other users' Plex Watchlists.
    * `request` - Grant permission to submit requests for non-4K media.
        * `request-movie` - Grant permission to submit requests for non-4K movies.
        * `request-series` - Grant permission to submit requests for non-4K series.
    * `auto-approve` - Grant automatic approval for all non-4K media requests.
        * `auto-approve-movie` - Grant automatic approval for non-4K movie requests.
        * `auto-approve-series` - Grant automatic approval for non-4K series requests.
    * `auto-request` - Grant permission to automatically submit requests for non-4K media
      via Plex Watchlist.
        * `auto-request-movie` - Grant permission to automatically submit requests
          for non-4K movies via Plex Watchlist.
        * `auto-request-series` - Grant permission to automatically submit requests
          for non-4K series via Plex Watchlist.
    * `request-4k` - Grant permission to submit requests for 4K media.
        * `request-4k-movie` - Grant permission to submit requests for 4K movies.
        * `request-4k-series` - Grant permission to submit requests for 4K series.
    * `auto-approve-4k` - Grant automatic approval for all 4K media requests.
        * `auto-approve-4k-movie` - Grant automatic approval for 4K movie requests.
        * `auto-approve-4k-series` - Grant automatic approval for 4K series requests.
    * `manage-issues` - Grant permission to manage media issues.
        * `view-issues` - Grant permission to report media issues.
        * `create-issues` - Grant permission to view media issues reported by other users.
    """

    @validator("default_permissions")
    def reduce_default_permissions(cls, value: Set[Permission]) -> Set[Permission]:
        return Permission.set_reduce(value)

    @classmethod
    def _get_remote_map(cls) -> List[RemoteMapEntry]:
        return [
            ("enable_local_signin", "localLogin", {}),
            ("enable_new_jellyfin_signin", "newPlexLogin", {}),
            ("global_movie_request_limit", "movieQuotaLimit", {}),
            ("global_movie_request_days", "movieQuotaDays", {}),
            ("global_series_request_limit", "tvQuotaLimit", {}),
            ("global_series_request_days", "tvQuotaDays", {}),
            (
                "default_permissions",
                "defaultPermissions",
                {
                    "decoder": lambda v: Permission.set_decoder(v),
                    "encoder": lambda v: Permission.set_encoder(v),
                },
            ),
        ]

    @classmethod
    def from_remote(cls, secrets: JellyseerrSecrets) -> Self:
        remote_attrs = api_get(secrets, "/api/v1/settings/main")
        default_quotas: Dict[str, Dict[str, int]] = remote_attrs["defaultQuotas"]
        del remote_attrs["defaultQuotas"]
        for category, local_category in (("movie", "movie"), ("tv", "series")):
            remote_attrs[f"{category}QuotaLimit"] = default_quotas[category].get(
                "quotaLimit",
                cls.__fields__[f"global_{local_category}_request_limit"].default,
            )
            remote_attrs[f"{category}QuotaDays"] = default_quotas[category].get(
                "quotaDays",
                cls.__fields__[f"global_{local_category}_request_days"].default,
            )
        return cls(
            **cls.get_local_attrs(cls._get_remote_map(), remote_attrs),
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
            self._get_remote_map(),
            check_unmanaged=check_unmanaged,
            set_unchanged=True,
        )
        remote_attrs["defaultQuotas"] = {
            category: {
                "quotaLimit": remote_attrs[f"{category}QuotaLimit"],
                "quotaDays": remote_attrs[f"{category}QuotaDays"],
            }
            for category in ("movie", "tv")
        }
        for category in ("movie", "tv"):
            del remote_attrs[f"{category}QuotaLimit"]
            del remote_attrs[f"{category}QuotaDays"]
        if changed:
            api_post(
                secrets,
                "/api/v1/settings/main",
                remote_attrs,
                expected_status_code=HTTPStatus.OK,
            )
            return True
        return False
