# Changelog

All notable changes to **OpenShot BnR** will be documented in this file.

## [1.0] - 2026-04-13

### Added
- Windows-first install, build, run, and distro-prep workflow for OpenShot 3.5.x.
- Honest stage-by-stage verification for prerequisites, dependencies, repositories, native builds, runtime bootstrap, and launch helpers.
- CLI info switches for usage, about, version, readme, license, and debug output.
- Generated launch helpers for source-build, portable, and frozen/distribution prep workflows.
- Repo documentation pack including README, INSTALL guide, help wiki, and supporting links.
- Prism.js-powered help examples with syntax highlighting, line numbers, copy, and print actions.

### Changed
- Verification logic now distinguishes between installed-mode misses and source-build success.
- Launcher bootstrap now mirrors the verified runtime path instead of relying on brittle shell assumptions.
- Help and documentation were rewritten to read like a real release candidate rather than an internal scratchpad.

### Fixed
- False-negative `MISS` / `FAIL` states caused by import-path and runtime bootstrap mismatches.
- Runtime crash path where `launch.py` could fall through to `NoneType.show_errors` after startup import failure.

[1.0]: https://github.com/tibberous/OpenShot-3.5x-Install-Build-and-Run-Script-en-es-Py-add
