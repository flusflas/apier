# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
