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
Jellyseerr plugin email notifications settings configuration.
"""


from __future__ import annotations

from typing import Dict, List, Optional, Set

from buildarr.config import RemoteMapEntry
from buildarr.types import BaseEnum, Port
from pydantic import EmailStr, Field, SecretStr

from .base import NotificationsSettingsBase


class EncryptionMethod(BaseEnum):
    none = "unencrypted"
    smtps = "implicit-tls"
    starttls_prefer = "starttls-optional"
    starttls_strict = "starttls-enforce"

    @property
    def secure(self) -> bool:
        return self is EncryptionMethod.smtps

    @property
    def ignore_tls(self) -> bool:
        return self is EncryptionMethod.none

    @property
    def require_tls(self) -> bool:
        return self is EncryptionMethod.starttls_strict

    @classmethod
    def decode(cls, secure: bool, ignore_tls: bool, require_tls: bool) -> EncryptionMethod:
        for value in cls:
            if (value.secure, value.ignore_tls, value.require_tls) == (
                secure,
                ignore_tls,
                require_tls,
            ):
                return value
        raise RuntimeError(f"Invalid input combination: {secure=}, {ignore_tls=}, {require_tls=}")

    def encode(self) -> Dict[str, bool]:
        return {"secure": self.secure, "ignoreTls": self.ignore_tls, "requireTls": self.require_tls}


class EmailSettings(NotificationsSettingsBase):
    """
    Jellyseerr email notifications settings.
    """

    require_user_email: bool = Field(False, alias="user_email_required")

    sender_name: Optional[str] = None

    sender_address: Optional[EmailStr] = None

    smtp_host: Optional[str] = None

    smtp_port: Port = 587  # type: ignore[assignment]

    encryption_method: EncryptionMethod = EncryptionMethod.starttls_prefer

    allow_selfsigned_certificates: bool = Field(False, alias="self_signed_certificates")

    smtp_username: Optional[str] = Field(None, alias="smtp_user")

    smtp_password: Optional[SecretStr] = Field(None, alias="smtp_pass")

    pgp_private_key: Optional[SecretStr] = Field(None, alias="pgp_key")

    pgp_password: Optional[SecretStr] = Field(None, alias="pgp_pass")

    _type: str = "email"
    _required_if_enabled: Set[str] = {"sender_name", "sender_address", "smtp_host"}

    @classmethod
    def _get_remote_map(cls) -> List[RemoteMapEntry]:
        return [
            (
                "require_user_email",
                "userEmailRequired",
                # In some cases it this appears to not in the output,
                # but the default value is `False`.
                {"optional": True},
            ),
            (
                "sender_name",
                "senderName",
                {"decoder": lambda v: v or None, "encoder": lambda v: v or ""},
            ),
            (
                "sender_address",
                "emailFrom",
                {"decoder": lambda v: v or None, "encoder": lambda v: v or ""},
            ),
            (
                "smtp_host",
                "smtpHost",
                {"decoder": lambda v: v or None, "encoder": lambda v: v or ""},
            ),
            ("smtp_port", "smtpPort", {}),
            # `encryption_method` is the aggregation of `secure`, `ignoreTls` and `requireTls`.
            (
                "encryption_method",
                "secure",
                {
                    "root_decoder": lambda vs: EncryptionMethod.decode(
                        secure=vs["secure"],
                        ignore_tls=vs["ignoreTls"],
                        require_tls=vs["requireTls"],
                    ),
                    "encoder": lambda v: v.secure,
                },
            ),
            (
                "encryption_method",
                "ignoreTls",
                {
                    "root_decoder": lambda vs: EncryptionMethod.decode(
                        secure=vs["secure"],
                        ignore_tls=vs["ignoreTls"],
                        require_tls=vs["requireTls"],
                    ),
                    "encoder": lambda v: v.ignore_tls,
                },
            ),
            (
                "encryption_method",
                "requireTls",
                {
                    "root_decoder": lambda vs: EncryptionMethod.decode(
                        secure=vs["secure"],
                        ignore_tls=vs["ignoreTls"],
                        require_tls=vs["requireTls"],
                    ),
                    "encoder": lambda v: v.require_tls,
                },
            ),
            ("allow_selfsigned_certificates", "allowSelfSigned", {}),
            (
                "smtp_username",
                "authUser",
                {"optional": True, "decoder": lambda v: v or None, "encoder": lambda v: v or ""},
            ),
            (
                "smtp_password",
                "authPass",
                {"optional": True, "decoder": lambda v: v or None, "encoder": lambda v: v or ""},
            ),
            (
                "pgp_private_key",
                "pgpPrivateKey",
                {
                    "optional": True,
                    "decoder": lambda v: v or None,
                    "encoder": lambda v: v.get_secret_value() if v else "",
                },
            ),
            (
                "pgp_password",
                "pgpPassword",
                {
                    "optional": True,
                    "decoder": lambda v: v or None,
                    "encoder": lambda v: v.get_secret_value() if v else "",
                },
            ),
        ]
