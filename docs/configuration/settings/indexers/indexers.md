# Indexers

##### ::: buildarr_prowlarr.config.settings.indexers.indexers.IndexersSettings
    options:
      members:
        - delete_unmanaged
        - definitions
      show_root_heading: false
      show_source: false

## Adding indexers to Buildarr

Due to the sheer number of possible indexer types in Prowlarr (583 at the time of writing),
indexers are expressed differently in Buildarr compared to other resource types.

Indexer configurations are partly composed of individually defined configuration attributes
common to all indexer types, and partly composed of dynamically parsed fields unique to
each indexer type.

The easiest way to add an indexer to the Buildarr configuration file is to
configure it manually in Prowlarr first, and then export the configuration using
[`buildarr prowlarr dump-config`](
../../../index.md#dumping-an-existing-prowlarr-instance-configuration
).

The resulting indexer configuration will have all possible attributes defined on it,
as shown below. Most of these are not required, so it is a good idea to only use
configuration attributes that are actually changed from default.

```yaml
prowlarr:
  settings:
    indexers:
      indexers:
        definitions:
        1337x:
          enable: false
          fields:
            baseUrl: null
            definitionFile: 1337x
            downloadlink: iTorrents.org
            downloadlink2: magnet
            sort: created
            torrentBaseSettings.seedRatio: null
            torrentBaseSettings.seedTime: null
            type: desc
          grab_limit: null
          indexer_priority: 1
          query_limit: null
          redirect: false
          secret_fields: {}
          sync_profile: Standard
          tags: []
          type: 1337x
```

## Indexer configuration format

##### ::: buildarr_prowlarr.config.settings.indexers.indexers.Indexer
    options:
      members:
        - type
        - enable
        - sync_profile
        - redirect
        - priority
        - query_limit
        - grab_limit
        - tags
        - fields
        - secret_fields
      show_root_heading: false
      show_source: false
