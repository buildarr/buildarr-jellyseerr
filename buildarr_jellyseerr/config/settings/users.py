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

from typing import Iterable, List, Mapping, Set

from buildarr.config import RemoteMapEntry
from buildarr.types import BaseIntEnum
from pydantic import Field, validator
from typing_extensions import Self

from ...api import api_get, api_post
from ...secrets import JellyseerrSecrets
from ..types import JellyseerrConfigBase


class Permission(BaseIntEnum):
    none = 0
    admin = 2
    manage_settings = 4
    manage_users = 8
    manage_requests = 16
    request = 32
    vote = 64
    auto_approve = 128
    auto_approve_movie = 256
    auto_approve_tv = 512
    request_4k = 1024
    request_4k_movie = 2048
    request_4k_tv = 4096
    request_advanced = 8192
    request_view = 16384
    auto_approve_4k = 32768
    auto_approve_4k_movie = 65536
    auto_approve_4k_tv = 131072
    request_movie = 262144
    request_tv = 524288
    manage_issues = 1048576
    view_issues = 2097152
    create_issues = 4194304
    auto_request = 8388608
    auto_request_movie = 16777216
    auto_request_tv = 33554432
    recent_view = 67108864
    watchlist_view = 134217728

    @classmethod
    def set_reduce(cls, permissions: Iterable[Permission]) -> Set[Permission]:
        return cls.set_decoder(cls.set_encoder(permissions))

    @classmethod
    def set_decoder(cls, permissions_encoded: int) -> Set[Permission]:
        #
        if not permissions_encoded:
            return {cls.none}
        if permissions_encoded & cls.admin:
            return {cls.admin}
        #
        permissions: Set[Permission] = set()
        #
        if permissions_encoded & cls.manage_users:
            permissions.add(cls.manage_users)
        #
        if permissions_encoded & cls.manage_issues:
            permissions.add(cls.manage_issues)
        else:
            for permission in (cls.create_issues, cls.view_issues):
                if permissions_encoded & permission:
                    permissions.add(permission)
        #
        if permissions_encoded & cls.manage_requests:
            permissions.add(cls.manage_requests)
        else:
            for permission in (
                cls.request_advanced,
                cls.request_view,
                cls.recent_view,
                cls.watchlist_view,
            ):
                if permissions_encoded & permission:
                    permissions.add(permission)
        #
        if permissions_encoded & cls.request:
            permissions.add(cls.request)
        else:
            for permission in (cls.request_movie, cls.request_tv):
                if permissions_encoded & permission:
                    permissions.add(permission)
        #
        if permissions_encoded & cls.request_4k:
            permissions.add(cls.request_4k)
        else:
            for permission in (cls.request_4k_movie, cls.request_4k_tv):
                if permissions_encoded & permission:
                    permissions.add(permission)
        #
        if permissions_encoded & cls.auto_request:
            if cls.request not in permissions:
                cls._permission_error(cls.auto_request, cls.request)
            permissions.add(cls.auto_request)
        else:
            if permissions_encoded & cls.auto_request_movie:
                if cls.request not in permissions or cls.request_movie not in permissions:
                    cls._permission_error(cls.auto_request_movie, cls.request_movie)
                permissions.add(cls.auto_request_movie)
            if permissions_encoded & cls.auto_request_tv:
                if cls.request not in permissions or cls.request_tv not in permissions:
                    cls._permission_error(cls.auto_request_tv, cls.request_tv)
                permissions.add(cls.auto_request_tv)
        #
        if permissions_encoded & cls.auto_approve:
            if cls.request not in permissions:
                cls._permission_error(cls.auto_approve, cls.request)
            permissions.add(cls.auto_approve)
        else:
            if permissions_encoded & cls.auto_approve_movie:
                if cls.request not in permissions or cls.request_movie not in permissions:
                    cls._permission_error(cls.auto_approve_movie, cls.request_movie)
                permissions.add(cls.auto_approve_movie)
            if permissions_encoded & cls.auto_approve_tv:
                if cls.request not in permissions or cls.request_tv not in permissions:
                    cls._permission_error(cls.auto_approve_tv, cls.request_tv)
                permissions.add(cls.auto_approve_tv)
        #
        if permissions_encoded & cls.auto_approve_4k:
            if cls.request_4k not in permissions:
                cls._permission_error(cls.auto_approve_4k, cls.request_4k)
            permissions.add(cls.auto_approve_4k)
        else:
            if permissions_encoded & cls.auto_approve_4k_movie:
                if cls.request_4k not in permissions or cls.request_4k_movie not in permissions:
                    cls._permission_error(cls.auto_approve_4k_movie, cls.request_4k_movie)
                permissions.add(cls.auto_approve_4k_movie)
            if permissions_encoded & cls.auto_approve_4k_tv:
                if cls.request_4k not in permissions or cls.request_4k_tv not in permissions:
                    cls._permission_error(cls.auto_approve_4k_tv, cls.request_4k_tv)
                permissions.add(cls.auto_approve_4k_tv)
        #
        return permissions

    @classmethod
    def _permission_error(cls, permission: Permission, required_permission: Permission) -> None:
        raise ValueError(
            f"permission '{permission.to_name_str()}' "
            f"requires unset permission '{required_permission.to_name_str()}'",
        )

    @classmethod
    def set_encoder(cls, permissions: Iterable[Permission]) -> int:
        return functools.reduce(operator.ior, permissions, 0)


