# Notifications

Jellyseerr supports pushing notifications to external applications and services.

These are not only for Jellyseerr to communicate with the outside world, they can also be useful
for monitoring since the user can be alerted, by a service of their choice, when
some kind of event (or problem) occurs.

For more information on configuring push notifications for Jellyseerr, refer to [this guide](https://docs.overseerr.dev/using-overseerr/notifications) in the Overseerr documentation.

## Enabling notifications

##### ::: buildarr_jellyseerr.config.settings.notifications.base.NotificationsSettingsBase
    options:
      members:
        - enable

## Configuring notification types

Some service types support fine-grained configuration of the type of notifications that get sent.

This is done by defining the optional `notification_types` configuration attribute
in the settings for that service.

```yaml
jellyseerr:
  settings:
    notifications:
      slack:
        enable: true
        webhook_url: "..."
        notification_types:
          - "media-pending"
          - "media-approved"
          - "media-available"
          - "media-failed"
          - "test-notification"
          - "media-declined"
          - "media-auto-approved"
          - "issue-created"
          - "issue-comment"
          - "issue-resolved"
          - "issue-reopened"
          - "media-auto-requested"
```

## Discord

##### ::: buildarr_jellyseerr.config.settings.notifications.discord.DiscordSettings
    options:
      members:
        - webhook_url
        - username
        - avatar_url
        - enable_mentions

##### ::: buildarr_jellyseerr.config.settings.notifications.notification_types.NotificationTypesSettingsBase
    options:
      members:
        - notification_types

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

## Gotify

##### ::: buildarr_jellyseerr.config.settings.notifications.gotify.GotifySettings
    options:
      members:
        - server_url
        - access_token

##### ::: buildarr_jellyseerr.config.settings.notifications.notification_types.NotificationTypesSettingsBase
    options:
      members:
        - notification_types

## LunaSea

##### ::: buildarr_jellyseerr.config.settings.notifications.lunasea.LunaseaSettings
    options:
      members:
        - webhook_url
        - profile_name

##### ::: buildarr_jellyseerr.config.settings.notifications.notification_types.NotificationTypesSettingsBase
    options:
      members:
        - notification_types

## Pushbullet

##### ::: buildarr_jellyseerr.config.settings.notifications.pushbullet.PushbulletSettings
    options:
      members:
        - access_token
        - channel_tag

##### ::: buildarr_jellyseerr.config.settings.notifications.notification_types.NotificationTypesSettingsBase
    options:
      members:
        - notification_types

## Pushover

##### ::: buildarr_jellyseerr.config.settings.notifications.pushover.PushoverSettings
    options:
      members:
        - api_key
        - user_key

##### ::: buildarr_jellyseerr.config.settings.notifications.notification_types.NotificationTypesSettingsBase
    options:
      members:
        - notification_types

## Slack

##### ::: buildarr_jellyseerr.config.settings.notifications.slack.SlackSettings
    options:
      members:
        - webhook_url

##### ::: buildarr_jellyseerr.config.settings.notifications.notification_types.NotificationTypesSettingsBase
    options:
      members:
        - notification_types

## Telegram

##### ::: buildarr_jellyseerr.config.settings.notifications.telegram.TelegramSettings
    options:
      members:
        - access_token
        - username
        - chat_id
        - send_silently

##### ::: buildarr_jellyseerr.config.settings.notifications.notification_types.NotificationTypesSettingsBase
    options:
      members:
        - notification_types

## Webhook

##### ::: buildarr_jellyseerr.config.settings.notifications.webhook.WebhookSettings
    options:
      members:
        - webhook_url
        - authorization_header
        - payload_template

##### ::: buildarr_jellyseerr.config.settings.notifications.notification_types.NotificationTypesSettingsBase
    options:
      members:
        - notification_types

## Webpush (Browser Push Notifiations)

##### ::: buildarr_jellyseerr.config.settings.notifications.webpush.WebpushSettings
