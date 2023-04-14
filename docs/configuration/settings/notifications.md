# Notifications

Jellyseerr supports pushing notifications to external applications and services.

These are not only for Jellyseerr to communicate with the outside world, they can also be useful
for monitoring since the user can be alerted, by a service of their choice, when
some kind of event (or problem) occurs.

## Configuration

## Discord

##### ::: buildarr_jellyseerr.config.settings.notifications.discord.DiscordSettings
    options:
      members:
        - type
        - webook_url
        - username
        - avatar
        - host
        - on_grab_fields
        - on_import_fields
      show_root_heading: false
      show_source: false

## Email

##### ::: buildarr_jellyseerr.config.settings.notifications.email.EmailSettings
    options:
      members:
        - type
        - server
        - port
        - use_encryption
        - username
        - password
        - from_address
        - recipient_addresses
        - cc_addresses
        - bcc_addresses
      show_root_heading: false
      show_source: false

## Gotify

##### ::: buildarr_jellyseerr.config.settings.notifications.gotify.GotifySettings
    options:
      members:
        - type
        - server
        - app_token
        - priority
      show_root_heading: false
      show_source: false

## LunaSea

##### ::: buildarr_jellyseerr.config.settings.notifications.lunasea.LunaseaSettings
    options:
      members:
        - type
        - api_key
        - device_names
        - priority
      show_root_heading: false
      show_source: false

## Pushbullet

##### ::: buildarr_jellyseerr.config.settings.notifications.pushbullet.PushbulletSettings
    options:
      members:
        - type
        - api_key
        - device_ids
        - channel_tags
        - sender_id
      show_root_heading: false
      show_source: false

## Pushover

##### ::: buildarr_jellyseerr.config.settings.notifications.pushover.PushoverSettings
    options:
      members:
        - type
        - user_key
        - api_key
        - devices
        - priority
        - retry
        - expire
        - sound
      show_root_heading: false
      show_source: false

## Slack

##### ::: buildarr_jellyseerr.config.settings.notifications.slack.SlackSettings
    options:
      members:
        - type
        - webhook_url
        - username
        - icon
        - channel
      show_root_heading: false
      show_source: false

## Telegram

##### ::: buildarr_jellyseerr.config.settings.notifications.telegram.TelegramSettings
    options:
      members:
        - type
        - bot_token
        - chat_id
        - send_silently
      show_root_heading: false
      show_source: false

## Webhook

##### ::: buildarr_jellyseerr.config.settings.notifications.webhook.WebhookSettings
    options:
      members:
        - type
        - webhook_url
        - method
        - username
        - password
      show_root_heading: false
      show_source: false


## Webpush (Browser Push Notifiations)

##### ::: buildarr_jellyseerr.config.settings.notifications.webpush.WebpushSettings
    options:
      members:
        - enable
      show_root_heading: false
      show_source: false
