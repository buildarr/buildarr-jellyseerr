# Release Notes (Buildarr Jellyseerr Plugin)

## [v0.3.2](https://github.com/buildarr/buildarr-jellyseerr/releases/tag/v0.3.2) - 2024-03-02

This release addresses the following issues:

* Support defining a URL base for the Jellyseerr instance in the Buildarr configuration, using the `url_base` host configuration attribute.
    * This allows Jellyseerr instances with APIs available under a custom path (e.g. `http://localhost:5055/jellyseerr`) to be managed by Buildarr.

The following issues have also been fixed:

* Return a more helpful error message when the API key is not specified when dumping Jellyseerr instance configurations.
* Improve error handling when Buildarr was unable to parse a JSON response from the Jellyseerr API.
* Use the global state attribute for API request timeouts available in newer versions of Buildarr, instead of directly reading it from the Buildarr configuration (and using a hard-coded default if not found).

### Changed

* Update Poetry and lock file ([#24](https://github.com/buildarr/buildarr-jellyseerr/pull/24))
* Make the Sonarr instance `animeAnimeDirectory` API field optional ([#26](https://github.com/buildarr/buildarr-jellyseerr/pull/26))


## [v0.3.1](https://github.com/buildarr/buildarr-jellyseerr/releases/tag/v0.3.1) - 2023-12-02

This release adds the following new features:

* Support defining a URL base for the Jellyseerr instance in the Buildarr configuration, using the `url_base` host configuration attribute.
    * This allows Jellyseerr instances with APIs available under a custom path (e.g. `http://localhost:5055/jellyseerr`) to be managed by Buildarr.

The following issues have also been fixed:

* Return a more helpful error message when the API key is not specified when dumping Jellyseerr instance configurations.
* Improve error handling when Buildarr was unable to parse a JSON response from the Jellyseerr API.
* Use the global state attribute for API request timeouts available in newer versions of Buildarr, instead of directly reading it from the Buildarr configuration (and using a hard-coded default if not found).

### Changed

* Add Jellyseerr instance URL base support ([#20](https://github.com/buildarr/buildarr-jellyseerr/pull/20))


## [v0.3.0](https://github.com/buildarr/buildarr-jellyseerr/releases/tag/v0.3.0) - 2023-11-12

This updates the Jellyseerr plugin so that it is compatible with [Buildarr v0.7.0](https://buildarr.github.io/release-notes/#v070-2023-11-12).

### Changed

* Add Buildarr v0.7.0 support ([#14](https://github.com/buildarr/buildarr-jellyseerr/pull/14))


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
