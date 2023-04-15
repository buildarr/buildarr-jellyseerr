# Jellyfin

[Jellyfin](https://jellyfin.org) is an open source self-hosted media server for managing and making your media library available for streaming across your network (or over a VPN) using client apps on your PC, phone or TV.

Jellyseerr links with Jellyfin, allows users to login to Jellyseerr using their Jellyfin credentials, and request media not yet available in Jellyfin for download.

Jellyseerr can also conect to the media server Jellyfin was forked from, [Emby](https://emby.media), using the same `jellyfin` configuration section.

## Initialisation

Before Jellyseerr can be made available to users, the Jellyfin admin user credentials and libraries to scan need to be configured.

When setting up Jellyseerr manually, this is done by navigating to `https://localhost:5055/setup` and following the on-screen instructions.

Buildarr supports initialising Jellyseerr with this Jellyfin configuration automatically.

To initialise the Jellyseerr instance automatically within Buildarr, make sure the below attributes are defined in the Buildarr configuration, and then start Buildarr as normal.

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

Once Jellyseerr is initialised, with the exception of `libraries`, the below attributes cannot be modified (and are no longer managed by Buildarr).

##### ::: buildarr_jellyseerr.config.settings.jellyfin.JellyseerrJellyfinSettings
    options:
      members:
        - server_url
        - username
        - password
        - email_address
        - libraries

## Configuration

After initialising Jellyseerr, the following configuration attributes are available to manage the corresponding settings on the instance.

These attributes can be modified at any time.

##### ::: buildarr_jellyseerr.config.settings.jellyfin.JellyseerrJellyfinSettings
    options:
      members:
        - external_url
        - libraries
