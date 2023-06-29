# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.0] - 2023-06-29
### Changed
- Using Draft7 instead of Draft4
- CI updates

## [0.8.0] - 2021-04-28
### Changed
- Better handling of json schema loading and error reporting
- Migrate changelog to Keep a Changelog style

## [0.7.1] - 2018-08-16
### Fixed
- ipv4netmask fix

## [0.7] - 2018-08-14
### Changed
- CI python3 integration
- make foris-schema python3 compatible

## [0.6] - 2018-06-19

- faster validations (splitted into two - basic an per module)
- schema attribute repalced (base_schema, error_schema, get_module_schema())
- validate_verbose removed (validate() should be verbose enough)
- allow definition overrides in modules (it still fails when override appears in global definitions)
- different error messages `errors` object is place directly in message root instead of inside `data` element
- is_valid function added (check message validity but doesn't raise an exception)

## [0.5] - 2018-05-24
### Changed
- test updates
- mac format checker added
- ipv4prefix, ipv4netmask, ipv6prefix format checkers added

## [0.4] - 2018-02-08
### Added
- integrate FormatChecker

## [0.3] - 2017-09-25
### Added
- json definitions can be read from another directory list

## [0.2] - 2017-08-28
### Added
- json definitions added
- validate_verbose function
- schema validation improvements


## [0.1] - 2017-08-01
### Added
- initial version
