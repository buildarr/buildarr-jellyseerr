# Indexer Proxies

##### ::: buildarr_prowlarr.config.settings.indexers.proxies.ProxiesSettings
    options:
      members:
        - delete_unmanaged
        - definitions
      show_root_heading: false
      show_source: false

## Configuring indexer proxies

##### ::: buildarr_prowlarr.config.settings.indexers.proxies.Proxy
    options:
      members:
        - tags
      show_root_heading: false
      show_source: false

## FlareSolverr

##### ::: buildarr_prowlarr.config.settings.indexers.proxies.FlaresolverrProxy
    options:
      members:
        - type
        - host_url
        - request_timeout
      show_root_heading: false
      show_source: false

## HTTP proxy

##### ::: buildarr_prowlarr.config.settings.indexers.proxies.HttpProxy
    options:
      members:
        - type
        - hostname
        - port
        - username
        - password
      show_root_heading: false
      show_source: false

## SOCKS4 proxy

##### ::: buildarr_prowlarr.config.settings.indexers.proxies.Socks4Proxy
    options:
      members:
        - type
        - hostname
        - port
        - username
        - password
      show_root_heading: false
      show_source: false

## SOCKS5 proxy

##### ::: buildarr_prowlarr.config.settings.indexers.proxies.Socks5Proxy
    options:
      members:
        - type
        - hostname
        - port
        - username
        - password
      show_root_heading: false
      show_source: false
