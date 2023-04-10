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
    NONE = 0
    ADMIN = 2
    MANAGE_SETTINGS = 4
    MANAGE_USERS = 8
    MANAGE_REQUESTS = 16
    REQUEST = 32
    VOTE = 64
    AUTO_APPROVE = 128
    AUTO_APPROVE_MOVIE = 256
    AUTO_APPROVE_TV = 512
    REQUEST_4K = 1024
    REQUEST_4K_MOVIE = 2048
    REQUEST_4K_TV = 4096
    REQUEST_ADVANCED = 8192
    REQUEST_VIEW = 16384
    AUTO_APPROVE_4K = 32768
    AUTO_APPROVE_4K_MOVIE = 65536
    AUTO_APPROVE_4K_TV = 131072
    REQUEST_MOVIE = 262144
    REQUEST_TV = 524288
    MANAGE_ISSUES = 1048576
    VIEW_ISSUES = 2097152
    CREATE_ISSUES = 4194304
    AUTO_REQUEST = 8388608
    AUTO_REQUEST_MOVIE = 16777216
    AUTO_REQUEST_TV = 33554432
    RECENT_VIEW = 67108864
    WATCHLIST_VIEW = 134217728

    @classmethod
    def set_reduce(cls, permissions: Iterable[Permission]) -> Set[Permission]:
        return cls.set_decoder(cls.set_encoder(permissions))

    @classmethod
    def set_decoder(cls, permissions_encoded: int) -> Set[Permission]:
        #
        if not permissions_encoded:
            return {cls.NONE}
        if permissions_encoded & cls.ADMIN:
            return {cls.ADMIN}
        #
        permissions: Set[Permission] = set()
        #
        if permissions_encoded & cls.MANAGE_USERS:
            permissions.add(cls.MANAGE_USERS)
        #
        if permissions_encoded & cls.MANAGE_ISSUES:
            permissions.add(cls.MANAGE_ISSUES)
        else:
            for permission in (cls.CREATE_ISSUES, cls.VIEW_ISSUES):
                if permissions_encoded & permission:
                    permissions.add(permission)
        #
        if permissions_encoded & cls.MANAGE_REQUESTS:
            permissions.add(cls.MANAGE_REQUESTS)
        else:
            for permission in (
                cls.REQUEST_ADVANCED,
                cls.REQUEST_VIEW,
                cls.RECENT_VIEW,
                cls.WATCHLIST_VIEW,
            ):
                if permissions_encoded & permission:
                    permissions.add(permission)
        #
        if permissions_encoded & cls.REQUEST:
            permissions.add(cls.REQUEST)
        else:
            for permission in (cls.REQUEST_MOVIE, cls.REQUEST_TV):
                if permissions_encoded & permission:
                    permissions.add(permission)
        #
        if permissions_encoded & cls.REQUEST_4K:
            permissions.add(cls.REQUEST_4K)
        else:
            for permission in (cls.REQUEST_4K_MOVIE, cls.REQUEST_4K_TV):
                if permissions_encoded & permission:
                    permissions.add(permission)
        #
        if permissions_encoded & cls.AUTO_REQUEST:
            if cls.REQUEST not in permissions:
                cls._permission_error(cls.AUTO_REQUEST, cls.REQUEST)
            permissions.add(cls.AUTO_REQUEST)
        else:
            if permissions_encoded & cls.AUTO_REQUEST_MOVIE:
                if cls.REQUEST not in permissions or cls.REQUEST_MOVIE not in permissions:
                    cls._permission_error(cls.AUTO_REQUEST_MOVIE, cls.REQUEST_MOVIE)
                permissions.add(cls.AUTO_REQUEST_MOVIE)
            if permissions_encoded & cls.AUTO_REQUEST_TV:
                if cls.REQUEST not in permissions or cls.REQUEST_TV not in permissions:
                    cls._permission_error(cls.AUTO_REQUEST_MOVIE, cls.REQUEST_TV)
                permissions.add(cls.AUTO_REQUEST_TV)
        #
        if permissions_encoded & cls.AUTO_APPROVE:
            if cls.REQUEST not in permissions:
                cls._permission_error(cls.AUTO_APPROVE, cls.REQUEST)
            permissions.add(cls.AUTO_APPROVE)
        else:
            if permissions_encoded & cls.AUTO_APPROVE_MOVIE:
                if cls.REQUEST not in permissions or cls.REQUEST_MOVIE not in permissions:
                    cls._permission_error(cls.AUTO_APPROVE_MOVIE, cls.REQUEST_MOVIE)
                permissions.add(cls.AUTO_APPROVE_MOVIE)
            if permissions_encoded & cls.AUTO_APPROVE_TV:
                if cls.REQUEST not in permissions or cls.REQUEST_TV not in permissions:
                    cls._permission_error(cls.AUTO_APPROVE_MOVIE, cls.REQUEST_TV)
                permissions.add(cls.AUTO_APPROVE_TV)
        #
        if permissions_encoded & cls.AUTO_APPROVE_4K:
            if cls.REQUEST_4K not in permissions:
                cls._permission_error(cls.AUTO_APPROVE_4K, cls.REQUEST_4K)
            permissions.add(cls.AUTO_APPROVE_4K)
        else:
            if permissions_encoded & cls.AUTO_APPROVE_4K_MOVIE:
                if cls.REQUEST_4K not in permissions or cls.REQUEST_4K_MOVIE not in permissions:
                    cls._permission_error(cls.AUTO_APPROVE_4K_MOVIE, cls.REQUEST_4K_MOVIE)
                permissions.add(cls.AUTO_APPROVE_4K_MOVIE)
            if permissions_encoded & cls.AUTO_APPROVE_4K_TV:
                if cls.REQUEST_4K not in permissions or cls.REQUEST_4K_TV not in permissions:
                    cls._permission_error(cls.AUTO_APPROVE_4K_MOVIE, cls.REQUEST_4K_TV)
                permissions.add(cls.AUTO_APPROVE_4K_TV)
        #
        return permissions

    @classmethod
    def _permission_error(cls, permission: Permission, required_permission: Permission) -> None:
        raise ValueError(
            f"permission '{permission.name}' "
            f"requires unset permission '{required_permission.name}'",
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

    default_permissions: Set[Permission] = {Permission.REQUEST, Permission.MANAGE_ISSUES}
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
