# Release Notes

## [v0.1.1](https://github.com/buildarr/buildarr-prowlarr/releases/tag/v0.1.1) - 2023-04-08

This is a bugfix release to resolve problems with the first release, particularly when using Prowlarr to manage the indexers of Sonarr instances.

* Add an error message for when an invalid indexer type is provided
* Add mutual exclusion handling for the `category` and `directory` attributes in Transmission/Vuze download clients
* Fix updating app sync profiles
* Fix updating indexer proxies, download clients, application links and app sync profiles when not all type-specific resource values are defined in the configuration
* Require at least [version 0.4.1](https://buildarr.github.io/plugins/sonarr/release-notes/#v041-2023-04-08) of the Sonarr plugin for Buildarr, to fix bugs with instance linking

### Changed

* Fix bugs from integration tests ([#4](https://github.com/buildarr/buildarr-prowlarr/pull/4))


## [v0.1.0](https://github.com/buildarr/buildarr-prowlarr/releases/tag/v0.1.0) - 2023-04-08

First release of the Prowlarr plugin for Buildarr.
