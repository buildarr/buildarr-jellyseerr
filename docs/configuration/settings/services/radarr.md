# Radarr

##### ::: buildarr_jellyseerr.config.settings.services.radarr.RadarrSettings
    options:
      members:
        - delete_unmanaged
        - definitions

## Configuration

The following configuration attributes are available when adding a Radarr instance to Jellyseerr.

##### ::: buildarr_jellyseerr.config.settings.services.base.ArrBase
    options:
      members:
        - is_default_server
        - is_4k_server

##### ::: buildarr_jellyseerr.config.settings.services.radarr.Radarr
    options:
      members:
        - instance_name

##### ::: buildarr_jellyseerr.config.settings.services.base.ArrBase
    options:
      members:
        - hostname

##### ::: buildarr_jellyseerr.config.settings.services.radarr.Radarr
    options:
      members:
        - port

##### ::: buildarr_jellyseerr.config.settings.services.base.ArrBase
    options:
      members:
        - use_ssl

##### ::: buildarr_jellyseerr.config.settings.services.radarr.Radarr
    options:
      members:
        - api_key

##### ::: buildarr_jellyseerr.config.settings.services.base.ArrBase
    options:
      members:
        - url_base

##### ::: buildarr_jellyseerr.config.settings.services.radarr.Radarr
    options:
      members:
        - root_folder
        - quality_profile
        - minimum_availability
        - tags

##### ::: buildarr_jellyseerr.config.settings.services.base.ArrBase
    options:
      members:
        - external_url
        - enable_scan
        - enable_automatic_search
