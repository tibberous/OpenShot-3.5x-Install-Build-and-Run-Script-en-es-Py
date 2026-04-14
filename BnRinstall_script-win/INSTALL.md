# INSTALL.md

## Purpose

This guide is for getting **OpenShot BnR 1.0** running on Windows, then using it to install, build, verify, and launch OpenShot 3.5.x.

## Before you start

You should have:

- Windows 10 or later
- internet access for package resolution and repository pulls
- a Python 3 interpreter available through `py -3` or `python`
- permission to elevate when the script requests admin access

## Fast path

```bash
py -3 OpenShot_BnR_v1_0.py
```

The script will:
1. check Windows support and elevation
2. find or restore WinGet, Git, and MSYS2
3. refresh MSYS2 and resolve dependencies against the live UCRT64 package list
4. clone or update the OpenShot repositories
5. build `libopenshot-audio`
6. build `libopenshot`
7. verify Python bindings in installed and source-build modes
8. generate launcher and distribution helper files


## Information-only commands

```bash
py -3 OpenShot_BnR_v1_0.py --usage
py -3 OpenShot_BnR_v1_0.py --help
py -3 OpenShot_BnR_v1_0.py man
py -3 OpenShot_BnR_v1_0.py --about
py -3 OpenShot_BnR_v1_0.py --version
py -3 OpenShot_BnR_v1_0.py --docs
py -3 OpenShot_BnR_v1_0.py --install
py -3 OpenShot_BnR_v1_0.py --manual-install
py -3 OpenShot_BnR_v1_0.py --log-guide
py -3 OpenShot_BnR_v1_0.py --troubleshoot
py -3 OpenShot_BnR_v1_0.py --license
py -3 OpenShot_BnR_v1_0.py --debug
```

Slash-style and short aliases also work, including `/usage`, `/help`, `/u`, `/U`, `/v`, `/docs`, and `/debug`.

## What gets created

Common outputs include:

- `C:\OpenShotBuild\Launch-OpenShot-Qt.cmd`
- `C:\OpenShotBuild\Launch-OpenShot-Qt.py`
- portable/frozen build helper scripts
- `openshot-installer.log`
- `openshot-installer-state.json`
- `openshot-installer-relay.log`

## Reading the result

### Good result
You want to see:
- stages marked `PASS`
- bindings import success
- launcher files generated
- a real OpenShot session log when launched

### Not automatically fatal
These are often informational, not catastrophic:
- installed binding misses while source-build mode passes
- optional tooling not required for launch
- local service checks that are unrelated to OpenShot core startup

## Troubleshooting basics

### `ModuleNotFoundError: No module named 'openshot'`
The runtime bootstrap path is wrong or incomplete. Check the generated launcher/bootstrap files and verify the bindings path is being injected.

### `MISS` in installed Python binding checks
This may simply mean installed mode was not used. Source-build mode can still be valid.

### stage fails after dependency resolution
Check `openshot-installer.log` and the state file to see exactly which capability or command failed.

### launcher opens and closes quickly
Look at the console output and the generated log file. Most launch issues are now path/bootstrap issues, not native compile issues.

## Recommended release workflow

1. Run `--debug`
2. Run the full build
3. Launch OpenShot
4. Confirm a clean session log
5. Test the portable/frozen helpers
6. Update `CHANGELOG.md`
7. Ship only after the launcher path has been validated on a second machine


## Manual install and package reference

If automatic bootstrap is blocked by permissions or Store policy, use the official package pages in [MANUAL_INSTALL.md](MANUAL_INSTALL.md). That file explains what each package does and gives the official URL and attribution.

## Troubleshooting and log reading

- [LOG_GUIDE.md](LOG_GUIDE.md) walks through a successful runtime log and explains what each line means.
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) covers permissions, manual install fallback, missing tools, and bad-launch scenarios.


See also: RELEASE_GUIDE.md for the public-release checklist and final QA pass.
