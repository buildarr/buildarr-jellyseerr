# Buildarr Jellyseerr Plugin

[![PyPI](https://img.shields.io/pypi/v/buildarr-jellyseerr)](https://pypi.org/project/buildarr-jellyseerr) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/buildarr-jellyseerr)  [![GitHub](https://img.shields.io/github/license/buildarr/buildarr-jellyseerr)](https://github.com/buildarr/buildarr-jellyseerr/blob/main/LICENSE) ![Pre-commit hooks](https://github.com/buildarr/buildarr-jellyseerr/actions/workflows/pre-commit.yml/badge.svg) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

The Buildarr Jellyseerr plugin (`buildarr-jellyseerr`) is a plugin for Buildarr that adds the capability to configure and manage [Jellyseerr](https://github.com/Fallenbagel/jellyseerr) instances.

Jellyseerr is an application that links with both Jellyfin/Plex and your Sonarr/Radarr instances. It allows your users to login using their Jellyfin/Plex credentials, browse available media online, and make media requests for new content.

Once these requests are approved, Jellyseerr will then make the requests to Sonarr/Radarr to download them, monitor the progress, and report back to the user when the media is available in Jellyfin/Plex.

Buildarr can be used to initialise a new Jellyseerr install with Jellyfin server credentials (Plex is not supported at this time), manage the Jellyseerr server settings, and connect it with Sonarr and Radarr servers.

## Installation

When using Buildarr as a [standalone application](https://buildarr.github.io/installation/#standalone-application), the Jellyseerr plugin can simply be installed using `pip`:

```bash
$ pip install buildarr buildarr-jellyseerr
```

If you are linking a Jellyseerr instance with another Buildarr-configured application, specify the following extras to also install a compatible version of the corresponding plugins:

* `sonarr` (for the Sonarr TV show PVR)
* `radarr` (for the Radarr movie PVR)

```bash
$ pip install buildarr buildarr-jellyseerr[sonarr,radarr]
```

When using Buildarr as a [Docker container](https://buildarr.github.io/installation/#docker), the Jellyseerr plugin is bundled with the official container (`callum027/buildarr`), so there is no need to install it separately.

You can upgrade or pin the version of the plugin to a specific version within the container by setting the `$BUILDARR_JELLYSEERR_VERSION` environment variable in the `docker run` command using `--env`/`-e`:

```bash
-e BUILDARR_JELLYSEERR_VERSION="<version>"
```

## Quick Start

Brand new Jellyseerr instances require initialisation for Buildarr to be able to manage it.

This is usually done manually by navigating to `http://localhost:5055/setup` on the Jellyseerr host, logging in with Jellyfin or Plex credentials, and then selecting libraries to monitor.

As of this release, automatically initialising Jellyseerr for Plex is not yet supported. Please initialise the Jellyseerr instance manually.

For Jellyseerr instances being connected to Jellyfin only, Buildarr can perform this initialisation automatically.

To do this, set the following parameters under the `jellyfin` configuration section, which are required when initialisting a new instance (they are otherwise optional):

```yaml
---

jellyseerr:
  hostname: "localhost"
  port: 5055
  protocol: "http"
  api_key: "<API key>"  # Required. Check `settings.json` in the config volume to get the value.
  settings:
    jellyfin:
      server_url: "http://localhost:8096"  # Jellyfin server URL, preferably direct (no proxy).
      username: "admin"  # Jellyfin server admin user.
      password: "secure-password"  # Jellyfin server admin user password.
      email_address: "admin@example.com"  # Jellyfin server admin email address.
      # Jellyfin media libraries to monitor.
      # This can be used to change what libraries Jellyseerr monitors,
      # even after it is initialised.
      libraries:
        - "Shows"
        - "Movies"
        - "Anime"
        - "Anime Movies"
```

After that, configure and run Buildarr as normal, and setup desired settings for Jellyseerr.

For more information on configuring Jellyseerr, see [Configuring your Jellyseerr instance](#configuring-your-jellyseerr-instance).

Once you have a complete configuration file, test it against the Jellyseerr instance using `buildarr run`.

The output should contain messages about checking, performing and finishing the initialisation. If no errors were found, congratulations, your Jellyseerr instance is now managed by Buildarr!

```text
2023-04-15 09:44:20,386 buildarr:1 buildarr.cli.run [INFO] Buildarr version 0.4.2 (log level: INFO)
2023-04-15 09:44:20,386 buildarr:1 buildarr.cli.run [INFO] Loading configuration file '/config/buildarr.yml'
2023-04-15 09:44:20,458 buildarr:1 buildarr.cli.run [INFO] Finished loading configuration file
2023-04-15 09:44:20,461 buildarr:1 buildarr.cli.run [INFO] Loaded plugins: jellyseerr (0.1.0), prowlarr (0.1.1), sonarr (0.4.1)
2023-04-15 09:44:20,461 buildarr:1 buildarr.cli.run [INFO] Loading instance configurations
2023-04-15 09:44:20,464 buildarr:1 buildarr.cli.run [INFO] Finished loading instance configurations
2023-04-15 09:44:20,464 buildarr:1 buildarr.cli.run [INFO] Running with plugins: sonarr, jellyseerr
2023-04-15 09:44:20,464 buildarr:1 buildarr.cli.run [INFO] Resolving instance dependencies
2023-04-15 09:44:20,464 buildarr:1 buildarr.cli.run [INFO] Finished resolving instance dependencies
2023-04-15 09:44:20,464 buildarr:1 buildarr.cli.run [INFO] Rendering instance configuration dynamic attributes
2023-04-15 09:44:20,465 buildarr:1 buildarr.cli.run [INFO] Finished rendering instance configuration dynamic attributes
2023-04-15 09:44:20,599 buildarr:1 buildarr.cli.run [INFO] <jellyseerr> (default) Instance has not been initialised
2023-04-15 09:44:20,600 buildarr:1 buildarr.cli.run [INFO] <jellyseerr> (default) Initialising instance
2023-04-15 09:44:20,600 buildarr:1 buildarr_jellyseerr.config.settings.jellyfin [INFO] <jellyseerr> (default) Checking if required attributes are defined
2023-04-15 09:44:20,600 buildarr:1 buildarr_jellyseerr.config.settings.jellyfin [INFO] <jellyseerr> (default) Finished checking if required attributes are defined
2023-04-15 09:44:20,600 buildarr:1 buildarr_jellyseerr.config.settings.jellyfin [INFO] <jellyseerr> (default) Authenticating Jellyseerr with Jellyfin
2023-04-15 09:44:20,842 buildarr:1 buildarr_jellyseerr.config.settings.jellyfin [INFO] <jellyseerr> (default) Finished authenticating Jellyseerr with Jellyfin
2023-04-15 09:44:20,842 buildarr:1 buildarr_jellyseerr.config.settings.jellyfin [INFO] <jellyseerr> (default) Syncing Jellyfin libraries to Jellyseerr
2023-04-15 09:44:21,027 buildarr:1 buildarr_jellyseerr.config.settings.jellyfin [INFO] <jellyseerr> (default) Finished syncing Jellyfin libraries to Jellyseerr
2023-04-15 09:44:21,027 buildarr:1 buildarr_jellyseerr.config.settings.jellyfin [INFO] <jellyseerr> (default) Enabling Jellyfin libraries in Jellyseerr: 'TV Shows'
2023-04-15 09:44:21,083 buildarr:1 buildarr_jellyseerr.config.settings.jellyfin [INFO] <jellyseerr> (default) Finished enabling Jellyfin libraries in Jellyseerr
2023-04-15 09:44:21,083 buildarr:1 buildarr_jellyseerr.config.settings.jellyfin [INFO] <jellyseerr> (default) Finalising initialisation
2023-04-15 09:44:21,191 buildarr:1 buildarr_jellyseerr.config.settings.jellyfin [INFO] <jellyseerr> (default) Finished finalising initialisation
2023-04-15 09:44:21,192 buildarr:1 buildarr.cli.run [INFO] <jellyseerr> (default) Finished initialising instance
2023-04-15 09:44:21,192 buildarr:1 buildarr.cli.run [INFO] Loading secrets file from '/config/secrets.json'
2023-04-15 09:44:21,196 buildarr:1 buildarr.cli.run [INFO] Finished loading secrets file
2023-04-15 09:44:21,196 buildarr:1 buildarr.cli.run [INFO] <sonarr> (default) Checking secrets
2023-04-15 09:44:21,201 buildarr:1 buildarr.cli.run [INFO] <sonarr> (default) Connection test successful using cached secrets
2023-04-15 09:44:21,201 buildarr:1 buildarr.cli.run [INFO] <sonarr> (default) Finished checking secrets
2023-04-15 09:44:21,201 buildarr:1 buildarr.cli.run [INFO] <jellyseerr> (default) Checking secrets
2023-04-15 09:44:21,223 buildarr:1 buildarr.cli.run [INFO] <jellyseerr> (default) Connection test failed using cached secrets (or not cached), fetching secrets
2023-04-15 09:44:21,231 buildarr:1 buildarr.cli.run [INFO] <jellyseerr> (default) Connection test successful using fetched secrets
2023-04-15 09:44:21,231 buildarr:1 buildarr.cli.run [INFO] <jellyseerr> (default) Finished checking secrets
2023-04-15 09:44:21,231 buildarr:1 buildarr.cli.run [INFO] Saving updated secrets file to '/config/secrets.json'
2023-04-15 09:44:21,232 buildarr:1 buildarr.cli.run [INFO] Finished saving updated secrets file
2023-04-15 09:44:21,232 buildarr:1 buildarr.cli.run [INFO] Updating configuration on remote instances
2023-04-15 09:44:21,232 buildarr:1 buildarr.cli.run [INFO] <sonarr> (default) Fetching remote configuration to check if updates are required
2023-04-15 09:44:21,363 buildarr:1 buildarr.cli.run [INFO] <sonarr> (default) Finished fetching remote configuration
2023-04-15 09:44:21,402 buildarr:1 buildarr.cli.run [INFO] <sonarr> (default) Updating remote configuration
2023-04-15 09:44:21,491 buildarr:1 buildarr.cli.run [INFO] <sonarr> (default) Remote configuration is up to date
2023-04-15 09:44:21,491 buildarr:1 buildarr.cli.run [INFO] <sonarr> (default) Finished updating remote configuration
2023-04-15 09:44:21,491 buildarr:1 buildarr.cli.run [INFO] <jellyseerr> (default) Fetching remote configuration to check if updates are required
2023-04-15 09:44:22,496 buildarr:1 buildarr.cli.run [INFO] <jellyseerr> (default) Finished fetching remote configuration
2023-04-15 09:44:22,507 buildarr:1 buildarr.cli.run [INFO] <jellyseerr> (default) Updating remote configuration
2023-04-15 09:44:22,629 buildarr:1 buildarr.cli.run [INFO] <jellyseerr> (default) Remote configuration successfully updated
2023-04-15 09:44:22,629 buildarr:1 buildarr.cli.run [INFO] <jellyseerr> (default) Finished updating remote configuration
2023-04-15 09:44:22,629 buildarr:1 buildarr.cli.run [INFO] Finished updating configuration on remote instances
2023-04-15 09:44:22,629 buildarr:1 buildarr.cli.run [INFO] Deleting unmanaged/unused resources on remote instances
2023-04-15 09:44:22,630 buildarr:1 buildarr.cli.run [INFO] <jellyseerr> (default) Refetching remote configuration to delete unused resources
2023-04-15 09:44:22,735 buildarr:1 buildarr.cli.run [INFO] <jellyseerr> (default) Finished refetching remote configuration
2023-04-15 09:44:22,749 buildarr:1 buildarr.cli.run [INFO] <jellyseerr> (default) Deleting unmanaged/unused resources on the remote instance
2023-04-15 09:44:22,760 buildarr:1 buildarr.cli.run [INFO] <jellyseerr> (default) Remote configuration is clean
2023-04-15 09:44:22,760 buildarr:1 buildarr.cli.run [INFO] <jellyseerr> (default) Finished deleting unmanaged/unused resources on the remote instance
2023-04-15 09:44:22,760 buildarr:1 buildarr.cli.run [INFO] <sonarr> (default) Refetching remote configuration to delete unused resources
2023-04-15 09:44:22,874 buildarr:1 buildarr.cli.run [INFO] <sonarr> (default) Finished refetching remote configuration
2023-04-15 09:44:22,909 buildarr:1 buildarr.cli.run [INFO] <sonarr> (default) Deleting unmanaged/unused resources on the remote instance
2023-04-15 09:44:22,910 buildarr:1 buildarr.cli.run [INFO] <sonarr> (default) Remote configuration is clean
2023-04-15 09:44:22,910 buildarr:1 buildarr.cli.run [INFO] <sonarr> (default) Finished deleting unmanaged/unused resources on the remote instance
2023-04-15 09:44:22,910 buildarr:1 buildarr.cli.run [INFO] Finished deleting unmanaged/unused resources on remote instances
```

## Configuring your Jellyseerr instance

The following sections cover all of the possible configuration attributes for a Jellyseerr instance.

* [Host Configuration](https://buildarr.github.io/plugins/jellyseerr/configuration/host)
* Settings
    * [General](https://buildarr.github.io/plugins/jellyseerr/configuration/settings/general)
    * [Users](https://buildarr.github.io/plugins/jellyseerr/configuration/settings/users)
    * [Jellyfin](https://buildarr.github.io/plugins/jellyseerr/configuration/settings/jellyfin)
    * Services
        * [Sonarr](https://buildarr.github.io/plugins/jellyseerr/configuration/settings/services/sonarr)
        * [Radarr](https://buildarr.github.io/plugins/jellyseerr/configuration/settings/services/radarr)
    * [Notifications](https://buildarr.github.io/plugins/jellyseerr/configuration/settings/notifications)

## Dumping an existing Jellyseerr instance configuration

Buildarr is capable of dumping a running Jellyseerr instance's configuration.

```bash
$ buildarr jellyseerr dump-config http://localhost:5055 > jellyseerr.yml
Jellyseerr instance API key: <Paste API key here>
```

The dumped YAML object can be placed directly under the `jellyseerr` configuration block, or used as an [instance-specific configuration](https://buildarr.github.io/configuration/#multiple-instances-of-the-same-type).

All possible values are explicitly defined in this dumped configuration.

```yaml
hostname: localhost
port: 5055
protocol: http
api_key: AbCdEfGhIjKlMnOpQrStUvWxYzaBcDeFgHiJkLmNoPqRsTuVwXyZ123456789012345=
image: fallenbagel/jellyseerr
version: 1.4.1
settings:
  general:
    application_title: Jellyseerr
    application_url: null
    enable_proxy_support: false
    enable_csrf_protection: false
    enable_image_caching: false
    display_language: en
    discover_region: ''
    discover_languages:
    - en
    hide_available_media: false
    allow_partial_series_requests: true
  jellyfin:
    server_url: null
    username: null
    password: null
    email_address: null
    external_url: null
    libraries:
    - TV Shows
  users:
    enable_local_signin: true
    enable_new_jellyfin_signin: true
    global_movie_request_limit: 0
    global_movie_request_days: 7
    global_series_request_limit: 0
    global_series_request_days: 7
    default_permissions:
    - request
    - request-4k
  services:
    radarr:
      delete_unmanaged: false
      definitions: {}
    sonarr:
      delete_unmanaged: false
      definitions:
        Sonarr:
          is_default_server: true
          is_4k_server: false
          hostname: localhost
          port: 8989
          use_ssl: false
          url_base: null
          external_url: http://localhost:8989
          enable_scan: false
          enable_automatic_search: true
          instance_name: null
          api_key: 1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c4d
          root_folder: /data/media/tv
          quality_profile: TV Shows
          language_profile: English
          tags: []
          anime_root_folder: null
          anime_quality_profile: null
          anime_language_profile: null
          anime_tags: []
          enable_season_folders: true
  notifications:
    discord:
      enable: false
      notification_types: []
      webhook_url: null
      username: null
      avatar_url: null
      enable_mentions: true
    email:
      enable: false
      require_user_email: false
      sender_name: Jellyseerr
      sender_address: null
      smtp_host: null
      smtp_port: 587
      encryption_method: starttls-prefer
      allow_selfsigned_certificates: false
      smtp_username: null
      smtp_password: null
      pgp_private_key: null
      pgp_password: null
    gotify:
      enable: false
      notification_types: []
      server_url: null
      access_token: null
    lunasea:
      enable: false
      notification_types: []
      webhook_url: null
      profile_name: null
    pushbullet:
      enable: false
      notification_types: []
      access_token: null
      channel_tag: null
    pushover:
      enable: false
      notification_types: []
      api_key: null
      user_key: null
    slack:
      enable: false
      notification_types: []
      webhook_url: null
    telegram:
      enable: false
      notification_types: []
      access_token: null
      username: null
      chat_id: null
      send_silently: false
    webhook:
      enable: false
      notification_types: []
      webhook_url: null
      authorization_header: null
      payload_template: "{\n    \"notification_type\": \"{{notification_type}}\",\n\
        \    \"event\": \"{{event}}\",\n    \"subject\": \"{{subject}}\",\n    \"\
        message\": \"{{message}}\",\n    \"image\": \"{{image}}\",\n    \"{{media}}\"\
        : {\n        \"media_type\": \"{{media_type}}\",\n        \"tmdbId\": \"{{media_tmdbid}}\"\
        ,\n        \"tvdbId\": \"{{media_tvdbid}}\",\n        \"status\": \"{{media_status}}\"\
        ,\n        \"status4k\": \"{{media_status4k}}\"\n    },\n    \"{{request}}\"\
        : {\n        \"request_id\": \"{{request_id}}\",\n        \"requestedBy_email\"\
        : \"{{requestedBy_email}}\",\n        \"requestedBy_username\": \"{{requestedBy_username}}\"\
        ,\n        \"requestedBy_avatar\": \"{{requestedBy_avatar}}\"\n    },\n  \
        \  \"{{issue}}\": {\n        \"issue_id\": \"{{issue_id}}\",\n        \"issue_type\"\
        : \"{{issue_type}}\",\n        \"issue_status\": \"{{issue_status}}\",\n \
        \       \"reportedBy_email\": \"{{reportedBy_email}}\",\n        \"reportedBy_username\"\
        : \"{{reportedBy_username}}\",\n        \"reportedBy_avatar\": \"{{reportedBy_avatar}}\"\
        \n    },\n    \"{{comment}}\": {\n        \"comment_message\": \"{{comment_message}}\"\
        ,\n        \"commentedBy_email\": \"{{commentedBy_email}}\",\n        \"commentedBy_username\"\
        : \"{{commentedBy_username}}\",\n        \"commentedBy_avatar\": \"{{commentedBy_avatar}}\"\
        \n    },\n    \"{{extra}}\": []\n}"
    webpush:
      enable: false
```
