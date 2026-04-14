# RELEASE_GUIDE.md

## Purpose

This is the release-candidate checklist for **OpenShot BnR 1.0**. It exists to keep the repo from feeling finished just because the main script ran once.

## Release standard

A public release should have:

- a clear README
- a root license file
- contribution guidance
- a code of conduct
- a security policy
- a changelog entry
- working install and usage instructions
- a tested launcher path
- a tested portable or frozen handoff path
- a help page with current screenshots, commands, and links

## Pre-release checklist

### Repo hygiene

- [ ] README.md and README.txt match the current version
- [ ] INSTALL.md matches the current launcher and helper files
- [ ] MANUAL_INSTALL.md still points at official vendor pages
- [ ] LOG_GUIDE.md and TROUBLESHOOTING.md still match current behavior
- [ ] CHANGELOG.md includes the release notes
- [ ] LICENSE.txt is present in the repo root
- [ ] CONTRIBUTING.md, SECURITY.md, and CODE_OF_CONDUCT.md are present and linked
- [ ] no `__pycache__`, temp files, logs, or accidental binaries are being shipped

### Script sanity

- [ ] `OpenShot_BnR_v1_0.py --usage` works
- [ ] `--about` works
- [ ] `--version` works
- [ ] `--license` works
- [ ] `--readme` works
- [ ] `--debug` works
- [ ] script passes syntax compile

### Build sanity

- [ ] prerequisites stage passes
- [ ] dependency resolution passes
- [ ] libopenshot-audio builds cleanly
- [ ] libopenshot builds cleanly
- [ ] source-build binding verification passes
- [ ] launcher files are generated

### Runtime sanity

- [ ] `Launch-OpenShot-Qt.cmd` starts OpenShot
- [ ] `Launch-OpenShot-Qt.py` starts OpenShot
- [ ] the session log shows a real OpenShot run, not just import smoke
- [ ] shutdown is clean
- [ ] the log does not show a new missing-DLL or missing-module regression

### Distribution sanity

- [ ] portable helper output exists and is structured correctly
- [ ] frozen helper output exists or is explicitly documented as not yet final
- [ ] a second machine test is done before calling it release-ready

## Suggested release notes structure

Use this simple shape for each release entry:

1. what changed
2. what was fixed
3. what still is not finished
4. what users should test first

## Recommended ship rule

Do not say **perfect**. Say what passed, what was tested, and what still needs verification.
