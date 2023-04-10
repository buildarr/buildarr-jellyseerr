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
Prowlarr plugin notification connection configuration.
"""


from __future__ import annotations

from logging import getLogger
from typing import Any, Dict, List, Literal, Mapping, Optional, Set, Tuple, Type, Union

import prowlarr

from buildarr.config import RemoteMapEntry
from buildarr.types import BaseEnum, BaseIntEnum, NonEmptyStr, Password, Port
from pydantic import AnyHttpUrl, ConstrainedInt, Field, NameEmail, SecretStr
from typing_extensions import Annotated, Self

from ...api import prowlarr_api_client
from ...secrets import ProwlarrSecrets
from ..types import ProwlarrConfigBase

logger = getLogger(__name__)


class OnGrabField(BaseIntEnum):
    """
    Values for `on_grab_fields` for the Discord connection.
    """

    overview = 0
    rating = 1
    genres = 2
    quality = 3
    group = 4
    size = 5
    links = 6
    release = 7
    poster = 8
    fanart = 9


class OnImportField(BaseIntEnum):
    """
    Values for `on_import_fields` for the Discord connection.
    """

    overview = 0
    rating = 1
    genres = 2
    quality = 3
    codecs = 4
    group = 5
    size = 6
    languages = 7
    subtitles = 8
    links = 9
    release = 10
    poster = 11
    fanart = 12


class GotifyPriority(BaseEnum):
    """
    Gotify notification priority.
    """

    min = 0
    low = 2
    normal = 5
    high = 8


class JoinPriority(BaseEnum):
    """
    Join notification priority.
    """

    silent = -2
    quiet = -1
    normal = 0
    high = 1
    emergency = 2


class NtfyshPriority(BaseIntEnum):
    min = 1
    low = 2
    default = 3
    high = 4
    max = 5


class ProwlPriority(BaseEnum):
    """
    Prowl notification priority.
    """

    verylow = -2
    low = -1
    normal = 0
    high = 1
    emergency = 2


class PushoverPriority(BaseEnum):
    """
    Pushover notification priority.
    """

    silent = -2
    quiet = -1
    normal = 0
    high = 1
    emergency = 2


class PushoverRetry(ConstrainedInt):
    """
    Constrained integer type to enforce Pushover retry field limits.
    """

    ge = 30


class WebhookMethod(BaseEnum):
    """
    HTTP method to use on a webhook connection.
    """

    POST = 1
    PUT = 2


class NotificationTriggers(ProwlarrConfigBase):
    """
    Notification connections are configured using the following syntax.

    ```yaml
    prowlarr:
      settings:
        notifications:
          delete_unmanaged: false # Optional
          definitions:
            Email: # Name of notification connection in Prowlarr.
              type: "email" # Required
              notification_triggers: # When to send notifications.
                on_health_issue: true
                include_health_warnings: false # Do not send on just warnings.
                on_application_update: true
              tags: # Tags can also be assigned to connections.
                - "example"
              # Connection-specific parameters.
              server: "smtp.example.com"
              port: 465
              use_encryption: true
              username: "prowlarr"
              password: "fake-password"
              from_address: "prowlarr@example.com"
              recipient_addresses:
                - "admin@example.com"
            # Add additional connections here.
    ```

    A `type` attribute must be defined so Buildarr knows what type of connection to make.
    Each connection has a unique value for `type` documented below.

    The triggers enabled on a connection are defined under `notification_triggers`.
    Tags can be assigned to connections, to only allow notifications relating
    to media under those tags.

    The `delete_unmanaged` flag on the outer `connect` block can be set
    to remove connections not defined in Buildarr.
    Take care when using this option, as it can remove connections
    automatically managed by other applications.

    The following notification triggers can be enabled.
    Some connection types only allow a subset of these to be enabled,
    check the documentation the specific connection type for more information.
    """

    on_health_issue: bool = False
    """
    Be notified on health check failures.
    """

    include_health_warnings: bool = False
    """
    Be notified on health warnings in addition to errors.

    Requires `on_health_issue` to be enabled to have any effect.
    """

    on_application_update: bool = False
    """
    Be notified when Prowlarr gets updated to a new version.
    """

    _remote_map: List[RemoteMapEntry] = [
        ("on_health_issue", "onHealthIssue", {}),
        ("include_health_warnings", "includeHealthWarnings", {}),
        ("on_application_update", "onApplicationUpdate", {}),
    ]


class Notification(ProwlarrConfigBase):
    """
    Base class for a Prowlarr notification connection.
    """

    notification_triggers: NotificationTriggers = NotificationTriggers()
    """
    Notification triggers to enable on this notification connection.
    """

    tags: List[NonEmptyStr] = []
    """
    Prowlarr tags to associate this notification connection with.
    """

    _implementation: str
    _remote_map: List[RemoteMapEntry]

    @classmethod
    def _get_base_remote_map(
        cls,
        tag_ids: Mapping[str, int],
    ) -> List[RemoteMapEntry]:
        return [
            (
                "tags",
                "tags",
                {
                    "decoder": lambda v: set(
                        (tag for tag, tag_id in tag_ids.items() if tag_id in v),
                    ),
                    "encoder": lambda v: sorted(tag_ids[tag] for tag in v),
                },
            ),
        ]

    @classmethod
    def _from_remote(cls, tag_ids: Mapping[str, int], remote_attrs: Mapping[str, Any]) -> Self:
        return cls(
            notification_triggers=NotificationTriggers(
                **NotificationTriggers.get_local_attrs(
                    remote_map=NotificationTriggers._remote_map,
                    remote_attrs=remote_attrs,
                ),
            ),
            **cls.get_local_attrs(
                remote_map=cls._get_base_remote_map(tag_ids) + cls._remote_map,
                remote_attrs=remote_attrs,
            ),
        )

    def _get_api_schema(self, schemas: List[prowlarr.NotificationResource]) -> Dict[str, Any]:
        return {
            k: v
            for k, v in next(
                s for s in schemas if s.implementation.lower() == self._implementation.lower()
            )
            .to_dict()
            .items()
            if k not in ["id", "name"]
        }

    def _create_remote(
        self,
        tree: str,
        secrets: ProwlarrSecrets,
        api_notification_schemas: List[prowlarr.NotificationResource],
        tag_ids: Mapping[str, int],
        notification_name: str,
    ) -> None:
        api_schema = self._get_api_schema(api_notification_schemas)
        set_attrs = {
            **self.notification_triggers.get_create_remote_attrs(
                tree=f"{tree}.notification_triggers",
                remote_map=self.notification_triggers._remote_map,
            ),
            **self.get_create_remote_attrs(
                tree=tree,
                remote_map=self._get_base_remote_map(tag_ids) + self._remote_map,
            ),
        }
        field_values: Dict[str, Any] = {
            field["name"]: field["value"] for field in set_attrs["fields"]
        }
        set_attrs["fields"] = [
            ({**f, "value": field_values[f["name"]]} if f["name"] in field_values else f)
            for f in api_schema["fields"]
        ]
        remote_attrs = {"name": notification_name, **api_schema, **set_attrs}
        with prowlarr_api_client(secrets=secrets) as api_client:
            prowlarr.NotificationApi(api_client).create_notification(
                notification_resource=prowlarr.NotificationResource.from_dict(remote_attrs),
            )

    def _update_remote(
        self,
        tree: str,
        secrets: ProwlarrSecrets,
        remote: Self,
        api_notification_schemas: List[prowlarr.NotificationResource],
        tag_ids: Mapping[str, int],
        api_notification: prowlarr.NotificationResource,
    ) -> bool:
        (
            triggers_updated,
            updated_triggers_attrs,
        ) = self.notification_triggers.get_update_remote_attrs(
            tree=tree,
            remote=remote.notification_triggers,
            remote_map=self.notification_triggers._remote_map,
        )
        base_updated, updated_base_attrs = self.get_update_remote_attrs(
            tree=tree,
            remote=remote,
            remote_map=self._get_base_remote_map(tag_ids) + self._remote_map,
        )
        if triggers_updated or base_updated:
            api_schema = self._get_api_schema(api_notification_schemas)
            api_notification_dict = api_notification.to_dict()
            updated_attrs = {**updated_triggers_attrs, **updated_base_attrs}
            if "fields" in updated_attrs:
                updated_field_values: Dict[str, Any] = {
                    field["name"]: field["value"] for field in updated_attrs["fields"]
                }
                remote_fields: Dict[str, Dict[str, Any]] = {
                    field["name"]: field for field in api_notification_dict["fields"]
                }
                updated_attrs["fields"] = [
                    (
                        {
                            **remote_fields[f["name"]],
                            "value": updated_field_values[f["name"]],
                        }
                        if f["name"] in updated_field_values
                        else remote_fields[f["name"]]
                    )
                    for f in api_schema["fields"]
                ]
            remote_attrs = {**api_notification_dict, **updated_attrs}
            with prowlarr_api_client(secrets=secrets) as api_client:
                prowlarr.NotificationApi(api_client).update_notification(
                    id=str(api_notification.id),
                    notification_resource=prowlarr.NotificationResource.from_dict(remote_attrs),
                )
            return True
        return False

    def _delete_remote(self, tree: str, secrets: ProwlarrSecrets, notification_id: int) -> None:
        logger.info("%s: (...) -> (deleted)", tree)
        with prowlarr_api_client(secrets=secrets) as api_client:
            prowlarr.NotificationApi(api_client).delete_notification(id=notification_id)


class AppriseNotification(Notification):
    """
    Receive media update and health alert push notifications via an Apprise server.
    """

    type: Literal["apprise"] = "apprise"
    """
    Type value associated with this kind of connection.
    """

    base_url: AnyHttpUrl
    """
    Apprise server base URL, including `http[s]://` and port if needed.
    """

    configuration_key: Optional[SecretStr] = None
    """
    Configuration key for the Persistent Storage Solution.

    Leave empty if Stateless URLs are used.
    """

    stateless_urls: Set[AnyHttpUrl] = set()
    """
    One or more URLs where notifications should be sent to.

    Leave undefined or empty if Persistent Storage is used.
    """

    apprise_tags: Set[NonEmptyStr] = set()
    """
    Optionally notify only targets with the defined tags.
    """

    auth_username: Optional[str] = None
    """
    Username for authenticating with Apprise, if required.
    """

    auth_password: Optional[SecretStr] = None
    """
    Password for authenticating with Apprise, if required.
    """

    _implementation: str = "Apprise"
    _remote_map: List[RemoteMapEntry] = [
        ("base_url", "baseUrl", {"is_field": True}),
        (
            "configuration_key",
            "configurationKey",
            {
                "is_field": True,
                "decoder": lambda v: SecretStr(v) if v else None,
                "encoder": lambda v: v.get_secret_value() if v else "",
            },
        ),
        (
            "stateless_urls",
            "statelessUrls",
            {
                "is_field": True,
                "decoder": lambda v: set(url.strip() for url in "".split(",") if url.strip()),
                "encoder": lambda v: ",".join(sorted(str(url) for url in v)),
            },
        ),
        (
            "apprise_tags",
            "tags",
            {"is_field": True, "encoder": lambda v: sorted(v)},
        ),
        (
            "auth_username",
            "authUsername",
            {"is_field": True, "decoder": lambda v: v or None, "encoder": lambda v: v or ""},
        ),
        (
            "auth_password",
            "authPassword",
            {
                "is_field": True,
                "decoder": lambda v: SecretStr(v) if v else None,
                "encoder": lambda v: v.get_secret_value() if v else "",
            },
        ),
    ]


class BoxcarNotification(Notification):
    """
    Receive media update and health alert push notifications via Boxcar.
    """

    type: Literal["boxcar"] = "boxcar"
    """
    Type value associated with this kind of connection.
    """

    access_token: Password
    """
    Access token for authenticating with Boxcar.
    """

    _implementation: str = "Boxcar"
    _remote_map: List[RemoteMapEntry] = [("access_token", "token", {"is_field": True})]


class CustomscriptNotification(Notification):
    """
    Execute a local script on the Prowlarr instance when events occur.
    """

    type: Literal["customscript"] = "customscript"
    """
    Type value associated with this kind of connection.
    """

    path: NonEmptyStr
    """
    Path of the script to execute.
    """

    _implementation: str = "CustomScript"
    _remote_map: List[RemoteMapEntry] = [("path", "path", {"is_field": True})]


class DiscordNotification(Notification):
    """
    Send media update and health alert messages to a Discord server.
    """

    type: Literal["discord"] = "discord"
    """
    Type value associated with this kind of connection.
    """

    webhook_url: AnyHttpUrl
    """
    Discord server webhook URL.
    """

    username: Optional[str] = None
    """
    The username to post as.

    If unset, blank or set to `None`, use the default username set to the webhook URL.
    """

    avatar: Optional[str] = None
    """
    Change the avatar that is used for messages from this connection.

    If unset, blank or set to `None`, use the default avatar for the user.
    """

    # Name override, None -> use machine_name
    host: Optional[str] = None
    """
    Override the host name that shows for this notification.

    If unset, blank or set to `None`, use the machine name.
    """

    on_grab_fields: Set[OnGrabField] = {
        OnGrabField.overview,
        OnGrabField.rating,
        OnGrabField.genres,
        OnGrabField.quality,
        OnGrabField.size,
        OnGrabField.links,
        OnGrabField.release,
        OnGrabField.poster,
        OnGrabField.fanart,
    }
    """
    Set the fields that are passed in for this 'on grab' notification.
    By default, all fields are passed in.

    Values:

    * `overview`
    * `rating`
    * `genres`
    * `quality`
    * `group`
    * `size`
    * `links`
    * `release`
    * `poster`
    * `fanart`

    Example:

    ```yaml
    ...
      connect:
        definitions:
          Discord:
            type: "discord"
            webhook_url: "https://..."
            on_grab_fields:
              - "overview"
              - "quality"
              - "release"
    ```
    """

    on_import_fields: Set[OnImportField] = {
        OnImportField.overview,
        OnImportField.rating,
        OnImportField.genres,
        OnImportField.quality,
        OnImportField.codecs,
        OnImportField.group,
        OnImportField.size,
        OnImportField.languages,
        OnImportField.subtitles,
        OnImportField.links,
        OnImportField.release,
        OnImportField.poster,
        OnImportField.fanart,
    }
    """
    Set the fields that are passed in for this 'on import' notification.
    By default, all fields are passed in.

    Values:

    * `overview`
    * `rating`
    * `genres`
    * `quality`
    * `codecs`
    * `group`
    * `size`
    * `languages`
    * `subtitles`
    * `links`
    * `release`
    * `poster`
    * `fanart`

    Example:

    ```yaml
    ...
      connect:
        definitions:
          Discord:
            type: "discord"
            webhook_url: "https://..."
            on_import_fields:
              - "overview"
              - "quality"
              - "release"
    ```
    """

    _implementation: str = "Discord"
    _remote_map: List[RemoteMapEntry] = [
        ("webhook_url", "webHookUrl", {"is_field": True}),
        (
            "username",
            "username",
            {"is_field": True, "decoder": lambda v: v or None, "encoder": lambda v: v or ""},
        ),
        (
            "avatar",
            "avatar",
            {"is_field": True, "decoder": lambda v: v or None, "encoder": lambda v: v or ""},
        ),
        (
            "host",
            "host",
            {"is_field": True, "decoder": lambda v: v or None, "encoder": lambda v: v or ""},
        ),
        (
            "on_grab_fields",
            "grabFields",
            {"is_field": True, "encoder": lambda v: sorted(f.value for f in v)},
        ),
        (
            "on_import_fields",
            "importFields",
            {"is_field": True, "encoder": lambda v: sorted(f.value for f in v)},
        ),
    ]


class EmailNotification(Notification):
    """
    Send media update and health alert messages to an email address.
    """

    type: Literal["email"] = "email"
    """
    Type value associated with this kind of connection.
    """

    server: NonEmptyStr
    """
    Hostname or IP address of the SMTP server to send outbound mail to.
    """

    port: Port = 587  # type: ignore[assignment]
    """
    The port number on the SMTP server to use to submit mail.

    The default is to use STARTTLS on the standard SMTP submission port.
    """

    use_encryption: bool = True
    """
    Whether or not to use encryption when sending mail to the SMTP server.

    If the port number is set to 465, SMTPS (implicit TLS) will be used.
    Any other port number will result in STARTTLS being used.

    The default is to enable encryption.
    """

    username: NonEmptyStr
    """
    SMTP username of the account to send the mail from.
    """

    password: Password
    """
    SMTP password of the account to send the mail from.
    """

    from_address: NameEmail
    """
    Email address to send the mail as.

    RFC-5322 formatted mailbox addresses are also supported,
    e.g. `Prowlarr Notifications <prowlarr@example.com>`.
    """

    recipient_addresses: Annotated[List[NameEmail], Field(min_items=1, unique_items=True)]
    """
    List of email addresses to directly address the mail to.

    At least one address must be provided.
    """

    cc_addresses: Annotated[List[NameEmail], Field(unique_items=True)] = []
    """
    Optional list of email addresses to copy (CC) the mail to.
    """

    bcc_addresses: Annotated[List[NameEmail], Field(unique_items=True)] = []
    """
    Optional list of email addresses to blind copy (BCC) the mail to.
    """

    _implementation: str = "Email"
    _remote_map: List[RemoteMapEntry] = [
        ("server", "server", {"is_field": True}),
        ("port", "port", {"is_field": True}),
        ("use_encryption", "requireEncryption", {"is_field": True}),
        ("username", "username", {"is_field": True}),
        ("password", "password", {"is_field": True}),
        ("from_address", "from", {"is_field": True}),
        ("recipient_addresses", "to", {"is_field": True}),
        ("cc_addresses", "cc", {"is_field": True}),
        ("bcc_addresses", "bcc", {"is_field": True}),
    ]


class GotifyNotification(Notification):
    """
    Send media update and health alert push notifications via a Gotify server.
    """

    type: Literal["gotify"] = "gotify"
    """
    Type value associated with this kind of connection.
    """

    server: AnyHttpUrl
    """
    Gotify server URL. (e.g. `http://gotify.example.com:1234`)
    """

    app_token: Password
    """
    App token to use to authenticate with Gotify.
    """

    priority: GotifyPriority = GotifyPriority.normal
    """
    Gotify notification priority.

    Values:

    * `min`
    * `low`
    * `normal`
    * `high`
    """

    _implementation: str = "Gotify"
    _remote_map: List[RemoteMapEntry] = [
        ("server", "server", {"is_field": True}),
        ("app_token", "appToken", {"is_field": True}),
        ("priority", "priority", {"is_field": True}),
    ]


class JoinNotification(Notification):
    """
    Send media update and health alert push notifications via Join.
    """

    type: Literal["join"] = "join"
    """
    Type value associated with this kind of connection.
    """

    api_key: Password
    """
    API key to use to authenticate with Join.
    """

    # Deprecated, only uncomment if absolutely required by Prowlarr
    # device_ids: Set[int] = set()

    device_names: Set[NonEmptyStr] = set()
    """
    List of full or partial device names you'd like to send notifications to.

    If unset or empty, all devices will receive notifications.
    """

    priority: JoinPriority = JoinPriority.normal
    """
    Join push notification priority.

    Values:

    * `silent`
    * `quiet`
    * `normal`
    * `high`
    * `emergency`
    """

    _implementation: str = "Join"
    _remote_map: List[RemoteMapEntry] = [
        ("api_key", "apiKey", {"is_field": True}),
        # ("device_ids", "deviceIds", {"is_field": True}),
        (
            "device_names",
            "deviceNames",
            {
                "is_field": True,
                "decoder": lambda v: (
                    set(d.strip() for d in v.split(",")) if v and v.strip() else set()
                ),
                "encoder": lambda v: ",".join(sorted(v)) if v else "",
            },
        ),
        ("priority", "priority", {"is_field": True}),
    ]


class MailgunNotification(Notification):
    """
    Send media update and health alert emails via the Mailgun delivery service.
    """

    type: Literal["mailgun"] = "mailgun"
    """
    Type value associated with this kind of connection.
    """

    api_key: Password
    """
    API key to use to authenticate with Mailgun.
    """

    use_eu_endpoint: bool = False
    """
    Send mail via the EU endpoint instead of the US one.
    """

    from_address: NameEmail
    """
    Email address to send the mail as.

    RFC-5322 formatted mailbox addresses are also supported,
    e.g. `Sonarr Notifications <sonarr@example.com>`.
    """

    sender_domain: NonEmptyStr
    """
    The domain from which the mail will be sent.
    """

    recipient_addresses: Annotated[List[NameEmail], Field(min_items=1, unique_items=True)]
    """
    The recipient email addresses of the notification mail.

    At least one recipient address is required.
    """

    _implementation: str = "Mailgun"
    _remote_map: List[RemoteMapEntry] = [
        ("api_key", "apiKey", {"is_field": True}),
        ("use_eu_endpoint", "useEuEndpoint", {"is_field": True}),
        ("from_address", "from", {"is_field": True}),
        ("sender_domain", "senderDomain", {"is_field": True}),
        ("recipient_addresses", "recipients", {"is_field": True}),
    ]


class NotifiarrNotification(Notification):
    """
    Send media update and health alert emails via the Notifiarr notification service.
    """

    type: Literal["notifiarr"] = "notifiarr"
    """
    Type value associated with this kind of connection.
    """

    api_key: Password
    """
    API key to use to authenticate with Notifiarr.
    """

    _implementation: str = "Notifiarr"
    _remote_map: List[RemoteMapEntry] = [("api_key", "apiKey", {"is_field": True})]


class NtfyNotification(Notification):
    """
    Send media update and health alert emails via the ntfy.sh notification service,
    or a self-hosted server using the same software.
    """

    type: Literal["ntfy"] = "ntfy"
    """
    Type value associated with this kind of connection.
    """

    server_url: Optional[AnyHttpUrl] = None
    """
    Custom ntfy server URL.

    Leave blank, set to `null` or undefined to use the public server (`https://ntfy.sh`).
    """

    username: Optional[str] = None
    """
    Username to use to authenticate, if required.
    """

    password: Optional[SecretStr] = None
    """
    Password to use to authenticate, if required.
    """

    priority: NtfyshPriority = NtfyshPriority.default
    """
    Values:

    * `min`
    * `low`
    * `default`
    * `high`
    * `max`
    """

    topics: Set[NonEmptyStr] = set()
    """
    List of Topics to send notifications to.
    """

    ntfy_tags: Set[NonEmptyStr] = set()
    """
    Optional list of tags or [emojis](https://ntfy.sh/docs/emojis) to use.
    """

    click_url: Optional[AnyHttpUrl] = None
    """
    Optional link for when the user clicks the notification.
    """

    _implementation: str = "Ntfy"
    _remote_map: List[RemoteMapEntry] = [
        (
            "server_url",
            "serverUrl",
            {
                "is_field": True,
                "decoder": lambda v: v or None,
                "encoder": lambda v: str(v) if v else "",
            },
        ),
        (
            "username",
            "userName",
            {"is_field": True, "decoder": lambda v: v or None, "encoder": lambda v: v or ""},
        ),
        (
            "password",
            "password",
            {
                "is_field": True,
                "decoder": lambda v: SecretStr(v) if v else None,
                "encoder": lambda v: v.get_secret_value() if v else "",
            },
        ),
        ("priority", "priority", {"is_field": True}),
        ("topics", "topics", {"is_field": True, "encoder": sorted}),
        ("ntfy_tags", "tags", {"is_field": True, "encoder": sorted}),
        (
            "click_url",
            "clickUrl",
            {"is_field": True, "decoder": lambda v: v or None, "encoder": lambda v: v or ""},
        ),
    ]


class ProwlNotification(Notification):
    """
    Send media update and health alert push notifications to a Prowl client.
    """

    type: Literal["prowl"] = "prowl"
    """
    Type value associated with this kind of connection.
    """

    api_key: Password
    """
    API key to use when authenticating with Prowl.
    """

    priority: ProwlPriority = ProwlPriority.normal
    """
    Prowl push notification priority.

    Values:

    * `verylow`
    * `low`
    * `normal`
    * `high`
    * `emergency`
    """

    _implementation: str = "Prowl"
    _remote_map: List[RemoteMapEntry] = [
        ("api_key", "apiKey", {"is_field": True}),
        ("priority", "priority", {"is_field": True}),
    ]


class PushbulletNotification(Notification):
    """
    Send media update and health alert push notifications to 1 or more Pushbullet devices.
    """

    type: Literal["pushbullet"] = "pushbullet"
    """
    Type value associated with this kind of connection.
    """

    api_key: Password
    """
    API key to use when authenticating with Pushbullet.
    """

    device_ids: List[NonEmptyStr] = []
    """
    List of device IDs to send notifications to.

    If unset or empty, send to all devices.
    """

    channel_tags: List[NonEmptyStr] = []
    """
    List of Channel Tags to send notifications to.
    """

    sender_id: Optional[str] = None
    """
    The device ID to send notifications from
    (`device_iden` in the device's URL on [pushbullet.com](https://pushbullet.com)).

    Leave unset, blank or set to `None` to send from yourself.
    """

    _implementation: str = "Pushbullet"
    _remote_map: List[RemoteMapEntry] = [
        ("api_key", "apiKey", {"is_field": True}),
        ("device_ids", "deviceIds", {"is_field": True}),
        ("channel_tags", "channelTags", {"is_field": True}),
        (
            "sender_id",
            "senderId",
            {"is_field": True, "decoder": lambda v: v or None, "encoder": lambda v: v or ""},
        ),
    ]


class PushoverNotification(Notification):
    """
    Send media update and health alert push notifications to 1 or more Pushover devices.
    """

    type: Literal["pushover"] = "pushover"
    """
    Type value associated with this kind of connection.
    """

    user_key: Annotated[SecretStr, Field(min_length=30, max_length=30)]
    """
    User key to use to authenticate with your Pushover account.
    """

    api_key: Annotated[SecretStr, Field(min_length=30, max_length=30)]
    """
    API key assigned to Prowlarr in Pushover.
    """

    devices: Set[NonEmptyStr] = set()
    """
    List of device names to send notifications to.

    If unset or empty, send to all devices.
    """

    priority: PushoverPriority = PushoverPriority.normal
    """
    Pushover push notification priority.

    Values:

    * `silent`
    * `quiet`
    * `normal`
    * `high`
    * `emergency`
    """

    retry: Union[Literal[0], PushoverRetry] = 0
    """
    Interval to retry emergency alerts, in seconds.

    Minimum 30 seconds. Set to 0 to disable retrying emergency alerts.
    """

    # TODO: Enforce "expire > retry if retry > 0" constraint
    expire: int = Field(0, ge=0, le=86400)
    """
    Threshold for retrying emergency alerts, in seconds.
    If `retry` is set, this should be set to a higher value.

    Maximum 86400 seconds (1 day).
    """

    sound: Optional[str] = None
    """
    Notification sound to use on devices.

    Leave unset, blank or set to `None` to use the default.
    """

    _implementation: str = "Pushover"
    _remote_map: List[RemoteMapEntry] = [
        ("user_key", "userKey", {"is_field": True}),
        ("api_key", "apiKey", {"is_field": True}),
        ("devices", "devices", {"is_field": True, "encoder": lambda v: sorted(v)}),
        ("priority", "priority", {"is_field": True}),
        ("retry", "retry", {"is_field": True}),
        ("expire", "expire", {"is_field": True}),
        (
            "sound",
            "sound",
            {"is_field": True, "decoder": lambda v: v or None, "encoder": lambda v: v or ""},
        ),
    ]


class SendgridNotification(Notification):
    """
    Send media update and health alert emails via the SendGrid delivery service.
    """

    type: Literal["sendgrid"] = "sendgrid"
    """
    Type value associated with this kind of connection.
    """

    api_key: Password
    """
    API key to use to authenticate with SendGrid.
    """

    from_address: NameEmail
    """
    Email address to send the mail as.

    RFC-5322 formatted mailbox addresses are also supported,
    e.g. `Prowlarr Notifications <prowlarr@example.com>`.
    """

    recipient_addresses: Annotated[List[NameEmail], Field(min_items=1, unique_items=True)]
    """
    The recipient email addresses of the notification mail.

    At least one recipient address is required.
    """

    _implementation: str = "SendGrid"
    _remote_map: List[RemoteMapEntry] = [
        ("api_key", "apiKey", {"is_field": True}),
        ("from_address", "from", {"is_field": True}),
        ("recipient_addresses", "recipients", {"is_field": True}),
    ]


class SlackNotification(Notification):
    """
    Send media update and health alert messages to a Slack channel.
    """

    type: Literal["slack"] = "slack"
    """
    Type value associated with this kind of connection.
    """

    webhook_url: AnyHttpUrl
    """
    Webhook URL for the Slack channel to send to.
    """

    username: NonEmptyStr
    """
    Username to post as.
    """

    icon: Optional[str] = None
    """
    The icon that is used for messages from this integration (emoji or URL).

    If unset, blank or set to `None`, use the default for the user.
    """

    channel: Optional[str] = None
    """
    If set, overrides the default channel in the webhook.
    """

    _implementation: str = "Slack"
    _remote_map: List[RemoteMapEntry] = [
        ("webhook_url", "webHookUrl", {"is_field": True}),
        ("username", "username", {"is_field": True}),
        (
            "icon",
            "icon",
            {"is_field": True, "decoder": lambda v: v or None, "encoder": lambda v: v or ""},
        ),
        (
            "channel",
            "channel",
            {"is_field": True, "decoder": lambda v: v or None, "encoder": lambda v: v or ""},
        ),
    ]


class TelegramNotification(Notification):
    """
    Send media update and health alert messages to a Telegram chat room.
    """

    type: Literal["telegram"] = "telegram"
    """
    Type value associated with this kind of connection.
    """

    bot_token: Password
    """
    The bot token assigned to the Prowlarr instance.
    """

    chat_id: NonEmptyStr
    """
    The ID of the chat room to send messages to.

    You must start a conversation with the bot or add it to your group to receive messages.
    """

    send_silently: bool = False
    """
    Sends the message silently. Users will receive a notification with no sound.
    """

    _implementation: str = "Telegram"
    _remote_map: List[RemoteMapEntry] = [
        ("bot_token", "botToken", {"is_field": True}),
        ("chat_id", "chatId", {"is_field": True}),
        ("send_silently", "sendSilently", {"is_field": True}),
    ]


class TwitterNotification(Notification):
    """
    Send media update and health alert messages via Twitter.

    Twitter requires you to create an application for their API
    to generate the necessary keys and secrets.
    If unsure how to proceed, refer to these guides from
    [Twitter](https://developer.twitter.com/en/docs/authentication/oauth-1-0a/api-key-and-secret)
    and [WikiArr](https://wiki.servarr.com/useful-tools#twitter-connect).

    Access tokens can be obtained using the prodecure documented [here](
    https://developer.twitter.com/en/docs/authentication/oauth-1-0a/obtaining-user-access-tokens).
    """

    type: Literal["twitter"] = "twitter"
    """
    Type value associated with this kind of connection.
    """

    consumer_key: Password
    """
    Consumer key from a Twitter application.
    """

    consumer_secret: Password
    """
    Consumer key from a Twitter application.
    """

    access_token: Password
    """
    Access token for a Twitter user.
    """

    access_token_secret: Password
    """
    Access token secret for a Twitter user.
    """

    mention: NonEmptyStr
    """
    Mention this user in sent tweets.
    """

    direct_message: bool = True
    """
    Send a direct message instead of a public message.
    """

    _implementation: str = "Twitter"
    _remote_map: List[RemoteMapEntry] = [
        ("consumer_key", "consumerKey", {"is_field": True}),
        ("consumer_secret", "consumerSecret", {"is_field": True}),
        ("access_token", "accessToken", {"is_field": True}),
        ("access_token_secret", "accessTokenSecret", {"is_field": True}),
        ("mention", "mention", {"is_field": True}),
        ("direct_message", "direct_message", {"is_field": True}),
    ]


class WebhookNotification(Notification):
    """
    Send media update and health alert notifications to a webhook API.
    """

    type: Literal["webhook"] = "webhook"
    """
    Type value associated with this kind of connection.
    """

    url: AnyHttpUrl
    """
    Webhook URL to send notifications to.
    """

    method: WebhookMethod = WebhookMethod.POST
    """
    HTTP request method type to use.

    Values:

    * `POST`
    * `PUT`
    """

    username: NonEmptyStr
    """
    Webhook API username.
    """

    password: Password
    """
    Webhook API password.
    """

    _implementation: str = "Webhook"
    _remote_map: List[RemoteMapEntry] = [
        ("url", "url", {"is_field": True}),
        ("method", "method", {"is_field": True}),
        ("username", "username", {"is_field": True}),
        ("password", "password", {"is_field": True}),
    ]


NOTIFICATION_TYPES: Tuple[Type[Notification], ...] = (
    AppriseNotification,
    BoxcarNotification,
    CustomscriptNotification,
    DiscordNotification,
    EmailNotification,
    GotifyNotification,
    JoinNotification,
    MailgunNotification,
    NotifiarrNotification,
    NtfyNotification,
    ProwlNotification,
    PushbulletNotification,
    PushoverNotification,
    SendgridNotification,
    SlackNotification,
    TelegramNotification,
    TwitterNotification,
    WebhookNotification,
)

NOTIFICATION_TYPE_MAP: Dict[str, Type[Notification]] = {
    notification_type._implementation.lower(): notification_type
    for notification_type in NOTIFICATION_TYPES
}

NotificationType = Union[
    AppriseNotification,
    BoxcarNotification,
    CustomscriptNotification,
    DiscordNotification,
    EmailNotification,
    GotifyNotification,
    JoinNotification,
    MailgunNotification,
    NotifiarrNotification,
    NtfyNotification,
    ProwlNotification,
    PushbulletNotification,
    PushoverNotification,
    SendgridNotification,
    SlackNotification,
    TelegramNotification,
    TwitterNotification,
    WebhookNotification,
]


class ProwlarrNotificationsSettings(ProwlarrConfigBase):
    """
    Manage notification connections in Prowlarr.
    """

    delete_unmanaged: bool = False
    """
    Automatically delete connections not configured in Buildarr.

    Take care when enabling this option, as this can remove connections automatically
    managed by other applications.
    """

    definitions: Dict[str, Annotated[NotificationType, Field(discriminator="type")]] = {}
    """
    Notification connections are defined here.
    """

    @classmethod
    def from_remote(cls, secrets: ProwlarrSecrets) -> Self:
        with prowlarr_api_client(secrets=secrets) as api_client:
            api_notifications = prowlarr.NotificationApi(api_client).list_notification()
            tag_ids: Dict[str, int] = (
                {tag.label: tag.id for tag in prowlarr.TagApi(api_client).list_tag()}
                if any(api_notification.tags for api_notification in api_notifications)
                else {}
            )
        return cls(
            definitions={
                api_notification.name: NOTIFICATION_TYPE_MAP[
                    api_notification.implementation.lower()
                ]._from_remote(
                    tag_ids=tag_ids,
                    remote_attrs=api_notification.to_dict(),
                )
                for api_notification in api_notifications
            },
        )

    def update_remote(
        self,
        tree: str,
        secrets: ProwlarrSecrets,
        remote: Self,
        check_unmanaged: bool = False,
    ) -> bool:
        # Track whether or not any changes have been made on the remote instance.
        changed = False
        # Pull API objects and metadata required during the update operation.
        with prowlarr_api_client(secrets=secrets) as api_client:
            notification_api = prowlarr.NotificationApi(api_client)
            api_notification_schemas = notification_api.list_notification_schema()
            api_notifications: Dict[str, prowlarr.NotificationResource] = {
                api_notification.name: api_notification
                for api_notification in notification_api.list_notification()
            }
            tag_ids: Dict[str, int] = (
                {tag.label: tag.id for tag in prowlarr.TagApi(api_client).list_tag()}
                if any(api_notification.tags for api_notification in self.definitions.values())
                or any(api_notification.tags for api_notification in remote.definitions.values())
                else {}
            )
        # Compare local definitions to their remote equivalent.
        # If a local definition does not exist on the remote, create it.
        # If it does exist on the remote, attempt an an in-place modification,
        # and set the `changed` flag if modifications were made.
        for notification_name, notification in self.definitions.items():
            notification_tree = f"{tree}.definitions[{repr(notification_name)}]"
            if notification_name not in remote.definitions:
                notification._create_remote(
                    tree=notification_tree,
                    secrets=secrets,
                    api_notification_schemas=api_notification_schemas,
                    tag_ids=tag_ids,
                    notification_name=notification_name,
                )
                changed = True
            elif notification._update_remote(
                tree=notification_tree,
                secrets=secrets,
                remote=remote.definitions[notification_name],  # type: ignore[arg-type]
                api_notification_schemas=api_notification_schemas,
                tag_ids=tag_ids,
                api_notification=api_notifications[notification_name],
            ):
                changed = True
        # Traverse the remote definitions, and see if there are any remote definitions
        # that do not exist in the local configuration.
        # If `delete_unmanaged` is enabled, delete it from the remote.
        # If `delete_unmanaged` is disabled, just add a log entry acknowledging
        # the existence of the unmanaged definition.
        for notification_name, notification in remote.definitions.items():
            if notification_name not in self.definitions:
                notification_tree = f"{tree}.definitions[{repr(notification_name)}]"
                if self.delete_unmanaged:
                    notification._delete_remote(
                        tree=notification_tree,
                        secrets=secrets,
                        notification_id=api_notifications[notification_name].id,
                    )
                    changed = True
                else:
                    logger.debug("%s: (...) (unmanaged)", notification_tree)
        # Return whether or not the remote instance was changed.
        return changed
