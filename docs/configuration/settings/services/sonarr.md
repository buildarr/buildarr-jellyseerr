# Sonarr

##### ::: buildarr_jellyseerr.config.settings.services.sonarr.SonarrSettings
    options:
      members:
        - delete_unmanaged
        - definitions

## Configuration

The following configuration attributes are available when adding a Sonarr instance to Jellyseerr.

##### ::: buildarr_jellyseerr.config.settings.services.base.ArrBase
    options:
      members:
        - is_default_server
        - is_4k_server

##### ::: buildarr_jellyseerr.config.settings.services.sonarr.Sonarr
    options:
      members:
        - instance_name

##### ::: buildarr_jellyseerr.config.settings.services.base.ArrBase
    options:
      members:
        - hostname

##### ::: buildarr_jellyseerr.config.settings.services.sonarr.Sonarr
    options:
      members:
        - port

##### ::: buildarr_jellyseerr.config.settings.services.base.ArrBase
    options:
      members:
        - use_ssl

##### ::: buildarr_jellyseerr.config.settings.services.sonarr.Sonarr
    options:
      members:
        - api_key

##### ::: buildarr_jellyseerr.config.settings.services.base.ArrBase
    options:
      members:
        - url_base

##### ::: buildarr_jellyseerr.config.settings.services.sonarr.Sonarr
    options:
      members:
        - root_folder
        - quality_profile
        - language_profile
        - tags
        - anime_root_folder
        - anime_quality_profile
        - anime_language_profile
        - anime_tags
        - enable_season_folders

##### ::: buildarr_jellyseerr.config.settings.services.base.ArrBase
    options:
      members:
        - external_url
        - enable_scan
        - enable_automatic_search
