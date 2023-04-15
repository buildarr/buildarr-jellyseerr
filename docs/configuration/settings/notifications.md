# Notifications

Jellyseerr supports pushing notifications to external applications and services.

These are not only for Jellyseerr to communicate with the outside world, they can also be useful
for monitoring since the user can be alerted, by a service of their choice, when
some kind of event (or problem) occurs.

## Enabling notifications

##### ::: buildarr_jellyseerr.config.settings.notifications.base.NotificationsSettingsBase
    options:
      members:
        - enable
      show_root_heading: false
      show_source: false

## Configuring notification types

##### ::: buildarr_jellyseerr.config.settings.notifications.notification_types.NotificationTypesSettingsBase
    options:
      members:
        - notification_types
      show_root_heading: false
      show_source: false

## Discord

##### ::: buildarr_jellyseerr.config.settings.notifications.discord.DiscordSettings
    options:
      members:
        - webhook_url
        - username
        - avatar_url
        - enable_mentions
      show_root_heading: false
      show_source: false

## Email

##### ::: buildarr_jellyseerr.config.settings.notifications.email.EmailSettings
    options:
      members:
        - require_user_email
        - sender_name
        - sender_address
        - smtp_host
        - smtp_port
        - encryption_method
        - allow_selfsigned_certificates
        - smtp_username
        - smtp_password
        - pgp_private_key
        - pgp_password
      show_root_heading: false
      show_source: false

## Gotify

##### ::: buildarr_jellyseerr.config.settings.notifications.gotify.GotifySettings
    options:
      members:
        - server_url
        - access_token
      show_root_heading: false
      show_source: false

## LunaSea

##### ::: buildarr_jellyseerr.config.settings.notifications.lunasea.LunaseaSettings
    options:
      members:
        - webhook_url
        - profile_name
      show_root_heading: false
      show_source: false

## Pushbullet

##### ::: buildarr_jellyseerr.config.settings.notifications.pushbullet.PushbulletSettings
    options:
      members:
        - access_token
        - channel_tag
      show_root_heading: false
      show_source: false

## Pushover

##### ::: buildarr_jellyseerr.config.settings.notifications.pushover.PushoverSettings
    options:
      members:
        - api_key
        - user_key
      show_root_heading: false
      show_source: false

## Slack

##### ::: buildarr_jellyseerr.config.settings.notifications.slack.SlackSettings
    options:
      members:
        - webhook_url
      show_root_heading: false
      show_source: false

## Telegram

##### ::: buildarr_jellyseerr.config.settings.notifications.telegram.TelegramSettings
    options:
      members:
        - access_token
        - username
        - chat_id
        - send_silently
      show_root_heading: false
      show_source: false

## Webhook

##### ::: buildarr_jellyseerr.config.settings.notifications.webhook.WebhookSettings
    options:
      members:
        - webhook_url
        - authorization_header
        - payload_template
      show_root_heading: false
      show_source: false


## Webpush (Browser Push Notifiations)

##### ::: buildarr_jellyseerr.config.settings.notifications.webpush.WebpushSettings
    options:
      show_root_heading: false
      show_source: false
