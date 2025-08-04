# Changelog

All notable changes to this project will be documented in this file.

> ⚠️ **Warning: Pre-1.0.0 Release**
> 
> This project is in early development. Breaking changes may occur in any minor
> or patch release until version 1.0.0. Follow changelogs closely and pin
> versions if needed.

## [0.4.0](https://github.com/flusflas/apier/tree/v0.4.0) (2025-08-04)

This release adds `$eval` support for dynamic expressions, allowing complex
evaluations and manipulations of request and response data, and unlocking
advanced pagination strategies.

### 🧨 Breaking Changes

- Renamed `reuse-previous-request` to `reuse_previous_request` in pagination
  configuration for naming consistency.
- Enforced `#` prefix for dot-separated paths in dynamic expressions (e.g.,
  `#users.0.name` instead of `users.0.name`).

### Added

- Simple expression evaluation with `ast` module.
- Support for nullish coalescing operator (`??`) in dynamic expressions.

### Fixed

- Evaluation of `results` parameter in pagination configuration.

## [0.3.0](https://github.com/flusflas/apier/tree/v0.3.0) (2025-07-31)

This release adds support for request payloads with
`application/x-www-form-urlencoded` content type, and improves handling of
structured content types such as `application/json-patch+json`.

### Added

- Handle request content types with structured syntax suffixes.
- Support for `application/x-www-form-urlencoded` request payloads.

## [0.2.0](https://github.com/flusflas/apier/tree/v0.2.0) (2025-07-24)

This release adds support for multipart requests, binary responses, improved
request handling, and includes various fixes and minor enhancements.

### Added

- Enforce body compatibility with request content types.
- Response stream extension.
- Support for binary responses.
- Support for streaming multipart requests.
- `FilePayload` model for file uploads.
- Format generated code with black.
- Support for `multipart/form-data` in file uploads.
- XML request and enhanced Content-Type handling.
- Enhanced Content-Type validation and request preparation.

## [0.1.0](https://github.com/flusflas/apier/tree/v0.1.0) (2025-07-18)

### Added

- 🚀 Initial release.
