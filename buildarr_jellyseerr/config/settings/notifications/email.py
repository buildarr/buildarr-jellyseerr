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
from pydantic import EmailStr, SecretStr

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
    Send notification emails via an SMTP server.

    In order for Jellyseerr to send emails to Jellyseerr users, an SMTP server
    needs to be configured here.

    !!! note

        If the [`jellyseerr.settings.general.application_url`](
        ../general/#buildarr_jellyseerr.config.settings.general
        .JellyseerrGeneralSettings.application_url
        ) attribute is configured, Jellyseerr will explicitly
        set the origin server hostname when connecting to the SMTP host.
    """

    require_user_email: bool = False
    """
    Require Jellyseerr users to have an email address configured, so emails can be sent to it.
    """

    sender_name: Optional[str] = "Jellyseerr"
    """
    Configure a friendly name for the email sender.
    """

    sender_address: Optional[EmailStr] = None
    """
    The `From` email address to send the email as.

    If sending email to public mailboxes, this should be set to an email address
    owned/controlled by the server being used to send the mail.

    **Required if email notifications are enabled.**
    """

    smtp_host: Optional[str] = None
    """
    The SMTP server to sent mail from.

    **Required if email notifications are enabled.**
    """

    encryption_method: EncryptionMethod = EncryptionMethod.starttls_prefer
    """
    The encryption method to use to communicate with the SMTP server.

    Values (in order of security):

    * `smtps` - Implicit TLS (SMTPS)
    * `starttls-strict` - Require STARTTLS
    * `starttls-prefer` - Use STARTTLS if available, unencrypted fallback (**not recommended**)
    * `none` - No encryption (**not recommended**)

    !!! warning

        The `starttls-prefer` and `none` encryption methods send (or can send)
        username and password credentials unencrypted over the network.

        **Do not use them unless you know what you are doing.**
    """

    smtp_port: Port = 587  # type: ignore[assignment]
    """
    The mail submission port of the SMTP server.

    The default is the standard SMTP submission port, used for STARTTLS.
    If using implicit TLS (SMTPS), this should be set to the standard port of `465`.
    """

    allow_selfsigned_certificates: bool = False
    """
    Allow self-signed certificates for the SMTP server host certificate.

    !!! warning

        Generally this option shouldn't be enabled, even on a private mail server,
        as any mail server can get free TLS certificates using services such as
        [Let's Encrypt](https://letsencrypt.org).

        **Never enable this option when using a public email service.**
    """

    smtp_username: Optional[str] = None
    """
    SMTP server username, if required (which is usually the case).
    """

    smtp_password: Optional[SecretStr] = None
    """
    SMTP server user password, if required (which is usually the case).
    """

    pgp_private_key: Optional[SecretStr] = None
    """
    An optional PGP private key to use to sign (and if configured by users, encrypt) sent emails.

    When configuring the PGP keys, be sure to keep the entire contents of the key intact.
    For example, private keys always begin with `-----BEGIN PGP PRIVATE KEY BLOCK-----`
    and end with `-----END PGP PRIVATE KEY BLOCK-----`.
    """

    pgp_password: Optional[SecretStr] = None
    """
    An optional password for unlocking the PGP private key.
    """

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
                {
                    "optional": True,
                    "decoder": lambda v: v or None,
                    "encoder": lambda v: v.get_secret_value() if v else "",
                },
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
