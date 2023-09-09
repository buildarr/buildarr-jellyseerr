# Release Notes (Buildarr Jellyseerr Plugin)

## [v0.2.0](https://github.com/buildarr/buildarr-jellyseerr/releases/tag/v0.2.0) - 2023-09-09

This release updates the Jellyseerr plugin so that it is compatible with [Buildarr v0.6.0](https://buildarr.github.io/release-notes/#v060-2023-09-02).

This version is backwards compatible with all versions of Buildarr supported by v0.1.0 of the plugin.

An optional extra dependency has been added to the plugin for the new [Radarr plugin for Buildarr](https://buildarr.github.io/plugins/radarr), for convenient installation when using Jellyseerr.

Other changes:

* Fix the plugin's internal name for `announced` in the minimum availability field. Shouldn't have caused any problems when using the plugin previously, but fixed anyway.

### Changed

* Update package metadata and dependencies ([#5](https://github.com/buildarr/buildarr-prowlarr/pull/5))
* Fix internal name for 'announced' minimum availability ([#6](https://github.com/buildarr/buildarr-prowlarr/pull/6))


## [v0.1.0](https://github.com/buildarr/buildarr-jellyseerr/releases/tag/v0.1.0) - 2023-04-15

First release of the Jellyseerr plugin for Buildarr.
