# Download Clients

##### ::: buildarr_prowlarr.config.settings.download_clients.ProwlarrDownloadClientsSettings
    options:
      members:
        - delete_unmanaged
        - definitions
      show_root_heading: false
      show_source: false

## Configuring download clients

##### ::: buildarr_prowlarr.config.settings.download_clients.base.DownloadClient
    options:
      members:
        - enable
        - priority
        - tags
      show_root_heading: false
      show_source: false

## Usenet download clients

These download clients retrieve media using the [Usenet](https://en.wikipedia.org/wiki/Usenet) discussion and content delivery system.

## Download Station (Usenet)

##### ::: buildarr_prowlarr.config.settings.download_clients.usenet.DownloadstationUsenetDownloadClient
    options:
      members:
        - type
        - host
        - port
        - use_ssl
        - username
        - password
        - category
        - directory
      show_root_heading: false
      show_source: false

## NZBGet

##### ::: buildarr_prowlarr.config.settings.download_clients.usenet.NzbgetDownloadClient
    options:
      members:
        - type
        - host
        - port
        - use_ssl
        - url_base
        - username
        - password
        - category
        - client_priority
        - add_paused
        - category_mappings
      show_root_heading: false
      show_source: false

## NZBVortex

##### ::: buildarr_prowlarr.config.settings.download_clients.usenet.NzbvortexDownloadClient
    options:
      members:
        - type
        - host
        - port
        - use_ssl
        - url_base
        - api_key
        - category
        - client_priority
        - category_mappings
      show_root_heading: false
      show_source: false

## Pneumatic

##### ::: buildarr_prowlarr.config.settings.download_clients.usenet.PneumaticDownloadClient
    options:
      members:
        - type
        - nzb_folder
      show_root_heading: false
      show_source: false

## SABnzbd

##### ::: buildarr_prowlarr.config.settings.download_clients.usenet.SabnzbdDownloadClient
    options:
      members:
        - type
        - host
        - port
        - use_ssl
        - url_base
        - api_key
        - category
        - client_priority
        - category_mappings
      show_root_heading: false
      show_source: false

## Usenet Blackhole

##### ::: buildarr_prowlarr.config.settings.download_clients.usenet.UsenetBlackholeDownloadClient
    options:
      members:
        - type
        - nzb_folder
      show_root_heading: false
      show_source: false

## Torrent download clients

These download clients use the [BitTorrent](https://en.wikipedia.org/wiki/BitTorrent)
peer-to-peer file sharing protocol to retrieve media files.

## Aria2

##### ::: buildarr_prowlarr.config.settings.download_clients.torrent.Aria2DownloadClient
    options:
      members:
        - type
        - host
        - port
        - use_ssl
        - rpc_path
        - secret_token
      show_root_heading: false
      show_source: false

## Deluge

##### ::: buildarr_prowlarr.config.settings.download_clients.torrent.DelugeDownloadClient
    options:
      members:
        - type
        - host
        - port
        - use_ssl
        - url_base
        - password
        - category
        - client_priority
        - category_mappings
      show_root_heading: false
      show_source: false

## Download Station (Torrent)

##### ::: buildarr_prowlarr.config.settings.download_clients.torrent.DownloadstationTorrentDownloadClient
    options:
      members:
        - type
        - host
        - port
        - use_ssl
        - username
        - password
        - category
        - directory
      show_root_heading: false
      show_source: false

## Flood

##### ::: buildarr_prowlarr.config.settings.download_clients.torrent.FloodDownloadClient
    options:
      members:
        - type
        - host
        - port
        - use_ssl
        - url_base
        - username
        - password
        - destination
        - flood_tags
        - additional_tags
        - add_paused
        - category_mappings
      show_root_heading: false
      show_source: false

## Freebox

##### ::: buildarr_prowlarr.config.settings.download_clients.torrent.FreeboxDownloadClient
    options:
      members:
        - type
        - host
        - port
        - use_ssl
        - api_url
        - app_id
        - app_token
        - destination_directory
        - category
        - priority
        - add_paused
        - category_mappings
      show_root_heading: false
      show_source: false

## Hadouken

##### ::: buildarr_prowlarr.config.settings.download_clients.torrent.HadoukenDownloadClient
    options:
      members:
        - type
        - host
        - port
        - use_ssl
        - url_base
        - username
        - password
        - category
        - category_mappings
      show_root_heading: false
      show_source: false

## qBittorrent

##### ::: buildarr_prowlarr.config.settings.download_clients.torrent.QbittorrentDownloadClient
    options:
      members:
        - type
        - host
        - port
        - use_ssl
        - url_base
        - username
        - password
        - category
        - client_priority
        - initial_state
        - sequential_order
        - first_and_last_first
        - category_mappings
      show_root_heading: false
      show_source: false

## RTorrent (ruTorrent)

##### ::: buildarr_prowlarr.config.settings.download_clients.torrent.RtorrentDownloadClient
    options:
      members:
        - type
        - host
        - port
        - use_ssl
        - url_base
        - username
        - password
        - category
        - client_priority
        - add_stopped
        - category_mappings
      show_root_heading: false
      show_source: false

## Torrent Blackhole

##### ::: buildarr_prowlarr.config.settings.download_clients.torrent.TorrentBlackholeDownloadClient
    options:
      members:
        - type
        - torrent_folder
        - save_magnet_files
        - magnet_file_extension
        - read_only
      show_root_heading: false
      show_source: false

## Transmission/Vuze

Transmission and Vuze use the same configuration parameters.

To use Transmission, set the `type` attribute in the download client to `transmission`.

To use Vuze, set the `type` attribute in the download client to `vuze`.

##### ::: buildarr_prowlarr.config.settings.download_clients.torrent.TransmissionDownloadClientBase
    options:
      members:
        - host
        - port
        - use_ssl
        - url_base
        - username
        - password
        - category
        - directory
        - client_priority
        - add_paused
      show_root_heading: false
      show_source: false

## uTorrent

##### ::: buildarr_prowlarr.config.settings.download_clients.torrent.UtorrentDownloadClient
    options:
      members:
        - type
        - host
        - port
        - use_ssl
        - url_base
        - username
        - password
        - category
        - client_priority
        - initial_state
        - category_mappings
      show_root_heading: false
      show_source: false