class JellyseerrUsersSettings(JellyseerrConfigBase):
    """
    Jellyseerr users settings.
    """

    enable_local_signin: bool = True

    enable_new_jellyfin_signin: bool = True

    global_movie_request_limit: int = Field(None, ge=0)
    """
    0 is unlimited.
    """

    global_series_request_limit: int = Field(None, ge=0)
    """
    0 is unlimited.
    """

    default_permissions: Set[Permission] = {Permission.request, Permission.manage_issues}
    """
    Get permission names from API schema (no camelCase)
    """

    @validator("default_permissions")
    def reduce_default_permissions(cls, value: Set[Permission]) -> Set[Permission]:
        return Permission.set_reduce(value)

    @classmethod
    def _get_remote_map(
        cls,
        movie_quota_days: int = 0,
        series_quota_days: int = 0,
    ) -> List[RemoteMapEntry]:
        return [
            ("enable_local_signin", "localLogin", {}),
            ("enable_new_jellyfin_signin", "newPlexLogin", {}),
            (
                "global_movie_request_limit",
                "defaultQuotas",
                {
                    "decoder": lambda v: v["movie"]["quotaLimit"],
                    "root_encoder": lambda vs: {
                        "movie": {
                            "quotaDays": movie_quota_days,
                            "quotaLimit": vs.global_movie_request_limit,
                        },
                        "tv": {
                            "quotaDays": series_quota_days,
                            "quotaLimit": vs.global_series_request_limit,
                        },
                    },
                },
            ),
            (
                "global_series_request_limit",
                "defaultQuotas",
                {
                    "decoder": lambda v: v["tv"]["quotaLimit"],
                    "root_encoder": lambda vs: {
                        "movie": {
                            "quotaDays": movie_quota_days,
                            "quotaLimit": vs.global_movie_request_limit,
                        },
                        "tv": {
                            "quotaDays": series_quota_days,
                            "quotaLimit": vs.global_series_request_limit,
                        },
                    },
                },
            ),
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
        return cls(
            **cls.get_local_attrs(cls._get_remote_map(), api_get(secrets, "/api/v1/settings/main")),
        )

    def update_remote(
        self,
        tree: str,
        secrets: JellyseerrSecrets,
        remote: Self,
        check_unmanaged: bool = False,
    ) -> bool:
        default_quotas: Mapping[str, Mapping[str, int]] = api_get(
            secrets,
            "/api/v1/settings/main",
        )["defaultQuotas"]
        changed, remote_attrs = self.get_update_remote_attrs(
            tree,
            remote,
            self._get_remote_map(
                movie_quota_days=default_quotas["movie"]["quotaDays"],
                series_quota_days=default_quotas["tv"]["quotaDays"],
            ),
            check_unmanaged=check_unmanaged,
        )
        if changed:
            api_post(secrets, "/api/v1/settings/main", remote_attrs)
            return True
        return False
