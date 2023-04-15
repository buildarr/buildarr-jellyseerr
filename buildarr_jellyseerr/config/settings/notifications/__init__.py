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
Jellyseerr plugin notifications settings configuration.
"""


from __future__ import annotations

from ...types import JellyseerrConfigBase
from .discord import DiscordSettings
from .email import EmailSettings
from .gotify import GotifySettings
from .lunasea import LunaseaSettings
from .pushbullet import PushbulletSettings
from .pushover import PushoverSettings
from .slack import SlackSettings
from .telegram import TelegramSettings
from .webhook import WebhookSettings
from .webpush import WebpushSettings


class JellyseerrNotificationsSettings(JellyseerrConfigBase):
    discord: DiscordSettings = DiscordSettings()
    email: EmailSettings = EmailSettings()
    gotify: GotifySettings = GotifySettings()
    lunasea: LunaseaSettings = LunaseaSettings()
    pushbullet: PushbulletSettings = PushbulletSettings()
    pushover: PushoverSettings = PushoverSettings()
    slack: SlackSettings = SlackSettings()
    telegram: TelegramSettings = TelegramSettings()
    webhook: WebhookSettings = WebhookSettings()
    webpush: WebpushSettings = WebpushSettings()
